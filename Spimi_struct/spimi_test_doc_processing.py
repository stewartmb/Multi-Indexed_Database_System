import os
import sys
import json
import math
import unittest
import shutil
from contextlib import contextmanager

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Spimi import Spimi
from Hash_struct.Hash import Hash

class TestSpimiDocumentProcessing(unittest.TestCase):
    documentos_iniciales = {
        "doc1.txt": "hold water run",
        "doc2.txt": "hold line water plant", 
        "doc3.txt": "run fast hold tight"
    }

    nuevo_documento = {"doc4.txt": "plant water grow strong"}

    OUTPUT_DIR = "test_output"
    SPIMI_FD = "mock_fd"
    SPIMI_FC = "mock_fc"

    def setUp(self):
        # Base directory for safety
        self.base_dir = os.getcwd()
        self.output_dir = os.path.join(self.base_dir, self.OUTPUT_DIR)

        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

    @contextmanager
    def in_output_dir(self):
        cwd_anterior = os.getcwd()
        os.chdir(self.output_dir)
        try:
            yield
        finally:
            os.chdir(cwd_anterior)

    def calcular_peso_real(self, term, doc_name, documentos, N):
        doc_text = documentos[doc_name]
        doc_terms = [w.lower() for w in doc_text.split()]
        term_freq = doc_terms.count(term)
        
        tf = math.log10(1 + term_freq) if term_freq > 0 else 0.0
        
        docs_con_termino = sum(
            1 for text in documentos.values() if term in [w.lower() for w in text.split()]
        )
        idf = math.log10(N / docs_con_termino) if docs_con_termino > 0 else 0.0
        
        return tf * idf

    def procesar_documentos(self, documentos, vocab=None, vocab_hash=None, spimi=None, start_idx=0):
        if vocab is None:
            vocab = {}
        if vocab_hash is None:
            vocab_hash = Hash(
                table_format={"term": "32s", "idx": "i"},
                key="term",
                data_file_name="vocab_data.bin",
                buckets_file_name="vocab_buckets.bin",
                index_file_name="vocab_index.bin",
                global_depth=4,
                force_create=True
            )
        if spimi is None:
            spimi = Spimi(
                self.SPIMI_FD,
                self.SPIMI_FC,
                header_file_name="spimi_header.bin"
            )

        vocab_next_idx = start_idx
        for doc_name, text in documentos.items():
            terms = [w.lower() for w in text.split()]
            term_counts = {}
            for t in terms:
                term_counts[t] = term_counts.get(t, 0) + 1
                if t not in vocab:
                    vocab[t] = vocab_next_idx
                    vocab_hash.insert([t, vocab_next_idx])
                    vocab_next_idx += 1
            spimi.insert(list(set(terms)), doc_name)

            meta = {"terms": term_counts}
            meta_file = os.path.join(self.output_dir, doc_name.replace(".txt", "_metadata.json"))
            with open(meta_file, "w") as f:
                json.dump(meta, f, indent=2)

        return vocab, vocab_hash, spimi

    def construir_vectores(self, documentos, vocab, spimi):
        for doc_name in documentos:
            meta_file = os.path.join(self.output_dir, doc_name.replace(".txt", "_metadata.json"))
            with open(meta_file, "r") as f:
                meta = json.load(f)

            tf_vector = []
            weight_vector = []
            for term, idx in vocab.items():
                tf = meta["terms"].get(term, 0)
                tf_val = math.log10(1 + tf) if tf > 0 else 0.0
                idf = spimi.get_feature_idf(term)
                weight = tf_val * idf
                tf_vector.append([idx, tf_val])
                weight_vector.append([idx, weight])

            meta["tf_vector"] = tf_vector
            meta["weight_vector"] = weight_vector
            with open(meta_file, "w") as f:
                json.dump(meta, f, indent=2)

    def leer_vectores(self, doc_name):
        meta_file = os.path.join(self.output_dir, doc_name.replace(".txt", "_metadata.json"))
        with open(meta_file, "r") as f:
            meta = json.load(f)
        return meta["tf_vector"], meta["weight_vector"], meta["terms"]

    def test_tf_idf_real_vs_spimi(self):
        with self.in_output_dir():
            # --- Fase inicial ---
            vocab, vocab_hash, spimi = self.procesar_documentos(self.documentos_iniciales)
            self.construir_vectores(self.documentos_iniciales, vocab, spimi)

            print("\n=== Vector de Pesos: Resultados iniciales de SPIMI vs Cálculo Real ===\n")
            N_inicial = len(self.documentos_iniciales)
            for doc_name in self.documentos_iniciales:
                tf_vector, weight_vector, _ = self.leer_vectores(doc_name)
                for term, idx in vocab.items():
                    peso_spimi = next((peso for i, peso in weight_vector if i == idx), 0.0)
                    peso_real = self.calcular_peso_real(term, doc_name, self.documentos_iniciales, N_inicial)
                    print(f"Doc: {doc_name} Term: '{term}' idx: {idx} -> SPIMI: {peso_spimi:.5f}, Real: {peso_real:.5f}")
                    self.assertAlmostEqual(peso_spimi, peso_real, places=5,
                        msg=f"Peso incorrecto para '{term}' en {doc_name}. SPIMI: {peso_spimi}, Real: {peso_real}")

            # --- Fase de expansión de colección ---
            vocab2, vocab_hash2, spimi2 = self.procesar_documentos(
                self.nuevo_documento, vocab, vocab_hash, spimi, start_idx=len(vocab)
            )

            all_docs = {**self.documentos_iniciales, **self.nuevo_documento}
            self.construir_vectores(all_docs, vocab2, spimi2)

            print("\n=== Vector de pesos: Resultados tras expansión de colección y recalculo ===\n")
            N_final = len(all_docs)
            for doc_name in all_docs:
                tf_vector, weight_vector, _ = self.leer_vectores(doc_name)
                for term, idx in vocab2.items():
                    peso_spimi = next((peso for i, peso in weight_vector if i == idx), 0.0)
                    peso_real = self.calcular_peso_real(term, doc_name, all_docs, N_final)
                    print(f"Doc: {doc_name} Term: '{term}' idx: {idx} -> SPIMI: {peso_spimi:.5f}, Real: {peso_real:.5f}")
                    self.assertAlmostEqual(peso_spimi, peso_real, places=5,
                        msg=f"Peso incorrecto tras expansión para '{term}' en {doc_name}. "
                            f"SPIMI: {peso_spimi}, Real: {peso_real}")

if __name__ == "__main__":
    unittest.main()