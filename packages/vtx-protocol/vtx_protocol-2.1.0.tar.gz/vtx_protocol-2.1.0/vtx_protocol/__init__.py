import os

def get_wit_path() -> str:
    """Returns the absolute path to vtx.wit"""
    return os.path.join(os.path.dirname(__file__), "wit", "vtx.wit")

def get_wit_content() -> str:
    """Returns the content of vtx.wit"""
    with open(get_wit_path(), 'r', encoding='utf-8') as f:
        return f.read()

try:
    from .generated import vtx
    from .generated.vtx import api

    if hasattr(api, 'types'):
        types = api.types
    if hasattr(api, 'sql'):
        sql = api.sql
    if hasattr(api, 'stream_io'):
        stream_io = api.stream_io

except ImportError:
    pass
