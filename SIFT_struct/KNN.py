import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def comparar_histogramas_coseno(npz_path, tfidf_path=None):
    """Abre el archivo de histogramas o TF-IDF y calcula la similitud de coseno entre todos los pares"""
    # Si existe el archivo TF-IDF, úsalo; si no, calcula y guárdalo
    if tfidf_path is not None and os.path.exists(tfidf_path):
        with np.load(tfidf_path) as data:
            keys = list(data.files)
            mats_tfidf = np.array([data[k] for k in keys])
    else:
        with np.load(npz_path) as data:
            histogramas = {key: data[key] for key in data.files}
        keys, mats_tfidf = calcular_tfidf(histogramas)
        if tfidf_path is not None:
            # Guardar el TF-IDF en un archivo .npz
            np.savez(tfidf_path, **{k: mats_tfidf[i] for i, k in enumerate(keys)})
            print(f"✔️ TF-IDF guardado en {tfidf_path}")

    # Calcula la matriz de similitud de coseno usando TF-IDF
    sim_matrix = cosine_similarity(mats_tfidf)
    n = len(keys)
    print("Pares de imágenes más similares (mayor valor = más similares):")
    pares = []
    for i in range(n):
        for j in range(i+1, n):
            pares.append((keys[i], keys[j], sim_matrix[i, j]))
    pares.sort(key=lambda x: -x[2])
    for a, b, sim in pares:
        print(f"{a} <-> {b}: similitud coseno = {sim:.4f}")

def calcular_tfidf(histogramas):
    # histogramas: dict {nombre: histograma}
    keys = list(histogramas.keys())
    mats = np.array([histogramas[k] for k in keys])
    N, V = mats.shape  # N imágenes, V palabras visuales

    # Document frequency (df): en cuántas imágenes aparece cada palabra visual
    df = np.sum(mats > 0, axis=0)
    idf = np.log((N + 1) / (df + 1)) + 1  # Suavizado para evitar división por cero

    # TF-IDF
    tfidf = mats * idf

    # Normalización L2
    norms = np.linalg.norm(tfidf, axis=1, keepdims=True)
    tfidf_normalized = tfidf / (norms + 1e-10)

    return keys, tfidf_normalized

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    hist_path = os.path.join(script_dir, 'descriptors', 'all_histograms.npz')
    tfidf_path = os.path.join(script_dir, 'descriptors', 'all_tfidf.npz')
    comparar_histogramas_coseno(hist_path, tfidf_path)