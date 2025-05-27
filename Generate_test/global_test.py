import pandas as pd
import os
import sys
import os

# Importar las estructuras de índices
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import BPtree_struct.Indice_BPTree_file as BPTREE
import Hash_struct.Hash as HASH
import Sequential_Struct.Indice_Sequential_file as SEQUENTIAL
import Isam_struct.Indice_Isam_file as ISAM 
import Brin_struct.Indice_Brin_file as BRIN
import RTree_struct.RTreeFile_Final as RTREE


import csv

# Lista fija de códigos a usar
# generar todos los códigos aleatorios entre 1 y 100
num = [10000,50000,100000]
x=1
path = "/Users/stewart/2025-1/BD2/Proyecto_BD2/Data_test"
# path = "C:/Users/Equipo/Documents/2025-1/BD2/proyecto/Proyecto_BD2/Data_test"
data_file = f'Generate_test/data_file{num[x]}.bin'

btree_file1 = f'Generate_test/btree_file1{num[x]}.bin'

btree

test_data_full = f'/test_data_full{num[x]}.csv'

table_format = {"timestamp": "24s", "random_int": "i", "name": "20s", "email": "50s", "date": "10s", "price": "d", "latitude": "d", "longitude": "d",  "is_active": "?", "category": "20s"}


Indices_struct = ["bptree", "hash", "sequential", "isam", "brin" ,"rtree"]

class MEGA_SUPER_HIPER_MASTER_INDICE:
    def __init__(self, name_key, table_format , param1 , param2 , x ):
        self.data_file = f'Generate_test/data_file{num[x]}.bin'
        self.bptree = BPTREE.BPTree(table_format, name_key , name_index_file = f'Generate_test/btree_1_index{num[x]}.bin', name_data_file = data_file , max_num_child = param1)
        self.hash = HASH.Hash(table_format, name_key, param1)
        self.sequential = SEQUENTIAL.Sequential(table_format, name_key, param1)
        self.isam = ISAM.ISAM(table_format, name_key, param1, param2)
        self.brin = BRIN.BRIN(table_format, name_key, param1)
        self.rtree = RTREE.RTreeFile(table_format, name_key, param1)




def notest_insert_CSV(csv_path, index_file, data_file):
    """
    Inserta registros en el ORDEN EXACTO de CODIGOS_A_USAR.
    """
    # Eliminar archivos existentes
    try:
        os.remove(index_file)
        os.remove(data_file)
    except FileNotFoundError:
        pass

    # Leer todos los registros del CSV y guardarlos en un diccionario por código
    arbol = archivo.BPTree(table_format, name_key, max_num_child=ma)
    registros_dict = {}
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        registros = list(reader)
        i = 0         
        for row in registros:
            i += 1
            m = N
            if random_index == 0:
                m = m / N
            if i % m == 0:
                print("|", end="")
            key = arbol.RT.get_key(row)
            KEYS.append(key)
            # manejar errores de formato:
            arbol.add(row)
        print()
        # arbol.print_tree_by_levels()


    return arbol

def notest_onesearch(key):
    # BUSQUEDA DE UN REGISTRO ESPECIFICO
    arbol = archivo.BPTree(table_format, name_key, max_num_child=ma)
    print("\nBúsqueda de un registro específico:")
    resultado = arbol.search(key)
    # for registro in resultado:
    #     print(registro)
    
    print()
    print("Búsqueda unica de prueba finalizada.")

def notest_allsearch():
    # BUSQUEDAS
    arbol = archivo.BPTree(table_format, name_key, max_num_child=ma)
    print("\nBúsquedas de prueba:")
    i=0
    for key in KEYS:
        i+=1
        resultado = arbol.search(key)
        # print(resultado)
        m = N
        if random_index == 0:
            m = m / N
        if i % m == 0:
            print("|", end="")
        if resultado == []:
            print(f"{key} No encontrado")
            break
    
    print()
    print("Búsqueda de prueba finalizada.")


def notest_search_range():
    # BUSQUEDAS POR RANGO
    arbol = archivo.BPTree(table_format, name_key, max_num_child=ma)

    if 's' in arbol.format_key:
        inferior = 'A'
        superior = 'D'
    else:
        inferior = 100
        superior = 1000
    print(f"\nBúsquedas por rango: {inferior} y {superior}:")
    print( f"Nombre de la llave: {name_key}  |  Formato de la llave: {arbol.format_key}\n")
    
    resultado_rango = arbol.search_range(inferior, superior)
    # for registro in resultado_rango:
    #     print(registro)
    

def notest_eliminar():
    # ELIMINAR REGISTROS
    arbol = archivo.BPTree(table_format, name_key, max_num_child=ma)
    print("\nEliminando registros:")
    while True:
        print(" desea eliminar un registro? (e)")
        opcion = input("Ingrese 'e' para eliminar o 'salir' para terminar: ").lower()
        if opcion == 'salir':
            break
        if opcion != 'e':
            continue
        key = input("Ingrese la llave del registro a eliminar: ")
        resultado = arbol.delete(int(key))
        if resultado:
            print(f"Registro con llave {key} eliminado.")
        else:
            print(f"Registro con llave {key} no encontrado.")
        
        arbol.print_tree_by_levels()




# Ejemplo de uso
if __name__ == "__main__":

    # Crear el árbol B+ e insertar registros desde el CSV
    notest_insert_CSV(csv_path, index_file, data_file)

    # Prueba de búsqueda
    notest_allsearch()
    # Prueba de búsqueda por rango
    notest_search_range()

    # Prueba de busqueda de un registro específico
    notest_onesearch(KEYS[0])

    # notest_eliminar()
 


    # # eliminar archivos existentes
    # try:
    #     os.remove(index_file)
    #     os.remove(data_file)
    # except FileNotFoundError:
    #     pass



