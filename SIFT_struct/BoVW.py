import numpy as np
from sklearn.cluster import KMeans
import os
import matplotlib.pyplot as plt

def cargar_todos_los_descriptores(npz_path):
    """Carga todos los descriptores de todas las imágenes en una sola matriz y un diccionario"""
    with np.load(npz_path) as data:
        descriptores = []
        nombres = []
        data_dict = {}
        for key in data.files:
            desc = data[key]
            descriptores.append(desc)
            nombres.append(key)
            data_dict[key] = desc
        all_desc = np.vstack(descriptores)
    return all_desc, nombres, data_dict

def crear_vocabulario_visual(all_desc, n_clusters=100, random_state=42):
    """Aplica KMeans a todos los descriptores para crear el vocabulario visual"""
    print(f"Entrenando KMeans con {n_clusters} clusters sobre {all_desc.shape[0]} descriptores...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    kmeans.fit(all_desc)
    print("✔️ Vocabulario visual generado.")
    return kmeans

def construir_histogramas_por_imagen(data_dict, kmeans):
    """Construye un histograma de palabras visuales para cada imagen"""
    histogramas = {}
    for key, desc in data_dict.items():
        words = kmeans.predict(desc)
        hist, _ = np.histogram(words, bins=np.arange(kmeans.n_clusters+1))
        histogramas[key] = hist
    return histogramas
def guardar_histogramas(histogramas, output_path):
    """Guarda los histogramas de todas las imágenes en un archivo .npz"""
    np.savez(output_path, **histogramas)
    print(f"✔️ Histogramas guardados en {output_path}")

def mostrar_histogramas(histogramas):
    """Muestra los histogramas de palabras visuales para cada imagen"""
    print("Histogramas de palabras visuales por imagen:")
    for key, hist in histogramas.items():
        print(f"- {key}: {hist}")



def graficar_histogramas(histogramas, n_cols=3, figsize=(15, 8)):
    """Grafica los histogramas de palabras visuales para cada imagen"""
    keys = list(histogramas.keys())
    n_imgs = len(keys)
    n_rows = (n_imgs + n_cols - 1) // n_cols

    plt.figure(figsize=figsize)
    for i, key in enumerate(keys):
        plt.subplot(n_rows, n_cols, i + 1)
        plt.bar(range(len(histogramas[key])), histogramas[key])
        plt.title(key)
        plt.xlabel("Palabra visual")
        plt.ylabel("Frecuencia")
        plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Configura las rutas según tu estructura
    script_dir = os.path.dirname(os.path.abspath(__file__))
    npz_path = os.path.join(script_dir, 'descriptors', 'all_descriptors.npz')
    output_hist_path = os.path.join(script_dir, 'descriptors', 'all_histograms.npz')

    # 1. Cargar todos los descriptores
    all_desc, nombres, data_dict = cargar_todos_los_descriptores(npz_path)

    # 2. Crear vocabulario visual (KMeans)
    n_clusters = 100  # Puedes ajustar este valor
    kmeans = crear_vocabulario_visual(all_desc, n_clusters=n_clusters)

    # 3. Construir histogramas para cada imagen
    histogramas = construir_histogramas_por_imagen(data_dict, kmeans)

    # 4. Guardar histogramas
    guardar_histogramas(histogramas, output_hist_path)

    graficar_histogramas(histogramas)