import csv
import os
import BPTree_file as BPT
import random

# Lista fija de códigos a usar
# generar todos los códigos aleatorios entre 1 y 100
CODIGOS_A_USAR = random.sample(range(101, 200), 99)
print("Códigos a usar:", CODIGOS_A_USAR)
def insertar_registros_en_orden_fijo(csv_path, index_file, data_file):
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
    registros_dict = {}
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            codigo_num = int(row['codigo'])
            registros_dict[codigo_num] = BPT.Registro(
                codigo=str(codigo_num),
                nombre=row['nombre'],
                ciclo=row['ciclo']
            )

    # Crear árbol B+ e insertar en el orden de CODIGOS_A_USAR
    arbol = BPT.BPTree(index_file, data_file)
    for i, codigo in enumerate(CODIGOS_A_USAR, 1):
        if codigo in registros_dict:
            registro = registros_dict[codigo]
            arbol.add(registro)
        else:
            print(f"¡Código {codigo} no encontrado en el CSV!")

    print("\nInserción completada. Resumen:")
    print(f"- Registros insertados: {len(CODIGOS_A_USAR)}")
    print(f"- Estructura final del árbol B+:")
    arbol.print_tree_by_levels()

    return arbol

# Ejemplo de uso
if __name__ == "__main__":
    csv_path = "BPtree_struct/BPTree.csv"  # Asegúrate de que los códigos sean numéricos
    index_file = "BPtree_struct/index_file.bin"
    data_file = "BPtree_struct/data_file.bin"

    arbol = insertar_registros_en_orden_fijo(csv_path, index_file, data_file)

    # Búsquedas de prueba (en el mismo orden)
    print("\nBúsquedas de prueba:")
    for codigo in CODIGOS_A_USAR:
        resultado = arbol.search(str(codigo))
        print(f"Buscando {codigo}: {resultado}")
    
    print("\nBusquedas por rango:")
    # Búsquedas por rango
    resultado_rango = arbol.search_range("110", "150")
    for registro in resultado_rango:
        print(f"{registro.codigo}, {registro.nombre}, {registro.ciclo}")

    # eliminar archivos existentes
    try:
        os.remove(index_file)
        os.remove(data_file)
    except FileNotFoundError:
        pass