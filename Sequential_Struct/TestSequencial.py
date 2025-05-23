import pandas as pd
import os
import Indice_Sequential_file as archivo
import random
import sys
import csv
from pathlib import Path

# Lista fija de códigos a usar
# generar todos los códigos aleatorios entre 1 y 100
KEYS = []
PATH = "/Users/stewart/2025-1/BD2/Proyecto_BD2/Data_test"
print("PATH", PATH)
index_file = 'Sequential_Struct/datos.bin'
data_file = 'Sequential_Struct/sequencial_aux.bin'
list_csv= ["/BPTree.csv","/airports.csv","/zipcodes.csv"]

format_tables = [{"codigo": "i", "nombre": "50s", "ciclo": "i"},
                 {"iata": "4s", "name": "20s", "city": "20s", "state": "2s", "country": "20s", "latitude": "d", "longitude": "d"},
                 {"zip_code": "i", "latitude": "d", "longitude": "d", "city": "20s", "state": "2s", "county": "20s"}]

name_keys = ["ciclo", "iata", "zip_code"]

# numero aleatorio entre 1 y 3
random_index = 2

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

ma = 200 # tamaño del aux

N = 100 # cada cuántos registros se imprime una barra de progreso



def test_insert_CSV(csv_path, index_file, data_file):
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
    Sequential = archivo.Sequential(table_format, name_key, name_index_file = index_file, name_data_file=data_file, num_aux=ma)
    registros_dict = {}
    print("\nLeyendo registros del CSV...")
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        registros = list(reader)
        i = 0         
        for row in registros:
            # Sequential.inorder()
            i += 1
            m = N
            if random_index == 0:
                m = m / N
            if i % m == 0:
                print("|", end="")
            row = Sequential.RT.correct_format(row)
            key = Sequential.RT.get_key(row)
            type_key = type(key)
            KEYS.append(key)
            Sequential.add(row)
    print()
    print("Proceso de lectura de CSV finalizado.")


    return Sequential

def test_search():
    # BUSQUEDAS
    Sequential = archivo.Sequential(table_format, name_key, name_index_file = index_file, name_data_file=data_file, num_aux=ma)
    print("\nBúsquedas de prueba:")
    i=0
    for key in KEYS:
        i+=1
        resultado = Sequential.search(key)
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


def test_search_range():
    # BUSQUEDAS POR RANGO
    Sequential = archivo.Sequential(table_format, name_key, name_index_file = index_file, name_data_file=data_file, num_aux=ma)

    if 's' in Sequential.format_key:
        inferior = 'A'
        superior = 'D'
    else:
        inferior = 101
        superior = 140
    print(f"\nBúsquedas por rango: {inferior} y {superior}:")
    print( f"Nombre de la llave: {name_key}  |  Formato de la llave: {Sequential.format_key}\n")
    
    resultado_rango = Sequential.search_range(inferior, superior)
    for registro in resultado_rango:
        print(registro)

def test_onesearch(key):
    # BUSQUEDA DE UN REGISTRO ESPECIFICO
    Sequential = archivo.Sequential(table_format, name_key, name_index_file = index_file, name_data_file=data_file, num_aux=ma)
    print("\nBúsqueda de un registro específico:", key)
    resultado = Sequential.search(key)
    if resultado == []:
        print(f"{key} No encontrado")
        return
    for registro in resultado:
        print(registro)
    print("Búsqueda unica de prueba finalizada.")
    print()


def test_delete():
    # ELIMINAR UN REGISTRO
    Sequential = archivo.Sequential(table_format, name_key, name_index_file = index_file, name_data_file=data_file, num_aux=ma)
    print("\nEliminando un registro específico:")
    Sequential.delete(KEYS[0])
    print("Eliminación de prueba finalizada.")
    print()



# Ejemplo de uso
if __name__ == "__main__":

    # Crear el árbol B+ e insertar registros desde el CSV
    test_insert_CSV(csv_path, index_file, data_file)
    # Prueba de búsqueda
    test_search()
    # Prueba de búsqueda por rango
    test_search_range()
    # Prueba de búsqueda de un registro específico
    test_onesearch(KEYS[0])
    # Prueba de eliminación de un registro específico
    test_delete()
    test_onesearch(KEYS[0])


 


    # eliminar archivos existentes
    try:
        os.remove(data_file)
        os.remove(index_file)
    except FileNotFoundError:
        pass