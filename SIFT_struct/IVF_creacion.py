import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from SIFT_struct.InvertVisualFile import MultimediaImageRetrieval

def test_creacion():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    mir = MultimediaImageRetrieval(base_dir, z=512, n_clusters=100)
    print("Iniciando proceso de creación de índices y heap...")
    mir.creacion(carpeta_entrada="SIFT_struct/test_images")
    print("\nContenido del heap (primeros 10 registros):")
    mir.mostrar_heap(max_registros=10)

if __name__ == "__main__":
    test_creacion()
 