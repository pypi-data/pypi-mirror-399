import re
import pyarrow as pa
from pyiceberg.schema import Schema
from pyiceberg.types import (
    BooleanType, StringType, IntegerType, LongType, FloatType, DoubleType,
    DateType, TimestampType, TimestamptzType, BinaryType, NestedField
)
from iceberg_cli.utils import print_error

def parse_schema_string(schema_str: str) -> pa.Schema:
    """
    Parses a simple SQL-like schema string into a PyArrow Schema.
    Format: "col1 type, col2 type"
    Example: "id int, name string, price double, is_active boolean"
    
    Supported types mapping (simple):
    - int, integer -> int32
    - long, bigint -> int64
    - float -> float32
    - double -> float64
    - string, text -> string
    - boolean, bool -> bool
    - date -> date32
    - timestamp -> timestamp[us]
    - binary -> binary
    """
    fields = []
    # Split by comma, but careful about future complex types (structs) which might have commas.
    # For V1 we assume simple flat schema.
    items = [x.strip() for x in schema_str.split(',')]
    
    for item in items:
        parts = item.split()
        if len(parts) < 2:
            raise ValueError(f"Invalid column definition: '{item}'. Expected 'NAME TYPE'.")
        
        name = parts[0]
        type_str = parts[1].lower()
        
        pa_type = None
        if type_str in ['int', 'integer', 'int32']:
            pa_type = pa.int32()
        elif type_str in ['long', 'bigint', 'int64']:
            pa_type = pa.int64()
        elif type_str in ['float', 'float32']:
            pa_type = pa.float32()
        elif type_str in ['double', 'float64']:
            pa_type = pa.float64()
        elif type_str in ['string', 'text']:
            pa_type = pa.string()
        elif type_str in ['boolean', 'bool']:
            pa_type = pa.bool_()
        elif type_str in ['date']:
            pa_type = pa.date32()
        elif type_str in ['timestamp']:
            pa_type = pa.timestamp('us')
        elif type_str in ['binary']:
            pa_type = pa.binary()
        else:
            raise ValueError(f"Unsupported or unknown type: '{type_str}' for column '{name}'")
            
        fields.append(pa.field(name, pa_type))
        
    return pa.schema(fields)
