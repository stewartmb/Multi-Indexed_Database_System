import csv
import os
import Independ_BPTree_file as BPT
import Indice_BPTree_file as archivo
import random

# Lista fija de códigos a usar
# generar todos los códigos aleatorios entre 1 y 100
KEYS = []
csv_path = "BPtree_struct/BPTree.csv"  # Asegúrate de que los códigos sean numéricos
index_file = "BPtree_struct/index_file.bin"
data_file = "BPtree_struct/data_file.bin"
table_format = {"codigo": "i", "nombre": "20s", "ciclo": "i"}
name_key = "codigo"
M =4


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
    arbol = archivo.BPTree(table_format, name_key, max_num_child=M)
    registros_dict = {}
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        registros = list(reader)         
        for row in registros:
            key = arbol.RT.get_key(row)
            KEYS.append(key)
            arbol.add(row)

        print("Registros del CSV insertados en el árbol B+.")

    arbol.print_tree_by_levels()

    return arbol

def test_search():
    # BUSQUEDAS
    arbol = archivo.BPTree(table_format, name_key, max_num_child=M)
    print("\nBúsquedas de prueba:")
    for key in KEYS:
        resultado = arbol.search(key)
        print(f"Buscando {key}: {resultado}")

def test_search_range(inferior, superior):
    # BUSQUEDAS POR RANGO
    print("\nBúsquedas por rango:")
    arbol = archivo.BPTree(table_format, name_key, max_num_child=M)
    resultado_rango = arbol.search_range(inferior, superior)
    for registro in resultado_rango:
        print(registro)




# Ejemplo de uso
if __name__ == "__main__":

    # Crear el árbol B+ e insertar registros desde el CSV
    test_insert_CSV(csv_path, index_file, data_file)
    # Prueba de búsqueda
    test_search()
    # Prueba de búsqueda por rango
    test_search_range(101, 110)


    # eliminar archivos existentes
    try:
        os.remove(index_file)
        os.remove(data_file)
    except FileNotFoundError:
        pass