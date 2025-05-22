import os

# Puedes definir ROOT como una variable global o recibirlo como parámetro
ROOT = "Schema/"

def index_filename(*args: str) -> str:
    """
    Crea un archivo con nombre 'idx_<param1>_<param2>_...<paramN>.bin'
    """
    filename = "idx_" + "_".join(args) + ".bin"
    filepath = os.path.join(ROOT, filename)
    return filepath

def table_filename(name: str) -> str:
    """
    Crea un archivo con nombre 'name.bin' dentro del directorio ROOT
    y lo devuelve como un objeto de archivo abierto en modo escritura binaria.
    """
    filename = "table_" + name + ".bin"
    filepath = os.path.join(ROOT, filename)
    return filepath