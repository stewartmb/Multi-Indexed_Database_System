import unittest
import os
from Hash import Hash  # Reemplazar con el nombre real del archivo


class TestHash(unittest.TestCase):
    def setUp(self):
        self.format = {"nombre": "12s", "edad": "i", "altura": "d"}
        self.key = "edad"
        self.hash = Hash(
            table_format=self.format,
            key=self.key,
            data_file_name="hash_test_data.bin",
            buckets_file_name="hash_test_buckets.bin",
            index_file_name="hash_test_index.bin",
            global_depth=4,
            force_create=True
        )

        # Insertar registros
        self.hash.insert(["Pepe", 18, 123.12])     # Pos 0
        self.hash.insert(["Juan", 19, 764.46])     # Pos 1
        self.hash.insert(["Lucas", 18, 925.34])    # Pos 2
        self.hash.insert(["Alfonso", 18, 585.21])  # Pos 3
        self.hash.insert(["Estefano", 20, 468.83]) # Pos 4
        self.hash.insert(["Carlos", 19, 875.27])   # Pos 5

    def tearDown(self):
        # Eliminar archivos generados
        for f in ["hash_test_data.bin", "hash_test_buckets.bin", "hash_test_index.bin"]:
            if os.path.exists(f):
                os.remove(f)

    def test_search_positions(self):
        positions = self.hash.search(18)
        registros = [self.hash.HEAP.read(pos) for pos in positions]
        self.assertEqual(len(registros), 3)
        for r in registros:
            self.assertEqual(r[1], 18)

    def test_range_search_positions(self):
        positions = self.hash.range_search(18, 19)
        registros = [self.hash.HEAP.read(pos) for pos in positions]
        self.assertEqual(len(registros), 5)
        for r in registros:
            self.assertIn(r[1], [18, 19])

    def test_delete_removes_position(self):
        # Confirmar que existe
        pos_list = self.hash.search(20)
        self.assertGreater(len(pos_list), 0)
        self.hash.delete(20)

        # Confirmar que ya no existe
        pos_list = self.hash.search(20)
        self.assertEqual(pos_list, [])

        range_pos = self.hash.range_search(20, 25)
        registros = [self.hash.HEAP.read(p) for p in range_pos]
        self.assertTrue(all(r[1] != 20 for r in registros))