import pandas as pd
import os
import Indice_Isam_file as archivo
import random
import sys
import csv
from pathlib import Path

# Lista fija de códigos a usar
# generar todos los códigos aleatorios entre 1 y 100
KEYS = []
PATH = "/Users/stewart/2025-1/BD2/Proyecto_BD2/Data_test"
print("PATH", PATH)
index_file = 'Isam_Struct/index_file.bin'
data_file = 'Isam_Struct/data_file.bin'
list_csv= ["/BPTree.csv","/airports.csv","/zipcodes.csv"]

format_tables = [{"codigo": "i", "nombre": "30s", "ciclo": "i"},
                 {"iata": "4s", "name": "20s", "city": "20s", "state": "2s", "country": "20s", "latitude": "d", "longitude": "d"},
                 {"zip_code": "i", "latitude": "d", "longitude": "d", "city": "20s", "state": "2s", "county": "20s"}]

name_keys = ["ciclo", "iata", "zip_code"]

# numero aleatorio entre 1 y 3
random_index = 0

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



def Create_index(csv_path, index_file, data_file):
    """
    Inserta registros en el ORDEN EXACTO de CODIGOS_A_USAR.
    """
    # Eliminar archivos existentes
    try:
        os.remove(index_file)
        # os.remove(data_file)
    except FileNotFoundError:
        pass

    # Generar indices al inicializar el ISAM
    isam = archivo.ISAM(table_format, name_key, name_index_file = index_file, name_data_file=data_file)

    print("Indices generados.")


    return isam
KEYS = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205]

def test_search():
    # BUSQUEDAS
    isam = archivo.ISAM(table_format, name_key, name_index_file = index_file, name_data_file=data_file)
    print("\nBúsquedas de prueba:")

    print ("formato de la llave:", isam.format_key)
    print ("index_format:", isam.indexp_format)
    print ("Maximo de hijos:", isam.M)
    i=0
    for key in KEYS:
        i+=1
        resultado = isam.search(key)
        # print(resultado)
        if resultado == []:
            print(f"{key} No encontrado")
            break
    print()
    print("Búsqueda de prueba finalizada.")


def test_search_range():
    # BUSQUEDAS POR RANGO
    isam = archivo.ISAM(table_format, name_key, name_index_file = index_file, name_data_file=data_file)

    if 's' in isam.format_key:
        inferior = 'A'
        superior = 'D'
    else:
        inferior = 101
        superior = 140
    print(f"\nBúsquedas por rango: {inferior} y {superior}:")
    print( f"Nombre de la llave: {name_key}  |  Formato de la llave: {isam.format_key}\n")
    
    resultado_rango = isam.search_range(inferior, superior)
    # for registro in resultado_rango:
    #     print(registro)

def test_onesearch(key):
    # BUSQUEDA DE UN REGISTRO ESPECIFICO
    isam = archivo.ISAM(table_format, name_key, name_index_file = index_file, name_data_file=data_file)
    print("\nBúsqueda de un registro específico:", key)
    resultado = isam.search(key)
    if resultado == []:
        print(f"{key} No encontrado")
        return
    for registro in resultado:
        print(isam.HEAP.read(registro))
    print("Búsqueda unica de prueba finalizada.")
    print()

def test_insert_eliminar():
    # INSERTAR REGISTROS
    isam = archivo.ISAM(table_format, name_key, name_index_file = index_file, name_data_file=data_file)
    print("\nInsertando y eliminando registros:")
    while True:
        print(" desea insertar o eliminar un registro? (i/e)")
        opcion = input("Ingrese 'i' para insertar, 'e' para eliminar o 'salir' para terminar: ").lower()
        if opcion == 'salir':
            break
        if opcion not in ['i', 'e']:
            print("Opción no válida. Intente de nuevo.")
            continue
        if opcion == 'i':
            codigo = input("Ingrese el codigo: \n(salir para terminar) ")
            if codigo.lower() == 'salir':
                break
            codigo = int(codigo)
            nombre = input("Ingrese el nombre: ")
            ciclo = input("Ingrese el ciclo: ")
            registro = [codigo , nombre , int(ciclo)]
            isam.add(registro)
            print(f"Codigo insertado: {codigo}")
        elif opcion == 'e':
            codigo = input("Ingrese el codigo a eliminar: \n(salir para terminar) ")
            if codigo.lower() == 'salir':
                break
            codigo = int(codigo)
            isam.delete(codigo)
            print(f"Codigo eliminado: {codigo}")
        isam.print_ISAM_by_levels()

# Ejemplo de uso
if __name__ == "__main__":

    # Crear el árbol B+ e insertar registros desde el CSV
    Create_index(csv_path, index_file, data_file)
    # Prueba de búsqueda
    test_search()
    # # Prueba de búsqueda por rango
    test_search_range()
    # # Prueba de búsqueda de un registro específico
    test_onesearch(1)
    # # Prueba de insercion de un registro específico
    test_insert_eliminar()
    # # # Prueba de eliminación de un registro específico


 


    # eliminar archivos existentes
    # try:
    #     os.remove(data_file)
    #     os.remove(index_file)
    # except FileNotFoundError:
    #     pass