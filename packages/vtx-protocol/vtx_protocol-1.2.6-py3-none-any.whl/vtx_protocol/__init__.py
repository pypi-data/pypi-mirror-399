import os

def get_wit_path():
    """Returns the absolute path to vtx.wit"""
    return os.path.join(os.path.dirname(__file__), "wit", "vtx.wit")

def get_wit_content():
    """Returns the content of vtx.wit"""
    with open(get_wit_path(), 'r', encoding='utf-8') as f:
        return f.read()