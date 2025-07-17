import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Spimi import Spimi

class TestSpimiPersistence(unittest.TestCase):
    def setUp(self):
        self.fd_file = "persist_fd"
        self.fc_file = "persist_fc"

    def tearDown(self):
        files = [
            "persist_fd_term_doc_data.bin",
            "persist_fd_term_doc_buckets.bin",
            "persist_fd_term_doc_index.bin",
            "persist_fc_term_df_data.bin",
            "persist_fc_term_df_buckets.bin",
            "persist_fc_term_df_index.bin",
            "spimi_header.bin"
        ]

        for f in files:
            if os.path.exists(f):
                os.remove(f)

    def test_persistence_and_correctness(self):
        # Primera sesión: insertar algunos documentos
        spimi = Spimi(self.fd_file, self.fc_file)
        docs1 = {
            "doc_a.txt": ["cat", "dog", "fish"],
            "doc_b.txt": ["dog", "bird"],
        }
        for doc, feats in docs1.items():
            spimi.insert(feats, doc)
        # Verificar después de primera inserción
        self.assertEqual(set(spimi.get_documents_with_feature("dog")), {"doc_a.txt", "doc_b.txt"})
        self.assertEqual(spimi.get_feature_count("cat"), 1)
        self.assertEqual(spimi.get_feature_count("dog"), 2)

        # Cerrar (simulado por eliminar referencia)
        del spimi

        # Segunda sesión: reabrir y agregar más documentos
        spimi = Spimi(self.fd_file, self.fc_file)
        docs2 = {
            "doc_c.txt": ["cat", "lion"],
            "doc_d.txt": ["dog", "lion", "fish"],
        }
        for doc, feats in docs2.items():
            spimi.insert(feats, doc)
        # Verificar persistencia y actualización
        self.assertEqual(set(spimi.get_documents_with_feature("cat")), {"doc_a.txt", "doc_c.txt"})
        self.assertEqual(set(spimi.get_documents_with_feature("dog")), {"doc_a.txt", "doc_b.txt", "doc_d.txt"})
        self.assertEqual(spimi.get_feature_count("cat"), 2)
        self.assertEqual(spimi.get_feature_count("dog"), 3)
        self.assertEqual(set(spimi.get_documents_with_feature("lion")), {"doc_c.txt", "doc_d.txt"})
        self.assertEqual(spimi.get_feature_count("lion"), 2)

        # Cerrar y abrir una vez más, insertar otro documento
        del spimi
        spimi = Spimi(self.fd_file, self.fc_file)
        spimi.insert(["cat", "dog", "lion", "tiger"], "doc_e.txt")
        self.assertEqual(set(spimi.get_documents_with_feature("cat")), {"doc_a.txt", "doc_c.txt", "doc_e.txt"})
        self.assertEqual(spimi.get_feature_count("cat"), 3)
        self.assertEqual(set(spimi.get_documents_with_feature("lion")), {"doc_c.txt", "doc_d.txt", "doc_e.txt"})
        self.assertEqual(spimi.get_feature_count("lion"), 3)
        self.assertEqual(set(spimi.get_documents_with_feature("tiger")), {"doc_e.txt"})
        self.assertEqual(spimi.get_feature_count("tiger"), 1)

        # Eliminar un feature y verificar
        spimi.delete_feature("cat")
        self.assertIsNone(spimi.get_feature_count("cat"))
        self.assertEqual(spimi.get_documents_with_feature("cat"), [])

if __name__ == "__main__":
    unittest.main()
