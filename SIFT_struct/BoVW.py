import numpy as np
from sklearn.cluster import MiniBatchKMeans
import os
import matplotlib.pyplot as plt
import joblib

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

def crear_vocabulario_visual(all_desc, n_clusters=1000, random_state=42, output_path=None):
    """Aplica MiniBatchKMeans a todos los descriptores para crear el vocabulario visual y lo guarda en disco si se indica"""
    print(f"Entrenando MiniBatchKMeans con {n_clusters} clusters sobre {all_desc.shape[0]} descriptores...")
    kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=random_state, batch_size=1000, n_init=3)
    kmeans.fit(all_desc)
    print("✔️ Vocabulario visual generado.")
    if output_path is not None:
        joblib.dump(kmeans, output_path)
        print(f"✔️ Diccionario visual guardado en {output_path}")
    return kmeans

def construir_histogramas_por_imagen(data_dict, kmeans_path):
    """Construye un histograma de palabras visuales para cada imagen usando el diccionario visual desde disco"""
    kmeans = joblib.load(kmeans_path)
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
    visual_dict_path = os.path.join(script_dir, 'descriptors', 'visual_dictionary.pkl')

    # 1. Cargar todos los descriptores
    all_desc, nombres, data_dict = cargar_todos_los_descriptores(npz_path)

    # 2. Crear vocabulario visual (MiniBatchKMeans) y guardarlo en disco
    n_clusters = 1000  # Puedes ajustar este valor
    crear_vocabulario_visual(all_desc, n_clusters=n_clusters, output_path=visual_dict_path)

    # 3. Construir histogramas para cada imagen usando el diccionario visual desde disco
    histogramas = construir_histogramas_por_imagen(data_dict, visual_dict_path)

    # 4. Guardar histogramas
    guardar_histogramas(histogramas, output_hist_path)

    # 5. (Opcional) Mostrar o graficar histogramas
    #