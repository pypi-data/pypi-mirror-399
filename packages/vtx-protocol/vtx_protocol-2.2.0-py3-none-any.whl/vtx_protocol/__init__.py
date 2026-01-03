import os

def get_wit_path() -> str:
    """Returns the absolute path to vtx.wit included in the package."""
    return os.path.join(os.path.dirname(__file__), "wit", "vtx.wit")

from .generated.vtx import api
from .generated.vtx.api import types, sql, stream_io

# 3. 显式导出，优化 IDE 提示体验
__all__ = [
    "get_wit_path",
    "api",
    "types",
    "sql",
    "stream_io",
]