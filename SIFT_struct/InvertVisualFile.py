import os
import numpy as np
import joblib
import cv2
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics.pairwise import cosine_similarity
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from SIFT_struct.redimensionar import resize_to_256_square
from SIFT_struct.SIFT import load_and_verify_image, extract_descriptors
from SIFT_struct.BoVW import cargar_todos_los_descriptores, crear_vocabulario_visual, construir_histogramas_por_imagen
from SIFT_struct.KNN import calcular_tfidf
from Utils.Registro import RegistroType
from Heap_struct.Heap import Heap

class MultimediaImageRetrieval:
    """
    Sistema de recuperación de imágenes multimedia usando BoVW y TF-IDF,
    con almacenamiento en memoria secundaria y manejo de encabezados.
    """

    def __init__(self, base_dir, z=512, n_clusters=1000):
        self.base_dir = base_dir
        self.z = z
        self.n_clusters = n_clusters

        # Rutas de archivos
        self.img_dir = os.path.join(base_dir, "SIFT_struct/test_images_reescaladas")
        self.descriptor_path = os.path.join(base_dir, "SIFT_struct/descriptors", "all_descriptors.npz")
        self.visual_dict_path = os.path.join(base_dir, "SIFT_struct/descriptors", "visual_dictionary.pkl")
        self.hist_path = os.path.join(base_dir, "SIFT_struct/descriptors", "all_histograms.npz")
        self.tfidf_path = os.path.join(base_dir, "SIFT_struct/descriptors", "all_tfidf.npz")
        self.heap_file = os.path.join(base_dir, "SIFT_struct/descriptors", "heap_hist.bin")

        # Asegúrate de que la carpeta descriptors exista
        os.makedirs(os.path.dirname(self.heap_file), exist_ok=True)

        # Formato del registro: nombre (100s) + vector tfidf (n_clusters * f)
        dict_format = {"nombre": "100s"}
        for i in range(n_clusters):
            dict_format[f"tfidf_{i}"] = "f"
        self.registro = RegistroType(dict_format, key_name="nombre")
        self.heap = Heap(dict_format, "nombre", self.heap_file, force_create=not os.path.exists(self.heap_file))

    def _add_descriptor_to_npz(self, nombre, descriptor):
        """Agrega un descriptor local al archivo all_descriptors.npz en disco."""
        if os.path.exists(self.descriptor_path):
            with np.load(self.descriptor_path) as data:
                descs = dict(data)
        else:
            descs = {}
        descs[nombre] = descriptor
        np.savez(self.descriptor_path, **descs)

    def _update_vocabulario(self):
        """Actualiza el vocabulario visual con todos los descriptores y lo guarda en disco."""
        all_desc, _, _ = cargar_todos_los_descriptores(self.descriptor_path)
        crear_vocabulario_visual(all_desc, n_clusters=self.n_clusters, output_path=self.visual_dict_path)

    def _add_histograma_to_npz(self, nombre, hist):
        """Agrega un histograma al archivo all_histograms.npz en disco."""
        if os.path.exists(self.hist_path):
            with np.load(self.hist_path) as data:
                hists = dict(data)
        else:
            hists = {}
        hists[nombre] = hist
        np.savez(self.hist_path, **hists)

    def _update_tfidf(self):
        with np.load(self.hist_path) as data:
            histogramas = {key: data[key] for key in data.files}
        # Normaliza todos los histogramas a la longitud correcta
        for k in histogramas:
            h = histogramas[k]
            if len(h) < self.n_clusters:
                histogramas[k] = np.pad(h, (0, self.n_clusters - len(h)), 'constant')
            elif len(h) > self.n_clusters:
                histogramas[k] = h[:self.n_clusters]
        keys, mats_tfidf = calcular_tfidf(histogramas)
        np.savez(self.tfidf_path, **{k: mats_tfidf[i] for i, k in enumerate(keys)})

    def _get_tfidf_vector(self, nombre):
        """Obtiene el vector tf-idf normalizado de una imagen por su nombre."""
        with np.load(self.tfidf_path) as data:
            return data[nombre]

    def insert(self, image_path):
        """
        Inserta una nueva imagen al sistema:
        1. Redimensiona y guarda la imagen.
        2. Extrae descriptores locales y los agrega a all_descriptors.npz.
        3. Actualiza el vocabulario visual (visual_dictionary.pkl).
        4. Calcula y agrega el histograma BoVW a all_histograms.npz.
        5. Actualiza el archivo all_tfidf.npz.
        6. Inserta el registro (nombre, vector tf-idf) en el Heap.
        """
        # 1. Redimensionar y guardar imagen
        nombre_base = os.path.splitext(os.path.basename(image_path))[0] + "_reescalado"
        ext = os.path.splitext(image_path)[1]
        img_out_path = os.path.join(self.img_dir, nombre_base + ext)
        os.makedirs(self.img_dir, exist_ok=True)
        resize_to_256_square(image_path, img_out_path, self.z)

        # 2. Extraer descriptores locales
        img = load_and_verify_image(img_out_path)
        sift = cv2.SIFT_create()
        _, descriptor = extract_descriptors(img, sift)
        if descriptor is None or len(descriptor) == 0:
            raise ValueError("No se pudieron extraer descriptores de la imagen.")
        self._add_descriptor_to_npz(nombre_base, descriptor)

        # 3. Actualizar vocabulario visual
        self._update_vocabulario()

        # 4. Calcular y agregar histograma BoVW
        # Solo para la nueva imagen, pero requiere el modelo actualizado
        data_dict = {nombre_base: descriptor}
        hist = construir_histogramas_por_imagen(data_dict, self.visual_dict_path)[nombre_base]
        self._add_histograma_to_npz(nombre_base, hist)

        # 5. Actualizar archivo tf-idf
        self._update_tfidf()

        # 6. Insertar registro en Heap
        tfidf_vec = self._get_tfidf_vector(nombre_base)
        # Registro: nombre (string, 100s) + vector tfidf (floats)
        reg = [nombre_base] + list(tfidf_vec)
        self.heap.insert(reg)
        print(f"✔️ Imagen '{nombre_base}' insertada correctamente.")

    def knn_search(self, image_path, k=3):
        """
        Busca las k imágenes más similares a la imagen dada usando similitud de coseno sobre TF-IDF.
        """
        # 1. Procesar imagen de consulta igual que insert (pero no la agrega)
        nombre_base = "__consulta__"
        ext = os.path.splitext(image_path)[1]
        img_tmp_path = os.path.join(self.img_dir, nombre_base + ext)
        resize_to_256_square(image_path, img_tmp_path, self.z)
        img = load_and_verify_image(img_tmp_path)
        sift = cv2.SIFT_create()
        _, descriptor = extract_descriptors(img, sift)
        if descriptor is None or len(descriptor) == 0:
            raise ValueError("No se pudieron extraer descriptores de la imagen de consulta.")

        # 2. Cargar vocabulario visual y calcular histograma
        kmeans = joblib.load(self.visual_dict_path)
        words = kmeans.predict(descriptor)
        hist, _ = np.histogram(words, bins=np.arange(self.n_clusters+1))

        
            # 3. Cargar todos los histogramas y calcular TF-IDF para la consulta
        with np.load(self.hist_path) as data:
            histogramas = {key: data[key] for key in data.files}
        histogramas[nombre_base] = hist

        # --- Normaliza todos los histogramas ---
        for key in histogramas:
            h = histogramas[key]
            if len(h) < self.n_clusters:
                histogramas[key] = np.pad(h, (0, self.n_clusters - len(h)), 'constant')
            elif len(h) > self.n_clusters:
                histogramas[key] = h[:self.n_clusters]

        keys, mats_tfidf = calcular_tfidf(histogramas)
        idx = keys.index(nombre_base)
        tfidf_query = mats_tfidf[idx]
        # Eliminar la consulta de la lista para comparar solo contra la base
        keys_base = [k for k in keys if k != nombre_base]
        mats_base = np.array([mats_tfidf[i] for i, k in enumerate(keys) if k != nombre_base])

        # 4. Calcular similitud de coseno
        sims = cosine_similarity([tfidf_query], mats_base)[0]
        top_idx = np.argsort(-sims)[:k]
        resultados = [(keys_base[i], float(sims[i])) for i in top_idx]
        print("Imágenes más similares:")
        for nombre, sim in resultados:
            print(f"{nombre}: similitud coseno = {sim:.4f}")
        return resultados
    

