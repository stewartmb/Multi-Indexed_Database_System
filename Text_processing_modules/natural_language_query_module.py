import json
import os
import math
import sys
import time
from pathlib import Path
from preprocessing_module import preprocess

# Agregar el directorio padre para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Hash_struct.Hash import Hash
from Spimi_struct.Spimi import Spimi

class NLQueryModule:
    """Sistema de consultas por similitud coseno"""
    
    def __init__(self, collection_path, collection_name, key_column=None, table_format=None):
        """
        Inicializar el sistema de consultas
        
        Args:
            collection_path: Ruta a la carpeta con los índices
            collection_name: Nombre de la colección (requerido)
            table_format: Formato de tabla para los documentos (opcional)
        """
        self.collection_path = Path(collection_path)
        self.collection_name = collection_name
        self.key_column = key_column

        # Formato de tabla por defecto para reviews de Disney
        self.table_format = table_format or {
            'Review_ID': '32s', 'Rating': 'i', 
            'Year_Month': '16s', 'Reviewer_Location': '32s',
            'Review_Text': '512s', 'Branch': '16s'
        }
        
        # Estructuras de datos
        self.vocab_hash = None
        self.spimi = None
        self.review_hash = None
        self.total_docs = 0
        
        # Cargar estructuras
        self._cargar_estructuras()
    
    def _cargar_estructuras(self):
        """Cargar todas las estructuras de datos desde disco"""
        try:
            self._cargar_vocabulario()
            self._cargar_spimi()
            self._cargar_documentos()
            self.total_docs = self.spimi.get_num_docs()
        except Exception as e:
            raise Exception(f"Error cargando estructuras: {e}")
    
    def _cargar_vocabulario(self):
        """Cargar hash del vocabulario"""
        self.vocab_hash = Hash(
            table_format={'term': '32s', 'idx': 'i'},
            key='term',
            data_file_name=str(self.collection_path / f'{self.collection_name}_vocab_data.bin'),
            buckets_file_name=str(self.collection_path / f'{self.collection_name}_vocab_buckets.bin'),
            index_file_name=str(self.collection_path / f'{self.collection_name}_vocab_index.bin'),
            force_create=False
        )
    
    def _cargar_spimi(self):
        """Cargar estructura SPIMI"""
        self.spimi = Spimi(
            feature_docs_hash_file_name=str(self.collection_path / f'{self.collection_name}_fd'),
            feature_df_hash_file_name=str(self.collection_path / f'{self.collection_name}_fc'),
            header_file_name=str(self.collection_path / f'{self.collection_name}_spimi_header.bin')
        )
    
    def _cargar_documentos(self):
        """Cargar hash de documentos"""
        self.review_hash = Hash(
            table_format=self.table_format,
            key=self.key_column,  # Usar primera columna como key
            data_file_name=str(self.collection_path / f'{self.collection_name}_data.bin'),
            buckets_file_name=str(self.collection_path / f'{self.collection_name}_buckets.bin'),
            index_file_name=str(self.collection_path / f'{self.collection_name}_index.bin'),
            force_create=False
        )
    
    def _preprocesar_consulta(self, query):
        """
        Preprocesar la consulta y crear vector TF-IDF
        
        Args:
            query: Texto de la consulta
            
        Returns:
            tuple: (vector_consulta, terminos_validos)
        """
        # Preprocesar consulta
        q_bow = preprocess(query, lang='english')
        # Construir vector de consulta
        q_vector = {}
        valid_terms = set()

        for term, count in q_bow.items():
            # Buscar término en vocabulario
            pos_list = self.vocab_hash.search(term)
            if not pos_list:
                continue
            
            # Obtener índice del término
            reg = self.vocab_hash.HEAP.read(pos_list[0])
            term_idx = reg[1]
            
            # Obtener frecuencia de documento (DF)
            df = self.spimi.get_feature_count(term)
            if not df:
                continue
            
            # Calcular peso TF-IDF
            tf = math.log10(1 + count)
            idf = math.log10(self.total_docs / df)
            weight = tf * idf
            
            q_vector[term_idx] = weight
            valid_terms.add(term)
        
        return q_vector, valid_terms
    
    def _obtener_documentos_candidatos(self, terms):
        candidate_docs = set()
        
        for term in terms:
            try:
                postings = self.spimi.get_documents_with_feature(term)
                candidate_docs.update(postings)
            except Exception:
                continue
        
        return candidate_docs
    
    def _calcular_similitud(self, q_vector, doc_id):
        """
        Calcular similitud coseno entre consulta y documento
        
        Args:
            q_vector: Vector de consulta
            doc_id: ID del documento
            
        Returns:
            float: Similitud coseno
        """
        # Cargar metadata del documento
        meta_path = self.collection_path / f"{self.collection_name}_{doc_id}_metadata.json"
        
        if not meta_path.exists():
            return 0.0
        
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            # Construir vector del documento
            d_vector = {}
            for item in meta['weight_vector']:
                d_vector[item[0]] = item[1]
            
            # Calcular producto punto
            dot_product = 0.0
            for term_idx, weight in q_vector.items():
                if term_idx in d_vector:
                    dot_product += weight * d_vector[term_idx]
            
            # Calcular normas
            q_norm = math.sqrt(sum(w**2 for w in q_vector.values()))
            d_norm = math.sqrt(sum(w**2 for w in d_vector.values()))
            
            # Calcular similitud coseno
            if q_norm * d_norm == 0:
                return 0.0
            else:
                return dot_product / (q_norm * d_norm)
                
        except Exception:
            return 0.0
    
    def _obtener_registro_documento(self, doc_id):
        """
        Obtener registro completo del documento
        
        Args:
            doc_id: ID del documento
            
        Returns:
            tuple: Registro del documento o None si no se encuentra
        """
        positions = self.review_hash.search(doc_id)
        if positions:
            # Como mencionas que solo habrá un registro, tomamos el primero
            registro = self.review_hash.HEAP.read(positions[0])
            return registro
        else:
            return None
    
    def query(self, query_text, k=5):
        """
        Procesar consulta y devolver top-k resultados
        
        Args:
            query_text: Texto de la consulta
            k: Número de resultados a devolver
            
        Returns:
            list: Lista de resultados ordenados por similitud
                  Cada resultado contiene: {'id': str, 'score': float, 'document': tuple}
        """
        # Preprocesar consulta
        q_vector, valid_terms = self._preprocesar_consulta(query_text)
        if not q_vector:
            return []
        
        # Obtener documentos candidatos
        candidate_docs = self._obtener_documentos_candidatos(valid_terms)

        if not candidate_docs:
            return []
        
        # Calcular similitudes
        scores = []
        for doc_id in candidate_docs:
            similarity = self._calcular_similitud(q_vector, doc_id)
            if similarity > 0:
                scores.append((doc_id, similarity))
        
        # Ordenar por similitud descendente
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Seleccionar top-k
        top_k = scores[:k]
        
        # Obtener registros de los documentos
        results = []
        for doc_id, score in top_k:
            registro = self._obtener_registro_documento(doc_id)
            if registro:
                results.append({
                    'id': doc_id,
                    'score': score,
                    'record': registro
                })
        
        return results
    
    def get_total_docs(self):
        return self.total_docs
    
    def get_collection_info(self):
        return {
            'collection_name': self.collection_name,
            'collection_path': str(self.collection_path),
            'total_documents': self.total_docs,
            'vocab_loaded': self.vocab_hash is not None,
            'spimi_loaded': self.spimi is not None,
            'documents_loaded': self.review_hash is not None
        }


# Ejemplo de uso del módulo
if __name__ == "__main__":
    try:
        # Inicializar sistema con una colección de ejemplo
        system = NLQueryModule(
            collection_path="collections/disneyland_reviews",
            collection_name="disneyland_reviews",
            key_column='Review_ID',
            table_format={
            'Review_ID': '32s',
            'Rating': 'i',
            'Year_Month': '16s',
            'Reviewer_Location': '32s',
            'Review_Text': '512s',
            'Branch': '16s'
            }
        )
        
        # Mostrar información del sistema
        info = system.get_collection_info()
        print(f"Colección: {info['collection_name']}")
        print(f"Total documentos: {info['total_documents']}")
        print(f"Ruta: {info['collection_path']}")
        print("-" * 50)
        
        # Realizar múltiples consultas de ejemplo
        consultas = [
            "disneyland was awesome",
            "food quality disney",
            "best experience ever"
        ]

        for consulta in consultas:
            print(f"\nConsulta: '{consulta}'")
            print("=" * 40)
            # Procesar consulta
            results = system.query(consulta, k=3)
            
            if not results:
                print("No se encontraron resultados.")
            else:
                for i, result in enumerate(results, 1):
                    print(f"#{i} [Score: {result['score']:.4f}]")
                    print(f"ID: {result['id']}")
                    # Ahora result['document'] es directamente el registro (tuple)
                    registro = result['record']
                    print(f"Review_ID: {registro[0]}")
                    print(f"Rating: {registro[1]}")
                    print(f"Year_Month: {registro[2]}")
                    print(f"Reviewer_Location: {registro[3]}")
                    print(f"Review_Text: {registro[4][:100]}...")  # Primeros 100 caracteres
                    print(f"Branch: {registro[5]}")
                    print("-" * 30)
    
    except Exception as e:
        import traceback
        print("Error:")
        traceback.print_exc()