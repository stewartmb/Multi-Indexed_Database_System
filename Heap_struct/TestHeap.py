import unittest
import os
import sys
import struct
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *
from Heap import Heap
import unittest


class TestHeap(unittest.TestCase):
    def setUp(self):
        # Diccionario de formato: id (int), name (string de 10), activo (bool como int)
        self.format_dict = {"id": "i", "name": "10s", "activo": "?"}
        self.filename = "test_data.bin"

        # Crear archivo desde cero
        self.heap = Heap(self.format_dict, key="id", data_file_name=self.filename, force_create=True)

    def tearDown(self):
        # Eliminar el archivo al finalizar las pruebas
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_insert_and_read(self):
        pos1 = self.heap.insert([1, "Alice", True])
        pos2 = self.heap.insert([2, "Bob", False])

        r1 = self.heap.read(pos1)
        r2 = self.heap.read(pos2)

        self.assertEqual(r1, [1, "Alice", True])
        self.assertEqual(r2, [2, "Bob", False])

    def test_mark_deleted_and_read(self):
        pos = self.heap.insert([3, "Charlie", True])
        self.assertEqual(self.heap.read(pos), [3, "Charlie", True])

        self.heap.mark_deleted(pos)
        self.assertIsNone(self.heap.read(pos))

    def test_read_out_of_range(self):
        self.assertIsNone(self.heap.read(-1))  # menor que cero
        self.assertIsNone(self.heap.read(100))  # mucho mayor que el número de registros

    def test_select_all(self):
        self.heap.insert([4, "Daniel", True])
        self.heap.insert([5, "Eve", False])
        self.heap.insert([6, "Frank", True])
        self.heap.mark_deleted(1)

        activos = self.heap._select_all()
        self.assertEqual(len(activos), 2)
        self.assertTrue([5, "Eve", False] not in activos)

        todos = self.heap._select_all(include_deleted=True)
        self.assertEqual(len(todos), 3)
