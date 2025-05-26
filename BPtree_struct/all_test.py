import pandas as pd
import os
import Independ_BPTree_file as archivo
import random
import sys
import csv
from pathlib import Path

# Lista fija de códigos a usar
# generar todos los códigos aleatorios entre 1 y 100
num = [10000,50000,100000]
x = 2
KEYS = []
PATH = "/Users/stewart/2025-1/BD2/Proyecto_BD2/Data_test"
# PATH = "C:/Users/Equipo/Documents/2025-1/BD2/proyecto/Proyecto_BD2/Data_test"
print("PATH", PATH)
index_file = "BPtree_struct/index_file.bin"
data_file = "BPtree_struct/data_file.bin"
test_data_full = f'/test_data_full{num[0]}.csv'
list_csv= ["/BPTree.csv","/airports.csv","/zipcodes.csv",test_data_full]

format_tables = [{"codigo": "i", "nombre": "30s", "ciclo": "i"},
                 {"iata": "4s", "name": "20s", "city": "20s", "state": "2s", "country": "20s", "latitude": "d", "longitude": "d"},
                 {"zip_code": "i", "latitude": "d", "longitude": "d", "city": "20s", "state": "2s", "county": "20s"},
                 {"timestamp": "24s", "random_int": "i", "name": "20s", "email": "50s", "date": "10s", "price": "d", "latitude": "d", "longitude": "d",  "is_active": "?", "category": "20s"}]

name_keys = ["codigo", "iata", "zip_code", 'random_int']

# numero aleatorio entre 1 y 3
random_index = 3

print("random_index", random_index)
# Seleccionar el formato de tabla correspondiente
table_format = format_tables[random_index]
print("table_format", table_format)
# Seleccionar el archivo CSV correspondiente
csv_path = list_csv[random_index]
csv_path = PATH + csv_path
print("csv_path", csv_path)
# Seleccionar el nombre de clave correspondiente
name_key = name_keys[random_index]
print("name_key", name_key)

ma = 1000 # orden del árbol B+

N = 1000 # cada cuántos registros se imprime una barra de progreso



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
    for registro in resultado:
        print(registro)
    
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
 


    # eliminar archivos existentes
    try:
        os.remove(index_file)
        os.remove(data_file)
    except FileNotFoundError:
        pass