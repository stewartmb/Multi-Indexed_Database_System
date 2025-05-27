import pandas as pd
import os
import sys
import os
import random

# Importar las estructuras de índices
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *
import BPtree_struct.Indice_BPTree_file as BPTREE
import Hash_struct.Hash as HASH
import Sequential_Struct.Indice_Sequential_file as SEQUENTIAL
import Isam_struct.Indice_Isam_file as ISAM 
import Brin_struct.Indice_Brin_file as BRIN
import RTree_struct.RTreeFile_Final as RTREE
import Heap_struct.Heap as HEAP
import time
N = 1000
import csv
KEYS = []
# Lista fija de códigos a usar
# generar todos los códigos aleatorios entre 1 y 100
num = [10000,50000,100000]
x=0
path = f'/Users/stewart/2025-1/BD2/Proyecto_BD2/Data_test'
# path = "C:/Users/Equipo/Documents/2025-1/BD2/proyecto/Proyecto_BD2/Data_test"
data_file = f'Generate_test/data_file{num[x]}.bin'

test_data_full = f'test_data_full{num[x]}.csv'
total_path = os.path.join(path, test_data_full)

csv_times = f'csv_times{num[x]}.csv'

csv_time_search = f'csv_time_search{num[x]}.csv'

table_format = {"timestamp": "24s", "random_int": "i", "name": "20s", "email": "50s", "date": "10s", "price": "d", "latitude": "d", "longitude": "d",  "is_active": "?", "category": "20s"}

Indices_struct = ["heap" , "bptree", "hash", "sequential", "isam", "brin" ,"rtree"]
def destroy_archivos(x):
    """
    Elimina los archivos de datos y de índices generados.
    """
    files_to_remove = [
        f'Generate_test/btree_1_index{num[x]}.bin',
        f'Generate_test/hash_1_index{num[x]}.bin',
        f'Generate_test/hash_2_index{num[x]}.bin',
        f'Generate_test/sequential_1_index{num[x]}.bin',
        f'Generate_test/isam_1_index{num[x]}.bin',
        f'Generate_test/brin_1_index{num[x]}.bin',
        f'Generate_test/brin_2_index{num[x]}.bin',
        f'Generate_test/rtree_1_index{num[x]}.bin',
        f'Generate_test/data_file{num[x]}.bin',
    ]
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print (f"Archivo {file} eliminado.")

class MEGA_SUPER_HIPER_MASTER_INDICE:
    def __init__(self, name_key, table_format , x , num = num , test_global = False):
        self.name_key = name_key
        self.table_format = table_format
        self.x = x
        self.data_file = f'Generate_test/data_file{num[x]}.bin'
        self.Registro = RegistroType(table_format, name_key)
        self.heap = HEAP.Heap(table_format, key = name_key, data_file_name = self.data_file , force_create = False)
        self.bptree = BPTREE.BPTree(table_format, name_key , name_index_file = f'Generate_test/btree_1_index{num[self.x]}.bin', name_data_file = data_file , max_num_child = 25)
        self.hash = HASH.Hash(table_format, name_key, buckets_file_name = f'Generate_test/hash_1_index{num[self.x]}.bin' ,index_file_name = f'Generate_test/hash_2_index{num[self.x]}.bin',data_file_name =data_file, global_depth = 32 ,max_records_per_bucket = 8)
        self.sequential = SEQUENTIAL.Sequential(table_format, name_key, name_index_file = f'Generate_test/sequential_1_index{num[self.x]}.bin',name_data_file = data_file , num_aux =200)
        if test_global:
            self.isam = None
        else:
            self.isam = ISAM.ISAM(table_format, self.name_key , name_index_file = f'Generate_test/isam_1_index{num[self.x]}.bin', name_data_file = self.data_file)
        self.brin = BRIN.BRIN(table_format, name_key , name_index_file = f'Generate_test/brin_1_index{num[self.x]}.bin', name_page_file =  f'Generate_test/brin_2_index{num[self.x]}.bin',name_data_file = data_file , max_num_pages = 20, max_num_keys = 20)
        self.rtree = RTREE.RTreeFile(table_format = table_format, p_key = name_key ,keys = ["latitude", "longitude"] , data_filename = data_file, index_filename = f'Generate_test/rtree_1_index{num[self.x]}.bin')

    def insert_csv(self, csv_path):
        """
        Inserta registros en el ORDEN EXACTO de CODIGOS_A_USAR.
        """
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            registros = list(reader)
            i = 0         
            for row in registros:
                i += 1
                if i % N == 0:
                    print("|", end="")
                key = self.Registro.get_key(row)
                KEYS = []
                KEYS.append(key)
                # manejar errores de formato:
                row = self.Registro.correct_format(row)
                self.heap.insert(row)
            print()
    
    def generate_index(self, index_type ,csv_path ):
        """
        Genera el índice del tipo especificado.
        """
        if  index_type == "heap":
            start_time = time.time()
            self.insert_csv(csv_path)
            end_time = time.time()
            return end_time - start_time 
        elif index_type == "bptree":
            start_time = time.time()
            for i in range(num[x]-1):
                self.bptree.add(pos_new_record = i)
            end_time = time.time()
            return end_time - start_time
        elif index_type == "hash":
            start_time = time.time()
            for i in range(num[x]-1):
                record = self.heap.read(i)
                self.hash.insert(record = record , data_position = i)
            end_time = time.time()
            return end_time - start_time
        elif index_type == "sequential":
            start_time = time.time()
            for i in range(num[x]-1):
                self.sequential.add(pos_new_record = i)
            end_time = time.time()
            return end_time - start_time
        elif index_type == "isam":
            start_time = time.time()
            for i in range(num[x]-1):
                self.isam = ISAM.ISAM(table_format, self.name_key , name_index_file = f'Generate_test/isam_1_index{num[x]}.bin', name_data_file = self.data_file)
            end_time = time.time()
            return end_time - start_time
        elif index_type == "brin":
            start_time = time.time()
            for i in range(num[x]-1):
                self.brin.add(pos_new_record = i)
            end_time = time.time()
            return end_time - start_time
        elif index_type == "rtree":
            start_time = time.time()
            for i in range(num[x]-1):
                record = self.heap.read(i)
                self.rtree.insert(record = record, record_pos = i)
            end_time = time.time()
            return end_time - start_time
    
    def generate_test_data(self, path, csv_times, Indices_struct,x):
        """
        Genera un archivo CSV con datos de prueba.
        Si el archivo ya existe, añade una nueva fila.
        """
        print (f"Generando datos de prueba ...")
        destroy_archivos(x) 
        diccionario_tiempos = {}
        for struct in Indices_struct:
            temp = MEGA_SUPER_HIPER_MASTER_INDICE(name_key = "timestamp", table_format = table_format, x = x , test_global = True)
            time = temp.generate_index(struct, csv_path=path)
            diccionario_tiempos[struct] = time
            print(f"Tiempo de creación del índice {struct}: {time:.2f} segundos")
        df = pd.DataFrame(diccionario_tiempos, index=[0])
        # Si el archivo existe, añade la fila sin encabezado
        if os.path.exists(csv_times):
            df.to_csv(csv_times, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_times, index=False)
    
    def search(self, key , key_type ,key_rtree ):
        """
        Realiza una búsqueda de los keys especificados y guarda los tiempos en un CSV.
        """
        if key_type == "heap":
            start_time = time.time()
            self.heap.search(key,key)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "bptree":
            start_time = time.time()
            self.bptree.search(key)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "hash":
            start_time = time.time()
            self.hash.search(key)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "sequential":
            start_time = time.time()
            self.sequential.search(key)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "isam":
            start_time = time.time()
            self.isam.search(key)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "brin":
            start_time = time.time()
            self.brin.search(key)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "rtree":
            start_time = time.time()
            self.rtree.search(key_rtree)
            end_time = time.time()
            return end_time - start_time
        
    def search_range(self, key_start, key_end, key_type , rtree_left , rtree_right):
        """
        Realiza una búsqueda de un rango de keys especificados y guarda los tiempos en un CSV.
        """
        if key_type == "heap":
            start_time = time.time()
            self.heap.search(key_start, key_end)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "bptree":
            start_time = time.time()
            self.bptree.search_range(key_start, key_end)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "hash":
            start_time = time.time()
            self.hash.range_search(key_start, key_end)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "sequential":
            start_time = time.time()
            self.sequential.search_range(key_start, key_end)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "isam":
            start_time = time.time()
            self.isam.search_range(key_start, key_end)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "brin":
            start_time = time.time()
            self.brin.search_range(key_start, key_end)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "rtree_point_to_point":
            start_time = time.time()
            self.rtree.range_search(rtree_left, rtree_right)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "rtree_knn":
            start_time = time.time()
            self.rtree.ksearch( k=10 , query = rtree_left)
            end_time = time.time()
            return end_time - start_time
        elif key_type == "rtree_radio":
            start_time = time.time()
            self.rtree.radius_query(rtree_left, 5)
            end_time = time.time()
            return end_time - start_time
        
    
    def test_search_range(self, total_path ,Indices_struct, csv_time_search ):
        df = pd.read_csv(total_path)
        random_sample = df.sample(n=100, random_state=42)  # random_state para reproducibilidad
        
        # Obtener las claves y coordenadas
        keys_for_search = random_sample[self.name_key].astype(str).tolist()
        list_latitude_longitude = random_sample[["latitude", "longitude"]].values.tolist()
      # se crea un diccionario para almacenar los tiempos de búsqueda
        tiempos = {}
        for struct in Indices_struct:
            tiempos[struct] = []
            print (f"Probando búsqueda en {struct}...")
            for j in range(len(keys_for_search)):
                key_start = keys_for_search[j]
                # aumentar 2 minutos a la clave para el rango
                key_end = str(pd.to_datetime(key_start) + pd.Timedelta(minutes=2))
                latitude = float(list_latitude_longitude[j][0])
                longitude = float(list_latitude_longitude[j][1])
                rtree_left = [latitude, longitude]
                rtree_right = [latitude + 10, longitude + 10]  # Ajustar el rango según sea necesario

                time = self.search_range(key_start = key_start, key_end=key_end , key_type = struct, rtree_left = rtree_left , rtree_right= rtree_right)
                time = round(time*1000, 4)
                tiempos[struct].append(time)
        # se crea un DataFrame con los tiempos de búsqueda
        df = pd.DataFrame(tiempos)
        # se guarda el DataFrame en un archivo CSV
        if os.path.exists(csv_time_search):
            df.to_csv(csv_time_search, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_time_search, index=False)




    def test_search(self, total_path ,Indices_struct, csv_time_search ):
        df = pd.read_csv(total_path)
        random_sample = df.sample(n=100, random_state=42)  # random_state para reproducibilidad
        
        # Obtener las claves y coordenadas
        keys_for_search = random_sample[self.name_key].astype(str).tolist()
        list_latitude_longitude = random_sample[["latitude", "longitude"]].values.tolist()

        # se crea un diccionario para almacenar los tiempos de búsqueda
        tiempos = {}

        for struct in Indices_struct:
            tiempos[struct] = []
            print (f"Probando búsqueda en {struct}...")
            for j in range(len(keys_for_search)):
                key = keys_for_search[j]
                latitude = float(list_latitude_longitude[j][0])
                longitude = float(list_latitude_longitude[j][1])
                key_rtree = [latitude, longitude]
                time = self.search(key = keys_for_search[j], key_type = struct, key_rtree = key_rtree)
                time = round(time*1000, 4)
                tiempos[struct].append(time)
        # se crea un DataFrame con los tiempos de búsqueda
        df = pd.DataFrame(tiempos)
        # se guarda el DataFrame en un archivo CSV
        if os.path.exists(csv_time_search):
            df.to_csv(csv_time_search, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_time_search, index=False)

    def insert(self, key , index_type ,key_rtree , pos):
        """
        Realiza una búsqueda de los keys especificados y guarda los tiempos en un CSV.
        """
        i=1
        if  index_type == "heap":
            pos = self.heap._read_header()
            KEYS.append(pos)
            start_time = time.time()
            self.heap.insert(key)
            end_time = time.time()
            return end_time - start_time 
        elif index_type == "bptree":
            start_time = time.time()
            self.bptree.add(pos_new_record = i)
            end_time = time.time()
            return end_time - start_time
        elif index_type == "hash":
            start_time = time.time()
            record = self.heap.read(i)
            self.hash.insert(record = record , data_position = i)
            end_time = time.time()
            return end_time - start_time
        elif index_type == "sequential":
            start_time = time.time()
            self.sequential.add(pos_new_record = i)
            end_time = time.time()
            return end_time - start_time
        elif index_type == "isam":
            start_time = time.time()
            self.isam.add(pos_new_record = i)
            end_time = time.time()
            return end_time - start_time
        elif index_type == "brin":
            start_time = time.time()
            self.brin.add(pos_new_record = i)
            end_time = time.time()
            return end_time - start_time
        elif index_type == "rtree":
            start_time = time.time()
            record = self.heap.read(i)
            self.rtree.insert(record = record, record_pos = i)
            end_time = time.time()
            return end_time - start_time




def Test_global():
    for x in range(len(num)):
        test_data_full = f'test_data_full{num[x]}.csv'
        total_path = os.path.join(path, test_data_full)
        csv_times = f'csv_times{num[x]}.csv'
        EL_indice = MEGA_SUPER_HIPER_MASTER_INDICE(name_key = "timestamp", table_format = table_format, x = x ,test_global = True)
        EL_indice.generate_test_data(path =total_path , csv_times = csv_times, Indices_struct = Indices_struct , x = x)

def Test_search():
    for x in range(len(num)):
        test_data_full = f'test_data_full{num[x]}.csv'
        total_path = os.path.join(path, test_data_full)
        print (f"Generando datos de prueba para {num[x]} registros...")
        EL_indice = MEGA_SUPER_HIPER_MASTER_INDICE(name_key = "timestamp", table_format = table_format, x = x)
        csv_time_search = f'csv_time_search{num[x]}.csv'
        EL_indice.test_search(total_path = total_path, Indices_struct = Indices_struct, csv_time_search = csv_time_search)

def Test_search_range():
    for x in range(len(num)):
        test_data_full = f'test_data_full{num[x]}.csv'
        total_path = os.path.join(path, test_data_full)
        print (f"Generando datos de prueba para {num[x]} registros...")
        EL_indice = MEGA_SUPER_HIPER_MASTER_INDICE(name_key = "timestamp", table_format = table_format, x = x)
        csv_time_search = f'csv_time_search_range{num[x]}.csv'
        indices = ["heap", "bptree", "hash", "sequential", "isam", "brin", "rtree_point_to_point", "rtree_knn", "rtree_radio"]
        EL_indice.test_search_range(total_path = total_path, Indices_struct = indices, csv_time_search = csv_time_search)

Test_search_range()
