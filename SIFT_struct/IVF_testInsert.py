import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from SIFT_struct.InvertVisualFile import MultimediaImageRetrieval

def test_insert_and_show_heap():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Base directory: {base_dir}")
    mir = MultimediaImageRetrieval(base_dir, z=512, n_clusters=100)  # Usa pocos clusters para pruebas rápidas

    # Usa imágenes reales de tu carpeta test_images
    img1 = os.path.join(base_dir, "SIFT_struct/test_images", "auto_0001.jpg")
    img2 = os.path.join(base_dir, "SIFT_struct/test_images", "Bici_0001.jpg")
    img3 = os.path.join(base_dir, "SIFT_struct/test_images", "billete_0001.jpg")
    img4 = os.path.join(base_dir, "SIFT_struct/test_images", "auto_0002.jpg")
    img5 = os.path.join(base_dir, "SIFT_struct/test_images", "Bici_0002.jpg")
    img6 = os.path.join(base_dir, "SIFT_struct/test_images", "auto_0003.jpg")
    img7 = os.path.join(base_dir, "SIFT_struct/test_images", "auto_0004.jpg")
    img8 = os.path.join(base_dir, "SIFT_struct/test_images", "billete_0002.jpg")

    # Inserta imágenes
    print("Insertando imagen 1...")
    mir.insert(img1)
    print("Insertando imagen 2...")
    mir.insert(img2)
    print("Insertando imagen 3...")
    mir.insert(img3)
    print("Insertando imagen 4...")
    mir.insert(img4)

    # Muestra el contenido del heap
    print("\nContenido del heap (4 imagenes):")
    mir.mostrar_heap(max_registros=10)

    print("Insertando imagen 5...")
    mir.insert(img5)
    print("Insertando imagen 6...")
    mir.insert(img6)
    print("Insertando imagen 7...")
    mir.insert(img7)
    print("Insertando imagen 8...")
    mir.insert(img8)

    # Muestra el contenido del heap
    print("\nContenido del heap (8 imagenes):")
    mir.mostrar_heap(max_registros=10)

if __name__ == "__main__":
    test_insert_and_show_heap()