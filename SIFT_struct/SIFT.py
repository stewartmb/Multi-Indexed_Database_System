import cv2
import os
import sys
import numpy as np
from sklearn.decomposition import PCA

def load_and_verify_image(path):
    """Carga una imagen y verifica su integridad"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen: {path} (¿Formato inválido?)")
    
    if img.dtype != 'uint8':
        img = cv2.convertScaleAbs(img)
        print(f"Convertida imagen a uint8: {path}")
    
    return img

def extract_descriptors(img, sift, pca=None):
    """Extrae los descriptores locales de una imagen usando SIFT y aplica PCA si se proporciona"""
    keypoints, descriptors = sift.detectAndCompute(img, None)
    if descriptors is not None and pca is not None:
        descriptors = pca.transform(descriptors)
    return keypoints, descriptors

def fit_pca_on_all_descriptors(images_dir, sift, n_components):
    """Ajusta un PCA sobre todos los descriptores de todas las imágenes"""
    all_desc = []
    for filename in os.listdir(images_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(images_dir, filename)
            img = load_and_verify_image(img_path)
            _, descriptors = sift.detectAndCompute(img, None)
            if descriptors is not None:
                all_desc.append(descriptors)
    if not all_desc:
        raise ValueError("No se encontraron descriptores en ninguna imagen.")
    all_desc = np.vstack(all_desc)
    pca = PCA(n_components=n_components)
    pca.fit(all_desc)
    return pca

def process_and_save_all_descriptors(images_dir, output_npz_path, n_components=None, batch_size=50):
    """
    Procesa todas las imágenes y guarda todos los descriptores (posiblemente reducidos) en un solo archivo .npz.
    Procesa en lotes y guarda temporalmente cada batch para ahorrar memoria.
    """
    sift = cv2.SIFT_create()
    pca = None
    filenames = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if n_components is not None and n_components < 128:
        print(f"Ajustando PCA para reducir descriptores a {n_components} dimensiones...")
        pca = fit_pca_on_all_descriptors(images_dir, sift, n_components)

    batch_files_list = []
    total = len(filenames)
    for batch_start in range(0, total, batch_size):
        batch_files = filenames[batch_start:batch_start+batch_size]
        batch_descriptors = {}
        print(f"\nProcesando batch {batch_start//batch_size + 1} ({len(batch_files)} imágenes)...")
        for filename in batch_files:
            img_path = os.path.join(images_dir, filename)
            print(f"  Procesando {filename}...")
            try:
                img = load_and_verify_image(img_path)
                keypoints, descriptors = extract_descriptors(img, sift, pca)
                if descriptors is None:
                    print(f"    ⚠️  No se encontraron descriptores en {filename}")
                    continue
                key = os.path.splitext(filename)[0]
                batch_descriptors[key] = descriptors
            except Exception as img_e:
                print(f"    ❌ Error procesando {filename}: {img_e}")
        # Guardar temporalmente el batch
        batch_npz = f"{output_npz_path}_batch_{batch_start//batch_size + 1}.npz"
        np.savez(batch_npz, **batch_descriptors)
        batch_files_list.append(batch_npz)
        del batch_descriptors  # Libera memoria

    # Combinar todos los batches en un solo archivo final
    all_descriptors = {}
    for batch_npz in batch_files_list:
        with np.load(batch_npz) as data:
            for key in data.files:
                all_descriptors[key] = data[key]
        os.remove(batch_npz)  # Borra el archivo temporal

    np.savez(output_npz_path, **all_descriptors)
    print(f"\n✔️  Todos los descriptores guardados en {output_npz_path}")

def mostrar_contenido_npz(npz_path):
    """Muestra las claves y la forma de los arrays almacenados en un archivo .npz"""
    with np.load(npz_path) as data:
        print(f"Contenido de {npz_path}:")
        for key in data.files:
            print(f" - {key}: shape={data[key].shape}, dtype={data[key].dtype}")

def main():
    try:
        # Configuración de rutas
        script_dir = os.path.dirname(os.path.abspath(__file__))
        test_images_dir = os.path.join(script_dir, 'test_images_reescaladas')
        output_npz_path = os.path.join(script_dir, 'descriptors', 'all_descriptors.npz')

        # Crear directorio para descriptores si no existe
        os.makedirs(os.path.dirname(output_npz_path), exist_ok=True)

        # Verificar existencia del directorio de imágenes
        if not os.path.exists(test_images_dir):
            raise FileNotFoundError(f"Directorio no encontrado: {test_images_dir}")

        # Cambia el valor de n_components para reducir la dimensión (por ejemplo, 70)
        process_and_save_all_descriptors(test_images_dir, output_npz_path, n_components=None)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    mostrar_contenido_npz(output_npz_path)

if __name__ == "__main__":
    main()