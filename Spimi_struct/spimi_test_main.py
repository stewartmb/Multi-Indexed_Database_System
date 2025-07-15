import unittest
import os
import sys

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
            "test_fd_term_doc_data.bin",
            "test_fd_term_doc_buckets.bin",
            "test_fd_term_doc_index.bin",
            "test_fc_term_df_data.bin",
            "test_fc_term_df_buckets.bin",
            "test_fc_term_df_index.bin",
            "spimi_header.bin"
        ]

        for f in files:
            if os.path.exists(f):
                os.remove(f)

    def test_spimi_insert_and_query(self):
        # Simular features distintos por documento
        # Generar muchos documentos y features textuales
        animal_features = [
            "elephant", "tiger", "lion", "monkey", "giraffe", "zebra", "hippo", "rhino", "leopard", "cheetah",
            "hyena", "buffalo", "antelope", "crocodile", "ostrich", "flamingo", "gorilla", "baboon", "warthog", "meerkat"
        ]
        color_features = [
            "red", "blue", "green", "cyan", "black", "white", "orange", "purple", "pink", "brown"
        ]
        action_features = [
            "run", "jump", "swim", "fly", "climb", "hunt", "sleep", "eat", "drink", "roar"
        ]
        # Crear 10 documentos, cada uno con 10-15 features mezclados
        import random
        random.seed(42)
        doc_features = {}
        for i in range(1, 11):
            feats = random.sample(animal_features, 5) + random.sample(color_features, 3) + random.sample(action_features, 4)
            doc_features[f"doc_{i}.txt"] = feats

        print("\n--- Insertando features sin codificar por documento ---")
        for doc, feats in doc_features.items():
            print(f"Insertando en {doc}: {feats}")
            self.spimi.insert(feats, doc)

        all_features = sorted(set(f for feats in doc_features.values() for f in feats))

        print(f"\nTotal de features únicos: {len(all_features)}")

        print("\n--- Documentos asociados a cada feature (sin codificar) ---")
        for f in all_features:
            docs_with_feature = self.spimi.get_documents_with_feature(f)
            print(f"Feature '{f}' en documentos: {docs_with_feature}")
            expected_docs = [doc for doc, feats in doc_features.items() if f in feats]
            self.assertEqual(set(docs_with_feature), set(expected_docs))

        print("\n--- Eliminando feature y verificando (sin codificar) ---")
        f_del = random.choice(all_features)
        self.spimi.delete_feature(f_del)
        print(f"Eliminado feature '{f_del}'")
        count = self.spimi.get_feature_count(f_del)
        docs_with_feature = self.spimi.get_documents_with_feature(f_del)
        print(f"Tras eliminar: count = {count}, docs = {docs_with_feature}")
        self.assertIsNone(count)
        self.assertEqual(docs_with_feature, [])

if __name__ == "__main__":
    unittest.main()