import unittest
import os
import sys
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Spimi import Spimi


class TestSpimi(unittest.TestCase):
    def setUp(self):
        # Nombres de archivos temporales para el hash de features y conteo
        self.fd_file = "test_fd"
        self.fc_file = "test_fc"
        # Inicializar SPIMI
        self.spimi = Spimi(self.fd_file, self.fc_file)

    def tearDown(self):
        files = [
            #-- Archivos de prueba con datoss
            "test_fd_term_doc_data.bin",
            "test_fd_term_doc_buckets.bin",
            "test_fd_term_doc_index.bin",
            "test_fc_term_df_data.bin",
            "test_fc_term_df_buckets.bin",
            "test_fc_term_df_index.bin",
            #-- Archivos de prueba vacíos
            "empty_fd_term_doc_data.bin",
            "empty_fd_term_doc_buckets.bin",
            "empty_fd_term_doc_index.bin",
            "empty_fc_term_df_data.bin",
            "empty_fc_term_df_buckets.bin",
            "empty_fc_term_df_index.bin",
            #-- Archivos de encabezado
            "spimi_header.bin",
            "empty_spimi_header.bin"
        ]

        for f in files:
            if os.path.exists(f):
                os.remove(f)

    def test_get_feature_idf(self):
        """Prueba el cálculo correcto del IDF para características existentes/inexistentes."""
        # Insertar documentos de prueba
        self.spimi.insert(["apple", "banana"], "doc1.txt")
        self.spimi.insert(["apple", "orange"], "doc2.txt")
        self.spimi.insert(["banana"], "doc3.txt")

        """# de documentos:", self.spimi.get_document_count())"""
        # Verificar IDFs
        self.assertAlmostEqual(
            self.spimi.get_feature_idf("apple"),
            math.log10(3/2),  # 3 docs total, 2 con "apple"
            places=5
        )
        self.assertAlmostEqual(
            self.spimi.get_feature_idf("banana"),
            math.log10(3/2),  # 3 docs, 2 con "banana"
            places=5
        )
        self.assertAlmostEqual(
            self.spimi.get_feature_idf("orange"),
            math.log10(3/1),  # 3 docs, 1 con "orange"
            places=5
        )
        self.assertEqual(
            self.spimi.get_feature_idf("mango_radioactivo"),
            0.0  # Característica inexistente
        )
        
        # Caso especial: sin documentos
        empty_spimi = Spimi("empty_fd", "empty_fc",header_file_name="empty_spimi_header.bin")
        self.assertEqual(
            empty_spimi.get_feature_idf("apple"),
            0.0  # No hay documentos en el índice
        )

if __name__ == "__main__":
    unittest.main()