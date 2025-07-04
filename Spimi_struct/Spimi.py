import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from Utils.Registro import *
from Heap_struct.Heap import *
from Hash_struct.Hash import *
from BPtree_struct.Indice_BPTree_file import *


class Spimi:
    def __init__(self,
                 feature_docs_hash_file_name: str,
                 feature_count_hash_file_name: str,):
        """
        Inicializa el SPIMI.
        :param feature_docs_hash_file_name: nombre del archivo hash principal de referencias a un feature
        :param feature_count_hash_file_name: nombre del archivo hash principal de conteo de features
        """
        fd_files = self._make_hash_filenames("fd_doc", feature_docs_hash_file_name)
        fc_files = self._make_hash_filenames("fd_count", feature_count_hash_file_name)

        """ Inicializa el SPIMI con los archivos de hash para documentos y conteo de features.
        Estryctura de los archivos:
        - feature_docs_hash: {encoded_feature: str, filepath: str}
        - feature_count_hash: {encoded_feature: str, count: int}.
        """

        self.feature_docs_hash = Hash(
        table_format={"encoded_feature": "64s", "filepath": "32s"},
        key="encoded_feature",
        data_file_name=fd_files["data_file_name"],
        buckets_file_name=fd_files["buckets_file_name"],
        index_file_name=fd_files["index_file_name"],
        global_depth=4,
        force_create=False
        )

        self.feature_count_hash = Hash(
            table_format={"encoded_feature": "64s", "count": "i"},
            key="encoded_feature",
            data_file_name=fc_files["data_file_name"],
            buckets_file_name=fc_files["buckets_file_name"],
            index_file_name=fc_files["index_file_name"],
            global_depth=4,
            force_create=False
        )

    def _make_hash_filenames(self, prefix: str, base: str):
        """
        Helper para generar nombres de los hash struct files.
        Eejemplo: prefix='fd_doc', base='myfile' -> 
            fd_doc_myfile_data.bin, fd_doc_myfile_buckets.bin, fd_doc_myfile_index.bin
        """
        return {
            "data_file_name":   f"{prefix}_{base}_data.bin",
            "buckets_file_name":f"{prefix}_{base}_buckets.bin",
            "index_file_name":  f"{prefix}_{base}_index.bin"
        }
    

    def insert(self, encoded_features_list, document_name):
        """
        Inserta un registro en el SPIMI.
        :param record: lista de features asociados a un documento.
        :param document_name: nombre del documento que posee los features.
        """       
        for encoded_feature in encoded_features_list:
            self.feature_docs_hash.insert([encoded_feature, document_name])

            pos_list = self.feature_count_hash.search(encoded_feature)
            if pos_list:
                reg = self.feature_count_hash.HEAP.read(pos_list[0])
                current_count = reg[1] 

                self.feature_count_hash.delete(encoded_feature)
                self.feature_count_hash.insert([encoded_feature, current_count + 1])
            else:  
                self.feature_count_hash.insert([encoded_feature, 1])

    def get_feature_count(self, encoded_feature):
        """
        Obtiene el conteo de un feature.
        :param encoded_feature: feature a buscar en BASE64.
        :return: conteo del feature o None si no se encuentra
        """
        pos_list = self.feature_count_hash.search(encoded_feature)

        if pos_list != []:
            reg = self.feature_count_hash.HEAP.read(pos_list[0])
            current_count = reg[1] 
            
            return current_count
        return None
    
    def get_documents_with_feature(self, encoded_feature):
        """
        Obtiene los documentos que contienen un feature.
        :param encoded_feature: feature a buscar en BASE64.
        :return: lista de nombres de documentos que contienen el feature
        """
        pos_list = self.feature_docs_hash.search(encoded_feature)
        if pos_list:
            registros = [self.feature_docs_hash.HEAP.read(pos) for pos in pos_list]
            return [reg[1] for reg in registros]
        return []

    def delete_feature(self, encoded_feature):
        """ Elimina un feature y sus referencias de documentos.
        :param encoded_feature: feature a eliminar en BASE64.
        """
        pos_list = self.feature_docs_hash.search(encoded_feature)
        while pos_list != []:
            self.feature_docs_hash.delete(encoded_feature)
            pos_list = self.feature_docs_hash.search(encoded_feature)
            
        self.feature_count_hash.delete(encoded_feature)