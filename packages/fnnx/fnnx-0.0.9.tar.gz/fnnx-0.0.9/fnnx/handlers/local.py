try:
    import numpy as np  # type: ignore
except ImportError:
    np = None
from os.path import join as pjoin
from shutil import rmtree
import atexit
import json
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from typing import Type
from fnnx.device import DeviceMap
from fnnx.dtypes import DtypesManager, BUILTINS, NDContainer
from fnnx.variants.pipeline import Pipeline
from fnnx.handlers._base import BaseHandler, BaseHandlerConfig
from fnnx.handlers._common import unpack_model
from fnnx.registry import Registry
from fnnx.variants.pyfunc import PyFuncVariant
from fnnx.validators.model_schema import (
    validate_manifest,
    validate_op_instances,
    validate_variant,
)
from fnnx.ops._base import BaseOp
from fnnx.variants._base import BaseVariant


@dataclass
class LocalHandlerConfig(BaseHandlerConfig):
    n_workers: int = 1
    n_workers_node: int = 1
    auto_cleanup: bool = True
    extra_ops: dict[str, Type[BaseOp]] | None = None


class LocalHandler(BaseHandler):
    def __init__(
        self,
        model_path: str,
        device_map: DeviceMap,
        handler_config: LocalHandlerConfig | None = None,
        **kwargs,
    ):
        if handler_config is None:
            handler_config = LocalHandlerConfig()

        if not isinstance(device_map, DeviceMap):
            raise ValueError("device_map must be an instance of DeviceMap")

        model_path, cleanup = unpack_model(model_path)

        self.model_path = model_path
        self.cleanup = handler_config.auto_cleanup and cleanup

        # should this be done on exit or on delete?
        if self.cleanup:
            # passing model_path and not self.model_path to avoid reference on self
            atexit.register(lambda: _cleanup(model_path))

        with open(pjoin(self.model_path, "manifest.json"), "r") as f:
            self.manifest = json.load(f)
            validate_manifest(self.manifest)

            self.input_specs = {spec["name"]: spec for spec in self.manifest["inputs"]}
            self.output_specs = {
                spec["name"]: spec for spec in self.manifest["outputs"]
            }

        with open(pjoin(self.model_path, "ops.json"), "r") as f:
            self.ops = json.load(f)
            validate_op_instances(self.ops)

        with open(pjoin(self.model_path, "variant_config.json"), "r") as f:
            self.variant_config = json.load(f)
            validate_variant(self.manifest["variant"], self.variant_config)

        with open(pjoin(self.model_path, "dtypes.json"), "r") as f:
            external_dtypes = json.load(f)
            self.dtypes_manager = DtypesManager(external_dtypes, BUILTINS)

        self.variant = self.manifest.get("variant")

        registry = Registry()
        registry.register_default_ops()
        if handler_config.extra_ops:
            for op_name, op in handler_config.extra_ops.items():
                registry.register_op(op, op_name)

        if self.variant == "pipeline":
            vcls = Pipeline
        elif self.variant == "pyfunc":
            vcls = PyFuncVariant
        else:
            raise ValueError(f"Unknown variant: {self.variant}")

        self.executor = ThreadPoolExecutor(max_workers=handler_config.n_workers)
        self.op_executor = ThreadPoolExecutor(max_workers=handler_config.n_workers_node)
        self.vrt: BaseVariant = vcls(
            self.model_path,
            self.ops,
            self.variant_config,
            registry=registry,
            device_map=device_map,
            dtypes_manager=self.dtypes_manager,
            executor=self.executor,
            op_executor=self.op_executor,
        ).warmup()

    def _as_np(self, data, spec):
        if np is None:
            raise RuntimeError("You must have numpy installed to use Array dtype")
        dtype = spec["dtype"][6:-1]
        if dtype == "string":
            return np.asarray(data).astype(np.str_)
        return np.asarray(data).astype(dtype)

    def _prepare_inputs(self, inputs):
        prepared_inputs = {}
        for name, input in inputs.items():
            spec = self.input_specs[name]
            if spec["content_type"] == "NDJSON":
                if "NDContainer[" in spec["dtype"]:
                    if not isinstance(input, NDContainer):
                        prepared_inputs[name] = NDContainer(
                            input,
                            dtype=spec["dtype"],
                            dtypes_manager=self.dtypes_manager,
                        )
                    else:
                        prepared_inputs[name] = input
                elif "Array[" in spec["dtype"]:
                    prepared_inputs[name] = self._as_np(input, spec)
                else:
                    raise ValueError(f"Unknown dtype {spec['dtype']}")
            elif spec["content_type"] == "JSON" and self.variant != "pipeline":
                if "Array[" in spec["dtype"]:
                    prepared_inputs[name] = self._as_np(input, spec)
                else:
                    dtype = spec["dtype"]
                    self.dtypes_manager.validate_dtype(dtype, input)
                    prepared_inputs[name] = input
            else:
                raise ValueError(f"Unknown input type {spec['content_type']}")
        return prepared_inputs

    def _prepare_outputs(self, outputs: dict) -> dict:
        return {k: outputs[k] for k in self.output_specs.keys()}

    def compute(self, inputs: dict, dynamic_attributes: dict) -> dict:
        res = self.vrt.compute(
            self._prepare_inputs(inputs),
            dynamic_attributes=dynamic_attributes,
        )
        return self._prepare_outputs(res)

    async def compute_async(self, inputs: dict, dynamic_attributes: dict) -> dict:
        res = await self.vrt.compute_async(
            self._prepare_inputs(inputs),
            dynamic_attributes=dynamic_attributes,
        )
        return self._prepare_outputs(res)

    def __del__(self):
        try:
            self.executor.shutdown()
            self.op_executor.shutdown()
        except Exception:
            pass


def _cleanup(model_path):
    # print("Cleaning up temporary model files at", model_path)
    rmtree(model_path)
