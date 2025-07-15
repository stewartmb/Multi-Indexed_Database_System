import math
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from Utils.Registro import *
from Heap_struct.Heap import *
from Hash_struct.Hash import *

class Spimi:
    """
    Inicializa el SPIMI.
    :param feature_docs_hash_file_name: nombre del archivo hash principal de referencias a un feature
    :param feature_df_hash_file_name: nombre del archivo hash principal de conteo de features en docs (df)
    """
    def __init__(self,
                 feature_docs_hash_file_name: str,
                 feature_df_hash_file_name: str,
                 max_feature_length: int = 64,
                 header_file_name: str = "spimi_header.bin"):
        
        """ Crear archivos de hash para documentos y hash para df de features."""

        fd_files = self._make_hash_filenames("term_doc", feature_docs_hash_file_name)
        fc_files = self._make_hash_filenames("term_df", feature_df_hash_file_name)

        """ El archivo de cabecera que contiene el número total de documentos."""

        self.header_file_name = header_file_name
        self._init_header_file()

        """ Inicializa los archivos de hash para documentos y df de features.
        Estructura de los archivos:
        - feature_docs_hash: {encoded_feature: str, filepath: str}
        - feature_df_hash: {encoded_feature: str, df: int}
        """

        encoded_feature_format = f"{max_feature_length}s"

        self.feature_docs_hash = Hash(
        table_format={"encoded_feature": encoded_feature_format, "filepath": "32s"},
        key="encoded_feature",
        data_file_name=fd_files["data_file_name"],
        buckets_file_name=fd_files["buckets_file_name"],
        index_file_name=fd_files["index_file_name"],
        global_depth=4,
        force_create=False
        )

        self.feature_df_hash = Hash(
            table_format={"encoded_feature": encoded_feature_format, "df": "i"},
            key="encoded_feature",
            data_file_name=fc_files["data_file_name"],
            buckets_file_name=fc_files["buckets_file_name"],
            index_file_name=fc_files["index_file_name"],
            global_depth=4,
            force_create=False
        )

    def _make_hash_filenames(self, suffix: str, base: str):
        """
        Helper para generar nombres de los hash struct files.
        Eejemplo: prefix='fd_doc', base='myfile' -> 
            fd_doc_myfile_data.bin, fd_doc_myfile_buckets.bin, fd_doc_myfile_index.bin
        """
        return {
            "data_file_name":   f"{base}_{suffix}_data.bin",
            "buckets_file_name":f"{base}_{suffix}_buckets.bin",
            "index_file_name":  f"{base}_{suffix}_index.bin"
        }
    
    def _init_header_file(self):
        """Crea el archivo de cabecera si no existe, inicializando num_docs en 0."""
        if not os.path.exists(self.header_file_name):
            with open(self.header_file_name, "wb") as f:
                f.write(struct.pack("i", 0))  # 4 bytes para un entero

    def get_num_docs(self):
        """Lee el número total de documentos del archivo de cabecera."""
        with open(self.header_file_name, "rb") as f:
            return struct.unpack("i", f.read(4))[0]

    def set_num_docs(self, value):
        """Actualiza el número total de documentos en el archivo de cabecera."""
        with open(self.header_file_name, "wb") as f:
            f.write(struct.pack("i", value))
    

    def insert(self, encoded_features_list, document_name):
        """
        Inserta un registro en el SPIMI.
        :param record: lista de features asociados a un documento.
        :param document_name: nombre del documento que posee los features.
        """ 
        num_docs = self.get_num_docs() + 1
        self.set_num_docs(num_docs)

        for encoded_feature in encoded_features_list:
            self.feature_docs_hash.insert([encoded_feature, document_name])

            pos_list = self.feature_df_hash.search(encoded_feature)
            if pos_list:
                reg = self.feature_df_hash.HEAP.read(pos_list[0])
                current_df = reg[1]

                self.feature_df_hash.delete(encoded_feature)
                self.feature_df_hash.insert([encoded_feature, current_df + 1])
            else:  
                self.feature_df_hash.insert([encoded_feature, 1])

    def get_feature_count(self, encoded_feature):
        """
        Obtiene el conteo de en cuantos docs aparece un feature en docs (sin repeticion),
        osea el df de un feature.
        :param encoded_feature: feature a buscar
        :return: conteo del feature o None si no se encuentra
        """
        pos_list = self.feature_df_hash.search(encoded_feature)

        if pos_list:
            reg = self.feature_df_hash.HEAP.read(pos_list[0])
            current_df = reg[1] 
            
            return current_df
        return None
    
    def get_feature_idf(self, encoded_feature):
        """ Calcula el IDF de un feature.
        :param encoded_feature: feature a buscar
        :return: IDF del feature o 0.0 si no se encuentra
        """
        df = self.get_feature_count(encoded_feature)
        if df is None:
            return 0.0
        total_docs = self.get_num_docs()
        if total_docs == 0 or df == 0:
            return 0.0
        return math.log10(total_docs / df)
    
    def get_documents_with_feature(self, encoded_feature):
        """
        Obtiene los documentos que contienen un feature.
        :param encoded_feature: feature a buscar
        :return: lista de nombres de documentos que contienen el feature
        """
        pos_list = self.feature_docs_hash.search(encoded_feature)
        if pos_list:
            registros = [self.feature_docs_hash.HEAP.read(pos) for pos in pos_list]
            return [reg[1] for reg in registros]
        return []

    def delete_feature(self, encoded_feature):
        """ Elimina un feature y sus referencias de documentos.
        :param encoded_feature: feature a eliminar
        """
        pos_list = self.feature_docs_hash.search(encoded_feature)
        while pos_list != []:
            self.feature_docs_hash.delete(encoded_feature)
            pos_list = self.feature_docs_hash.search(encoded_feature)
            
        self.feature_df_hash.delete(encoded_feature)
            
