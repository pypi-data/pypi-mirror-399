from typing import cast

from pyarrow import DataType, Table, ListType, StructType
from pyarrow.types import (is_int8, is_int16, is_int32, is_int64,
                           is_float32, is_float64,
                           is_string, is_boolean, is_timestamp,
                           is_date32, is_list, is_struct,
                           )


class ToAvro:

    def __init__(self, table: Table):
        self.table = table

    @staticmethod
    def type(arrow_type: DataType):
        if is_int8(arrow_type) or is_int16(arrow_type) or is_int32(arrow_type):
            return "int"
        elif is_int64(arrow_type):
            return "long"
        elif is_float32(arrow_type):
            return "float"
        elif is_float64(arrow_type):
            return "double"
        elif is_string(arrow_type):
            return "string"
        elif is_boolean(arrow_type):
            return "boolean"
        elif is_timestamp(arrow_type):
            return {"type": "long", "logicalType": "timestamp-millis"}
        elif is_date32(arrow_type):
            return {"type": "int", "logicalType": "date"}
        elif is_list(arrow_type):

            return {"type": "array", "items": ToAvro.type(cast(ListType, arrow_type).value_type)}
        elif is_struct(arrow_type):
            return {
                "type": "record",
                "name": "struct",
                "fields": [{"name": field.name, "type": ToAvro.type(field.type)} for field in
                           cast(StructType, arrow_type)]
            }
        else:
            raise ValueError(f"Unsupported PyArrow type: {arrow_type}")

    @property
    def schema(self):
        return {
            "type": "record",
            "name": "Root",
            "fields": list(map(lambda _field: {
                "name": _field.name,
                "type": ToAvro.type(_field.type)
            }, self.table.schema))
        }

    @property
    def records(self):
        return self.table.to_pylist()
