"""Serialize and deserialize Polars dataframe schemas.

This module provides functions to convert Polars dataframe schemas to JSON-serializable
dictionaries and vice versa, supporting all Polars data types including nested structures,
enums, categoricals, date/datetime, etc.
"""

from typing import Any
import polars as pl

from .typing import PolarsDataType


__all__ = [
    "schema_to_dict",
    "dict_to_schema",
]


def schema_to_dict(schema: pl.DataFrame | pl.Schema | dict[str, PolarsDataType]) -> dict[str, dict[str, Any]]:
    """Convert a Polars schema to a serializable dictionary.

    Takes a Polars schema (either pl.Schema or dict) and converts it to a JSON-serializable
    dictionary that contains all information needed to exactly regenerate the original schema.

    Parameters
    ----------
    schema
        A Polars schema object, dictionary mapping column names to DataTypes, or a DataFrame.

    Returns
    -------
    dict
        A dictionary with column names as keys and schema information as values.
        Each value contains 'dtype' and optional type-specific parameters.

    Examples
    --------
    >>> import polars as pl
    >>> df = pl.DataFrame({
    ...     'a': [1, 2, 3],
    ...     'b': ['x', 'y', 'z']
    ... })
    >>> schema_dict = schema_to_dict(df)  # Pass DataFrame directly
    >>> schema_dict
    {'a': {'dtype': 'Int64'}, 'b': {'dtype': 'String'}}
    >>> # Or pass the schema explicitly
    >>> schema_to_dict(df.schema) == schema_dict
    True
    """
    # If input is a DataFrame, extract its schema
    if isinstance(schema, pl.DataFrame):
        schema = schema.schema

    result = {}
    for col_name, dtype in schema.items():
        result[col_name] = _dtype_to_dict(dtype)
    return result


def dict_to_schema(schema_dict: dict[str, dict[str, Any]]) -> pl.Schema:
    """Convert a serialized schema dictionary back to a Polars schema.

    Takes the dictionary output of schema_to_dict and reconstructs the original Polars schema.

    Parameters
    ----------
    schema_dict
        A dictionary produced by schema_to_dict with column names as keys.

    Returns
    -------
    pl.Schema
        A Polars Schema object that can be used to create or validate dataframes.

    Examples
    --------
    >>> schema_dict = {'a': {'dtype': 'Int64'}, 'b': {'dtype': 'String'}}
    >>> schema = dict_to_schema(schema_dict)
    >>> schema
    Schema({'a': Int64, 'b': String})
    """
    result = {}
    for col_name, type_info in schema_dict.items():
        result[col_name] = _dict_to_dtype(type_info)
    return pl.Schema(result)


def _dtype_to_dict(dtype: PolarsDataType) -> dict[str, Any]:
    """Convert a Polars DataType to a serializable dictionary.

    Handles all Polars data types including numeric, temporal, nested, string, and other types.

    Parameters
    ----------
    dtype
        A Polars DataType instance.

    Returns
    -------
    dict
        A dictionary representation of the DataType with its parameters.
    """
    dtype_name = dtype.__class__.__name__

    # Handle each data type category
    if isinstance(dtype, pl.Decimal):
        return {
            'dtype': dtype_name,
            'precision': dtype.precision,
            'scale': dtype.scale,
        }

    elif isinstance(dtype, (pl.Array, pl.List)):
        return {
            'dtype': dtype_name,
            'inner': _dtype_to_dict(dtype.inner),
            **(
                {'width': dtype.width, 'shape': dtype.shape}
                if isinstance(dtype, pl.Array)
                else {}
            ),
        }

    elif isinstance(dtype, pl.Struct):
        return {
            'dtype': dtype_name,
            'fields': [
                {'name': field.name, 'dtype': _dtype_to_dict(field.dtype)}
                for field in dtype.fields
            ],
        }

    elif isinstance(dtype, pl.Enum):
        return {
            'dtype': dtype_name,
            'categories': dtype.categories.to_list() if dtype.categories is not None else None,
        }

    elif isinstance(dtype, pl.Categorical):
        return {
            'dtype': dtype_name,
            'ordering': dtype.ordering,
        }

    elif isinstance(dtype, pl.Datetime):
        return {
            'dtype': dtype_name,
            'time_zone': dtype.time_zone,
            'time_unit': dtype.time_unit,
        }

    elif isinstance(dtype, pl.Duration):
        return {
            'dtype': dtype_name,
            'time_unit': dtype.time_unit,
        }

    elif isinstance(dtype, pl.Field):
        return {
            'dtype': dtype_name,
            'name': dtype.name,
            'inner': _dtype_to_dict(dtype.dtype),
        }

    else:
        # Simple types with no parameters
        return {'dtype': dtype_name}


def _dict_to_dtype(type_info: dict[str, Any]) -> PolarsDataType:
    """Convert a serialized type dictionary back to a Polars DataType.

    Reconstructs any Polars DataType from its serialized dictionary representation.

    Parameters
    ----------
    type_info
        A dictionary with 'dtype' key and optional type-specific parameters.

    Returns
    -------
    pl.DataType
        A Polars DataType instance.
    """
    dtype_name = type_info['dtype']

    # Numeric types
    if dtype_name == 'Int8':
        return pl.Int8()
    elif dtype_name == 'Int16':
        return pl.Int16()
    elif dtype_name == 'Int32':
        return pl.Int32()
    elif dtype_name == 'Int64':
        return pl.Int64()
    elif dtype_name == 'Int128':
        return pl.Int128()
    elif dtype_name == 'UInt8':
        return pl.UInt8()
    elif dtype_name == 'UInt16':
        return pl.UInt16()
    elif dtype_name == 'UInt32':
        return pl.UInt32()
    elif dtype_name == 'UInt64':
        return pl.UInt64()
    elif dtype_name == 'Float16':
        return pl.Float16()
    elif dtype_name == 'Float32':
        return pl.Float32()
    elif dtype_name == 'Float64':
        return pl.Float64()
    elif dtype_name == 'Decimal':
        return pl.Decimal(precision=type_info['precision'], scale=type_info['scale'])

    # String types
    elif dtype_name == 'String':
        return pl.String()
    elif dtype_name == 'Utf8':
        return pl.String()  # Utf8 is an alias for String
    elif dtype_name == 'Binary':
        return pl.Binary()
    elif dtype_name == 'Categorical':
        return pl.Categorical(ordering=type_info.get('ordering', 'physical'))
    elif dtype_name == 'Enum':
        categories = type_info.get('categories')
        return pl.Enum(categories=categories)

    # Temporal types
    elif dtype_name == 'Date':
        return pl.Date()
    elif dtype_name == 'Time':
        return pl.Time()
    elif dtype_name == 'Datetime':
        return pl.Datetime(
            time_zone=type_info.get('time_zone'),
            time_unit=type_info.get('time_unit', 'us'),
        )
    elif dtype_name == 'Duration':
        return pl.Duration(time_unit=type_info.get('time_unit', 'us'))

    # Nested types
    elif dtype_name == 'List':
        inner_dtype = _dict_to_dtype(type_info['inner'])
        return pl.List(inner_dtype)
    elif dtype_name == 'Array':
        inner_dtype = _dict_to_dtype(type_info['inner'])
        width = type_info.get('width')
        shape = type_info.get('shape')
        if width is not None and shape is not None:
            return pl.Array(inner_dtype, width=width, shape=shape)
        return pl.Array(inner_dtype)
    elif dtype_name == 'Struct':
        fields = []
        for field_info in type_info.get('fields', []):
            field_name = field_info['name']
            field_dtype = _dict_to_dtype(field_info['dtype'])
            fields.append(pl.Field(field_name, field_dtype))
        return pl.Struct(fields)
    elif dtype_name == 'Field':
        field_name = type_info['name']
        field_dtype = _dict_to_dtype(type_info['inner'])
        return pl.Field(field_name, field_dtype)

    # Other types
    elif dtype_name == 'Boolean':
        return pl.Boolean()
    elif dtype_name == 'Null':
        return pl.Null()
    elif dtype_name == 'Object':
        return pl.Object()
    elif dtype_name == 'Unknown':
        return pl.Unknown()

    else:
        raise ValueError(f"Unknown data type: {dtype_name}")
