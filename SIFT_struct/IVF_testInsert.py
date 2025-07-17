import sys
import unittest
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from SIFT_struct.InvertVisualFile import MultimediaImageRetrieval

class TestMultimediaImageRetrieval(unittest.TestCase):
    def setUp(self):
        # Configuración de prueba
        self.table_format = {
            "id": "i",
            "nombre": "100s",
            "ruta": "100s"
        }
        self.key = "id"
        self.data_file_name = "test_data_file.bin"
        self.index_file_name = "test_index_file.bin"
        self.base_dir = "."
        self.n_clusters = 10  # Número pequeño para pruebas rápidas
        self.ruta_col_name = "ruta"

        # Crear heap principal con registros de prueba
        self.ivf = MultimediaImageRetrieval(
            table_format=self.table_format,
            key=self.key,
            data_file_name=self.data_file_name,
            index_file_name=self.index_file_name,
            base_dir=self.base_dir,
            n_clusters=self.n_clusters,
            force_create=True,
            ruta_col_name=self.ruta_col_name
        )

        # Insertar registros de prueba en el heap principal
        self.rutas = [
            "SIFT_struct/test_images/auto_0001.jpg",
            "SIFT_struct/test_images/Bici_0001.jpg",
            "SIFT_struct/test_images/billete_0001.jpg"
        ]
        self.nombres = ["auto_0001", "Bici_0001", "billete_0001"]
        for i, (nombre, ruta) in enumerate(zip(self.nombres, self.rutas)):
            self.ivf.HEAP.insert([i, nombre, ruta])

    def tearDown(self):
        # Eliminar archivos generados
        for f in [self.data_file_name, self.index_file_name]:
            if os.path.exists(f):
                os.remove(f)

    def test_insert_and_heap(self):
        # Insertar imágenes al índice usando la posición en el heap principal
        for pos in range(len(self.rutas)):
            self.ivf.insert(pos)
        # Verificar que el heap del índice tiene los registros
        registros = self.ivf.index_heap._select_all()
        self.assertEqual(len(registros), len(self.rutas))
        for reg, nombre in zip(registros, self.nombres):
            self.assertIn(nombre, reg[1])

    def test_knn_search(self):
        # Insertar todas las imágenes primero
        for pos in range(len(self.rutas)):
            self.ivf.insert(pos)
        # Buscar vecinos más cercanos para la primera imagen
        resultados = self.ivf.knn_search(0, k=2)
        # Debe retornar una lista de posiciones (enteros)
        self.assertIsInstance(resultados, list)
        self.assertTrue(all(isinstance(p, int) for p in resultados))
        # La posición de la imagen consultada no debe estar en los resultados
        self.assertNotIn(0, resultados)

    def test_mostrar_heap(self):
        # Insertar imágenes y mostrar el heap
        for pos in range(len(self.rutas)):
            self.ivf.insert(pos)
        # Solo verifica que no lanza excepción
        self.ivf.mostrar_heap(max_registros=2)

if __name__ == "__main__":
    unittest.main()
