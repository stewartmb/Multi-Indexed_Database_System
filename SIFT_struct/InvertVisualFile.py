import os
import numpy as np
import joblib
import cv2
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics.pairwise import cosine_similarity
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from SIFT_struct.redimensionar import *
from SIFT_struct.SIFT import *
from SIFT_struct.BoVW import *
from SIFT_struct.KNN import *
from Utils.Registro import *
from Heap_struct.Heap import *

class MultimediaImageRetrieval:
    """
    Sistema de recuperación de imágenes multimedia usando BoVW y TF-IDF,
    con almacenamiento en memoria secundaria y manejo de encabezados.
    El índice trabaja sobre un archivo heap_file (data_file) que contiene todos los atributos de la tabla,
    entre ellos la ruta de la imagen como string.
    """

    def __init__(self,
                 table_format: dict,
                 key: str,
                 data_file_name: str,  # heap_file con todos los atributos de la tabla
                 index_file_name: str, # heap_file del índice (nombre, vector tfidf, pos)
                 base_dir: str,
                 z=512,
                 n_clusters=1000,
                 force_create: bool = False,
                 ruta_col_name = "ruta"):
        """
        table_format: formato de la tabla principal (incluye la ruta de la imagen)
        key: nombre del campo clave de la tabla principal
        data_file_name: archivo binario principal (heap_file) con todos los atributos
        index_file_name: archivo binario del índice (heap_file del índice)
        base_dir: base del proyecto
        z: tamaño de redimensión
        n_clusters: clusters para BoVW
        force_create: fuerza la creación de archivos
        """
        self.base_dir = base_dir
        self.z = z
        self.n_clusters = n_clusters
        self.ruta_col_name = ruta_col_name
        # Rutas de archivos auxiliares
        self.img_dir = os.path.join(base_dir, "SIFT_struct/test_images_reescaladas")
        self.descriptor_path = os.path.join(base_dir, "SIFT_struct/descriptors", "all_descriptors.npz")
        self.visual_dict_path = os.path.join(base_dir, "SIFT_struct/descriptors", "visual_dictionary.pkl")
        self.hist_path = os.path.join(base_dir, "SIFT_struct/descriptors", "all_histograms.npz")
        self.tfidf_path = os.path.join(base_dir, "SIFT_struct/descriptors", "all_tfidf.npz")
        self.RT = RegistroType(table_format, key_name=key)
        # Heap principal (tabla completa)
        self.HEAP = Heap(table_format, key, data_file_name, force_create=force_create)

        # Formato del índice: posición (i), nombre (100s), vector tfidf (n_clusters * f)
        dict_format = {"pos": "i", "nombre": "100s"}
        for i in range(n_clusters):
            dict_format[f"tfidf_{i}"] = "f"
        self.index_heap = Heap(dict_format, "pos", index_file_name, force_create=force_create)

        # Asegúrate de que la carpeta descriptors exista
        os.makedirs(os.path.dirname(self.descriptor_path), exist_ok=True)
        os.makedirs(self.img_dir, exist_ok=True)

    def _get_ruta_from_pos(self, pos):
        """Obtiene la ruta de la imagen a partir de la posición en el heap principal."""
        reg = self.HEAP.read(pos)
        if reg is None:
            raise ValueError(f"No se encontró registro en posición {pos}")
        # Busca el índice de la columna de ruta
        if isinstance(self.HEAP.RT.key, str):
            keys = list(self.HEAP.RT.dict_format.keys())
            ruta_idx = keys.index(self.ruta_col_name)
        else:
            ruta_idx = self.ruta_col_name
        return reg[ruta_idx]

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

    def insert(self, pos):
        """
        Inserta una nueva imagen al índice usando la posición del registro en el heap principal.
        1. Obtiene la ruta de la imagen desde el heap principal.
        2. Redimensiona y guarda la imagen.
        3. Extrae descriptores locales y los agrega a all_descriptors.npz.
        4. Actualiza el vocabulario visual (visual_dictionary.pkl).
        5. Calcula y agrega el histograma BoVW a all_histograms.npz.
        6. Actualiza el archivo all_tfidf.npz.
        7. Inserta el registro (pos, nombre, vector tf-idf) en el heap del índice.
        """
        ruta = self._get_ruta_from_pos(pos)
        nombre_base = os.path.splitext(os.path.basename(ruta))[0] + "_reescalado"
        ext = os.path.splitext(ruta)[1]
        img_out_path = os.path.join(self.img_dir, nombre_base + ext)
        os.makedirs(self.img_dir, exist_ok=True)
        resize_to_256_square(ruta, img_out_path, self.z)

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
        data_dict = {nombre_base: descriptor}
        hist = construir_histogramas_por_imagen(data_dict, self.visual_dict_path)[nombre_base]
        self._add_histograma_to_npz(nombre_base, hist)

        # 5. Actualizar archivo tf-idf
        self._update_tfidf()

        # 6. Insertar registro en Heap del índice
        tfidf_vec = self._get_tfidf_vector(nombre_base)
        reg = [pos, nombre_base] + list(tfidf_vec)
        self.index_heap.insert(reg)
        print(f"✔️ Imagen '{nombre_base}' (pos {pos}) insertada correctamente en el índice.")

    def knn_search(self, pos, k=3):
        """
        Busca las k imágenes más similares a la imagen dada usando similitud de coseno sobre TF-IDF.
        Recibe la posición del registro en el heap principal.
        Retorna una lista de posiciones (posiciones en el heap principal) de las imágenes más similares.
        """
        ruta = self._get_ruta_from_pos(pos)
        nombre_base = "__consulta__"
        ext = os.path.splitext(ruta)[1]
        img_tmp_path = os.path.join(self.img_dir, nombre_base + ext)
        resize_to_256_square(ruta, img_tmp_path, self.z)
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

        # 4. Obtener todas las posiciones y nombres del heap del índice
        registros = self.index_heap._select_all()
        pos_list = [reg[0] for reg in registros]
        nombre_list = [reg[1] for reg in registros]

        # Alinear los vectores tfidf con las posiciones
        tfidf_base = []
        pos_base = []
        for nombre, posi in zip(nombre_list, pos_list):
            if nombre in keys_base:
                idx = keys_base.index(nombre)
                tfidf_base.append(mats_base[idx])
                pos_base.append(posi)
        tfidf_base = np.array(tfidf_base)

        # 5. Calcular similitud de coseno
        if len(tfidf_base) == 0:
            print("No hay imágenes indexadas para comparar.")
            return []
        sims = cosine_similarity([tfidf_query], tfidf_base)[0]
        top_idx = np.argsort(-sims)[:k]
        resultados = [(pos_base[i], float(sims[i])) for i in top_idx]
        # Filtrar la posición consultada
        resultados = [r for r in resultados if r[0] != pos]
        print("Imágenes más similares (posiciones en heap principal):")
        for posi, sim in resultados:
            print(f"pos {posi}: similitud coseno = {sim:.4f}")
        return [posi for posi, _ in resultados]

    def mostrar_heap(self, max_registros=10):
        print(f"Contenido de {self.index_heap.filename}:")
        count = 0
        registros = self.index_heap._select_all()
        for reg in registros:
            nombre = reg[1].rstrip('\x00')
            pos = reg[0]
            tfidf_preview = reg[2:2+min(5, self.n_clusters)]
            print(f"pos={pos} | {nombre} | tfidf[:5]={tfidf_preview} ...")
            count += 1
            if count >= max_registros:
                break
        if count == 0:
            print("Heap vacío.")