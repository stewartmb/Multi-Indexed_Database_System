import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def cargar_histogramas(npz_path):
    """Carga los histogramas de imágenes desde un archivo .npz"""
    with np.load(npz_path) as data:
        histogramas = {key: data[key] for key in data.files}
    return histogramas

def comparar_histogramas_coseno(histogramas):
    """Calcula la similitud de coseno entre todos los pares de histogramas y muestra los más similares"""
    keys = list(histogramas.keys())
    mats = np.array([histogramas[k] for k in keys])
    # Calcula la matriz de similitud de coseno
    sim_matrix = cosine_similarity(mats)
    n = len(keys)
    print("Pares de imágenes más similares (mayor valor = más similares):")
    # Solo muestra cada par una vez y no la diagonal
    pares = []
    for i in range(n):
        for j in range(i+1, n):
            pares.append((keys[i], keys[j], sim_matrix[i, j]))
    # Ordenar por similitud descendente
    pares.sort(key=lambda x: -x[2])
    for a, b, sim in pares:
        print(f"{a} <-> {b}: similitud coseno = {sim:.4f}")

if __name__ == "__main__":
    # Cambia la ruta si es necesario
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    hist_path = os.path.join(script_dir, 'descriptors', 'all_histograms.npz')
    histogramas = cargar_histogramas(hist_path)
    comparar_histogramas_coseno(histogramas)