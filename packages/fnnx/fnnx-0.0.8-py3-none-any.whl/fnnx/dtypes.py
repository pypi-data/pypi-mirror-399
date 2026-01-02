from fnnx.validators.jsonschema import validate_jsonschema
from copy import copy, deepcopy


class FlatList:
    def __init__(self, data: list):
        if not isinstance(data, list):
            raise ValueError("FlatList only accepts lists")
        self.data = copy(data)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def __repr__(self):
        return f"FlatList({self.data})"

    def append(self, value):
        self.data.append(value)


class DtypesManager:
    def __init__(self, external_dtypes: dict, builtins: dict):
        self.dtypes = deepcopy(external_dtypes)
        self.dtypes.update(deepcopy(builtins))
        for dtype in self.dtypes:
            if "[" in dtype:
                raise ValueError(f"Invalid dtype name: {dtype}")
        for reserved_type in [
            "string",
            "integer",
            "float",
            "Array",
            "NDContainer",
            "FlatList",
        ]:
            if reserved_type in self.dtypes:
                raise ValueError(f"Invalid dtype name: {reserved_type}")

    def get_dtype(self, dtype_name: str):
        if dtype_name not in self.dtypes:
            raise ValueError(f"Unknown dtype: {dtype_name}")
        return self.dtypes[dtype_name]

    def _validate_dtype(self, dtype_name: str, data: dict):
        schema = self.get_dtype(dtype_name)
        validate_jsonschema(data, schema)

    def validate_dtype(self, dtype_name: str, data):
        if isinstance(data, list):
            for d in data:
                self.validate_dtype(dtype_name, d)
        elif isinstance(data, FlatList):
            self.validate_dtype(dtype_name, data.data)
        elif isinstance(data, dict):
            self._validate_dtype(dtype_name, data)
        elif isinstance(data, str):
            if dtype_name != "string":
                raise TypeError(
                    f"Invalid data type, expected `string`, got `{dtype_name}`"
                )
        elif isinstance(data, int):
            if dtype_name != "integer":
                raise TypeError(
                    f"Invalid data type, expected `integer`, got `{dtype_name}`"
                )
        elif isinstance(data, float):
            if dtype_name != "float":
                raise TypeError(
                    f"Invalid data type, expected `float`, got `{dtype_name}`"
                )
        else:
            raise TypeError(f"Invalid data type: {type(data)}")


class NDContainer:
    def __init__(self, data, dtype, dtypes_manager: DtypesManager):
        if dtype.startswith("Array["):
            raise ValueError("NDContainer does not support Array dtype")
        elif dtype.startswith("NDContainer["):
            dtype = dtype[12:-1]

        self.data = deepcopy(data if isinstance(data, list) else [data])

        if dtypes_manager:
            dtypes_manager.validate_dtype(dtype, self.data)
        self.dtypes_manager = dtypes_manager
        self._dtype = dtype
        if "FlatList[" in self._dtype:
            self.data = self._inner_to_flatlist(self.data)
        self.shape = tuple(self._compute_shape(self.data))

    def _inner_to_flatlist(self, nested_list, root=True):
        if root:
            # check base case
            if all(not isinstance(item, (list, FlatList)) for item in nested_list):
                return [FlatList(nested_list)]

        for i, item in enumerate(nested_list):
            if isinstance(item, list):
                if all(not isinstance(sub_item, (list, FlatList)) for sub_item in item):
                    nested_list[i] = FlatList(item)
                else:
                    self._inner_to_flatlist(item, root=False)
        return nested_list

    def _compute_shape(self, data):
        if not isinstance(data, list) or not data:
            return []
        sub_shape = self._compute_shape(data[0])
        return [len(data)] + sub_shape

    def __getitem__(self, index):
        if isinstance(index, tuple):
            result = self.data
            for idx in index:
                result = result[idx]
            return result
        return self.data[index]

    def reshape(self, *new_shape):
        if isinstance(new_shape[0], tuple) or isinstance(new_shape[0], list):
            new_shape = new_shape[0]
        # Check if the total number of elements matches
        if self._product(new_shape) != self._product(self.shape):
            raise ValueError(
                "Cannot reshape array of size {} into shape {}".format(
                    self._product(self.shape), new_shape
                )
            )
        flat_list = self.flatten(self.data)
        if self._product(new_shape) != self._product(self.shape):
            raise ValueError(
                "Cannot reshape array of size {} into shape {}".format(
                    self._product(self.shape), new_shape
                )
            )
        reshaped = self._reshape_helper(flat_list, list(new_shape))
        return NDContainer(
            data=reshaped, dtype=self.dtype, dtypes_manager=self.dtypes_manager
        )

    def flatten(self, data: list | None = None):
        return NDContainer(
            data=self._flatten(data or self.data),
            dtype=self.dtype,
            dtypes_manager=self.dtypes_manager,
        )

    def _flatten(self, data) -> list:
        result = []
        for item in data:
            if isinstance(item, list):
                result.extend(self._flatten(item))
            else:
                result.append(item)
        return result

    def _reshape_helper(self, flat_list, shape):
        if len(shape) == 1:
            return flat_list[: shape[0]]
        step = self._product(shape[1:])
        return [
            self._reshape_helper(flat_list[i * step : (i + 1) * step], shape[1:])
            for i in range(shape[0])
        ]

    def _product(self, shape):
        product = 1
        for dim in shape:
            product *= dim
        return product

    @property
    def dtype(self):
        return self._dtype

    @dtype.setter
    def dtype(self, value):
        raise AttributeError("Cannot modify immutable attribute dtype")

    def __repr__(self) -> str:
        return f"NDContainer(shape={self.shape}, dtype={self._dtype}, data={self.data})"


BUILTINS = {}
