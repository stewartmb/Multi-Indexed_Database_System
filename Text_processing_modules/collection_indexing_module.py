import os
import csv
import json
import sys
import math
import contextlib
import time
from Text_processing_modules.preprocessing_module import preprocess, preprocess_batch


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Hash_struct.Hash import Hash
from Spimi_struct.Spimi import Spimi
from Utils.file_format import table_filename


class TextCollectionIndexer:
    """
    Esta clase maneja:
    - Carga de datos CSV y preprocesamiento
    - Construcción de vocabulario
    - Indexación de registros basada en hash
    - Construcción de índice invertido SPIMI
    - Precomputación de IDF
    - Cálculo de vectores TF-IDF y generación de metadata en disco con estos vectores
    """
    
    def __init__(self, csv_file_path, collection_name, table_format, text_column, output_base_path, 
                 key_column=None, encoding='latin-1', max_records=None, language='english',
                 use_absolute_path=False):
        """
        Inicializa el indexador de documentos.
        
        Args:
            csv_file_path (str): Ruta al archivo CSV
            collection_name (str): Nombre de la colección (usado para carpetas y archivos)
            table_format (dict): Diccionario definiendo el formato para cada columna en formato struct
                                Ejemplo: {'id': '32s', 'text': '512s', 'rating': 'i'}
            text_column (str): Nombre de la columna que contiene los documentos textuales a indexar
            output_base_path (str): Ruta base donde se creará la carpeta de la colección
            key_column (str, opcional): Columna a usar como clave primaria. Si es None, usa la primera columna
            encoding (str): Codificación del archivo CSV (por defecto: 'latin-1')
            max_records (int, opcional): Número máximo de registros a procesar. Si es None, procesa todos
            language (str): Idioma para el preprocesamiento (por defecto: 'english')
            use_absolute_path (bool): Si True, usa ruta absoluta; si False, usa ruta relativa (por defecto: False)
        """
        self.csv_file_path = csv_file_path
        self.collection_name = collection_name
        self.table_format = table_format
        self.text_column = text_column
        self.output_base_path = output_base_path
        self.key_column = key_column
        self.encoding = encoding
        self.max_records = max_records
        self.language = language
        self.use_absolute_path = use_absolute_path
        
        # Guardar directorio inicial del usuario
        self.original_dir = os.getcwd()
        
        # Crear directorio de salida
        if use_absolute_path:
            # Usar ruta absoluta
            self.output_dir = os.path.abspath(os.path.join(output_base_path, collection_name))
        else:
            # Usar ruta relativa desde el directorio original
            self.output_dir = os.path.join(self.original_dir, output_base_path, collection_name)
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.records = {}
        self.vocab_dict = {}
        self.vocab_next_idx = 0
        self.idf_dict = {}
        
    def load_and_preprocess_data(self):
        """Cargar datos CSV y preprocesar documentos textuales."""
        # Resolver ruta del CSV desde el directorio original
        csv_path = os.path.join(self.original_dir, self.csv_file_path) if not os.path.isabs(self.csv_file_path) else self.csv_file_path
        print(f"[STATUS] Cargando y preprocesando registros desde {csv_path}")
        
        with open(csv_path, newline='', encoding=self.encoding) as csvfile:
            reader = csv.DictReader(csvfile)

            # positions = []

            self.record_hash = None
            
            # Determinar columna clave
            if self.key_column is None:
                self.key_column = reader.fieldnames[0]
                self.record_hash = Hash(
                    table_format=self.table_format,
                    key=self.key_column,
                    data_file_name=table_filename(self.collection_name),
                    buckets_file_name=os.path.join(self.output_dir, f'{self.collection_name}_buckets.bin'),
                    index_file_name=os.path.join(self.output_dir, f'{self.collection_name}_index.bin'),
                    force_create=False
                )
            
            # Cargar registros
            for i, row in enumerate(reader):
                if self.max_records and i >= self.max_records:
                    break

                record_id = row[self.key_column]
                record = {}
                
                # Almacenar todas las columnas
                for column in reader.fieldnames:
                    record[column] = row[column]
                
                self.records[record_id] = record

                # if self.record_hash is not None:
                #     pos = self.record_hash.insert(row)
                #     positions.append(pos)
            

        
        print(f"[STATUS] Total de registros cargados: {len(self.records)}")
        
        # Preprocesamiento por lotes de documentos textuales
        print("[STATUS] Preprocesamiento por lotes de documentos textuales...")
        texts = [record[self.text_column] for record in self.records.values()]
        all_bows = preprocess_batch(texts, lang=self.language)
        
        # Asignar BOWs a cada registro
        record_ids = list(self.records.keys())
        for i, record_id in enumerate(record_ids):
            self.records[record_id]['bow'] = all_bows[i]

        # return positions

    
    def build_vocabulary(self):
        """Construir vocabulario a partir de todos los documentos procesados."""
        print("[STATUS] Construyendo vocabulario...")
        
        for record in self.records.values():
            for term in record['bow']:
                if term not in self.vocab_dict:
                    self.vocab_dict[term] = self.vocab_next_idx
                    self.vocab_next_idx += 1
        
        print(f"[STATUS] Tamaño del vocabulario: {len(self.vocab_dict)}")
    
    def create_record_hash(self): # TODO: CAMBIAR A HEAP
        """Crear tabla hash para almacenamiento de registros."""
        print("[STATUS] Creando tabla hash de registros...")
        
        self.record_hash = Hash(
            table_format=self.table_format,
            key=self.key_column,
            data_file_name=table_filename(self.collection_name),
            buckets_file_name=os.path.join(self.output_dir, f'{self.collection_name}_buckets.bin'),
            index_file_name=os.path.join(self.output_dir, f'{self.collection_name}_index.bin'),
            force_create=False
        )

        positions = []
        
        # Insertar registros en el hash
        for i, record in enumerate(self.records.values(), 1):
            # Preparar registro para inserción basado en el formato de tabla
            hash_record = []
            for field_name, field_format in self.table_format.items():
                value = record[field_name]
                
                # Manejar diferentes tipos de datos basado en el formato
                if field_format.endswith('s'):  # Formato string
                    max_len = int(field_format[:-1])
                    hash_record.append(str(value)[:max_len])
                elif field_format == 'i':  # Formato integer
                    hash_record.append(int(value) if value.isdigit() else 0)
                elif field_format == 'f':  # Formato float
                    hash_record.append(float(value) if value.replace('.', '').isdigit() else 0.0)
                else:
                    hash_record.append(value)
            
            pos = self.record_hash.insert(hash_record)
            print(f"POSITIONS {pos}")
            positions.append(pos)
            
            if i % 100 == 0 or i == len(self.records):
                print(f"[STATUS] Insertados {i}/{len(self.records)} registros en el hash.")
        return positions
    
    def persist_vocabulary(self):
        """Persistir vocabulario en tabla hash."""
        print("[STATUS] Persistiendo vocabulario...")
        
        vocab_hash = Hash(
            table_format={'term': '32s', 'idx': 'i'},
            key='term',
            data_file_name=os.path.join(self.output_dir, f'{self.collection_name}_vocab_data.bin'),
            buckets_file_name=os.path.join(self.output_dir, f'{self.collection_name}_vocab_buckets.bin'),
            index_file_name=os.path.join(self.output_dir, f'{self.collection_name}_vocab_index.bin'),
            force_create=False
        )
        
        for term, idx in self.vocab_dict.items():
            vocab_hash.insert([term, idx])
    
    def create_spimi_index(self):
        """Crear índice invertido SPIMI."""
        print("[STATUS] Creando índice invertido SPIMI...")
        
        self.spimi = Spimi(
            feature_docs_hash_file_name=os.path.join(self.output_dir, f'{self.collection_name}_fd'),
            feature_df_hash_file_name=os.path.join(self.output_dir, f'{self.collection_name}_fc'),
            header_file_name=os.path.join(self.output_dir, f'{self.collection_name}_spimi_header.bin')
        )
        
        # Insertar documentos en SPIMI
        for i, (record_id, record) in enumerate(self.records.items(), 1):
            print(f"[STATUS] Insertando registro {i}/{len(self.records)} en SPIMI...")
            self.spimi.insert(list(record['bow'].keys()), record_id)
    
    def precompute_idfs(self):
        """Precomputar valores IDF para todos los términos."""
        print("[STATUS] Precomputando valores IDF...")
        
        for term in self.vocab_dict:
            self.idf_dict[term] = self.spimi.get_feature_idf(term)
    
    def calculate_vectors_and_metadata(self):
        """Calcular vectores TF-IDF y generar archivos de metadata."""
        print("[STATUS] Calculando vectores TF-IDF y generando metadata...")
        
        for i, (record_id, record) in enumerate(self.records.items(), 1):
            tf_vector = []
            weight_vector = []
            bow = record['bow']
            
            for term, count in bow.items():
                tf_val = math.log10(1 + count)  # Fórmula TF
                weight = tf_val * self.idf_dict[term]  # Peso TF-IDF
                term_idx = self.vocab_dict[term]  # Índice del término
                
                tf_vector.append([term_idx, tf_val])
                weight_vector.append([term_idx, weight])
            
            # Crear metadata
            metadata = {
                'record_id': record_id,
                'terms': bow,
                'tf_vector': tf_vector,
                'weight_vector': weight_vector,
            }
            
            # Guardar metadata en archivo
            print(self.output_dir)
            meta_file = os.path.join(self.output_dir, f'{self.collection_name}_{record_id}_metadata.json')
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"[STATUS] Metadata guardada para registro {i}/{len(self.records)}")
    
    def process(self):
        """Ejecutar el proceso completo de indexación."""
        print(f"[STATUS] Iniciando proceso de indexación para colección: {self.collection_name}")
        print(f"[STATUS] Directorio de salida: {self.output_dir}")
        
        # Paso 1: Cargar y preprocesar datos
        self.load_and_preprocess_data()
        
        # Paso 2: Construir vocabulario
        self.build_vocabulary()
        
        # Paso 3: Crear hash de registros
        positions = self.create_record_hash()
        
        # Paso 4: Persistir vocabulario
        self.persist_vocabulary()
        
        # Paso 5: Crear índice SPIMI
        self.create_spimi_index()
        
        # Paso 6: Precomputar IDFs
        self.precompute_idfs()
        
        # Paso 7: Calcular vectores y generar metadata
        self.calculate_vectors_and_metadata()
        
        print(f"[STATUS] Proceso de indexación completado. Archivos generados en: {self.output_dir}")

        print(positions)
        return positions


def main():
    """
    Ejemplo de uso del TextCollectionIndexer.
    
    Este ejemplo muestra cómo usar el indexador con diferentes tipos de colecciones.
    """
    
    # Ejemplo : Reviews de Disney 
    disney_indexer = TextCollectionIndexer(
        csv_file_path='DisneylandReviews.csv',
        collection_name='disneyland_reviews',
        table_format={
            'id': '32s',
            'rating': 'i',
            'year_month': '16s',
            'location': '32s',
            'review': '512s',
            'branch': '16s'
        },
        text_column='review', # MISMO NOMBRE QUE EN EL CSV
        output_base_path='Schema/collections',
        key_column='id',
        max_records=100,
        use_absolute_path=False  # Usar ruta relativa
    )
    
    # Procesar reviews de Disney
    disney_indexer.process()

if __name__ == "__main__":
    main()