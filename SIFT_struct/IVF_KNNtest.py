import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from SIFT_struct.InvertVisualFile import MultimediaImageRetrieval

def test_knn_search():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    mir = MultimediaImageRetrieval(base_dir, z=512, n_clusters=250)

    # Primero crea el índice y el heap (solo la primera vez o si quieres regenerar todo)
    print("Creando índices y heap...")
    mir.creacion(carpeta_entrada="SIFT_struct/test_images")
    print("\nContenido del heap (primeros 10 registros):")
    mir.mostrar_heap(max_registros=10)

    # Luego realiza las búsquedas KNN
    img_query1 = os.path.join(base_dir, "SIFT_struct/query_images", "auto_0005.jpg")
    img_query2 = os.path.join(base_dir, "SIFT_struct/query_images", "Bici_0003.jpg")
    img_query4 = os.path.join(base_dir, "SIFT_struct/query_images", "torre_query.jpg")

    print("\nKNN Search para auto_0005.jpg:")
    mir.knn_search(img_query1, k=5)

    print("\nKNN Search para Bici_0003.jpg:")
    mir.knn_search(img_query2, k=5)

    print("\nKNN Search para torre_query.jpg:")
    mir.knn_search(img_query4, k=5)

if __name__ == "__main__":
    test_knn_search()