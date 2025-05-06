import Independ_BPTree_file as B
import Indice_BPTree_file as archivo
import os


def test_registro():
    # Crear un registro
    registro = B.Registro(codigo="A1", nombre="Producto", ciclo="01")

    # Convertir el registro a bytes
    registro_bytes = registro.to_bytes()
    print("Bytes del registro:", registro_bytes)

    # Reconstruir el registro desde los bytes
    registro_reconstruido = B.Registro.from_bytes(registro_bytes)
    print("Registro reconstruido:")
    print("Código:", registro_reconstruido.codigo)
    print("Nombre:", registro_reconstruido.nombre)
    print("Ciclo:", registro_reconstruido.ciclo)

    # Verificar que los datos sean consistentes
    assert registro_reconstruido.codigo == registro.codigo, "Error: Código no coincide"
    assert registro_reconstruido.nombre == registro.nombre, "Error: Nombre no coincide"
    assert registro_reconstruido.ciclo == registro.ciclo, "Error: Ciclo no coincide"

    print("Prueba exitosa: Los datos del registro son consistentes.")

def test_index_page():
    # Crear una página de índice
    a = {"nombre": "12s", "edad": "i", "altura": "d"}
    b = "nombre"

    btree = archivo.BPTree(table_format=a, name_key = b , max_num_child=4) 
    page = archivo.IndexPage(leaf=True, M = btree.M, format_key=btree.format_key, indexp_format=btree.indexp_format) 
    page.keys = ['ASF', 'ASD', 'EDW']  # M-1 claves (M=4, por lo que M-1=3)
    page.childrens = [1, 2, 3, 4]  # M punteros
    page.leaf = True  # Indica si es una hoja
    page.father = 0  # Índice del padre
    page.key_count = 3  # Número de claves en el nodo

    print("Página de índice original:")
    print("Leaf:", page.leaf)
    print("Keys:", page.keys)
    print("Childrens:", page.childrens)
    print("Key Count:", page.key_count)
    print("Parent:", page.father)
    
    # Convertir la página a bytes
    page_bytes = page.to_bytes()
    print("Bytes de la página de índice:", page_bytes)

    # Reconstruir la página desde los bytes
    reconstructed_page = page.from_bytes(page_bytes)

    print("Página reconstruida:")
    print("Leaf:", reconstructed_page.leaf)
    print("Keys:", reconstructed_page.keys)
    print("Childrens:", reconstructed_page.childrens)
    print("Key Count:", reconstructed_page.key_count)
    print("Parent:", reconstructed_page.father)

    # Verificar que los datos sean consistentes
    assert reconstructed_page.leaf == page.leaf, "Error: Leaf no coincide"
    assert reconstructed_page.keys == page.keys, "Error: Keys no coinciden"
    assert reconstructed_page.childrens == page.childrens, "Error: Childrens no coinciden"
    assert reconstructed_page.key_count == page.key_count, "Error: Key Count no coincide"

    print("Prueba exitosa: Los datos son consistentes.")


def test_index_page_indice():
    # Create format specifications
    table_format = {"codigo": "d", "nombre": "d", "ciclo": "d"}
    name_key = "codigo"
    
    # Create B+ tree instance (order M=4)
    btree = archivo.BPTree(table_format=table_format, name_key=name_key, max_num_child=4)
    
    # Create index page
    page = archivo.IndexPage(
        leaf=True,
        M=btree.M,
        format_key=btree.format_key,
        indexp_format=btree.indexp_format
    )
    page.keys = [1235.1234, 1234.1346, 1123.54735]  # M-1 keys (M=4, so 3 keys)
    page.childrens = [1, 2, 3, 4]     # M children pointers
    page.father = 0                    # Parent index
    page.key_count = 3                 # Number of keys in node

    print("Original index page:")
    print("Leaf:", page.leaf)
    print("Keys:", page.keys)
    print("Children:", page.childrens)
    print("Key Count:", page.key_count)
    print("Parent:", page.father)
    
    # Convert to bytes
    page_bytes = page.to_bytes(btree.format_key, btree.indexp_format)
    print("Page bytes:", page_bytes)

    # Reconstruct from bytes
    reconstructed_page = page.from_bytes(page_bytes, btree.M, btree.format_key, btree.indexp_format)

    print("\nReconstructed page:")
    print("Leaf:", reconstructed_page.leaf)
    print("Keys:", reconstructed_page.keys)
    print("Children:", reconstructed_page.childrens)
    print("Key Count:", reconstructed_page.key_count)
    print("Parent:", reconstructed_page.father)

    # Verify data consistency
    assert reconstructed_page.leaf == page.leaf, "Leaf mismatch"
    assert reconstructed_page.keys == page.keys, "Keys mismatch"
    assert reconstructed_page.childrens == page.childrens, "Children mismatch"
    assert reconstructed_page.key_count == page.key_count, "Key count mismatch"
    assert reconstructed_page.father == page.father, "Parent mismatch"

    print("\nTest successful: Data is consistent!")


def test_indice_bptree_search():
    # Create format specifications

    table_format = {"codigo": "3s", "nombre": "20s", "ciclo": "2s"}
    name_key = "codigo"
    
    # Create B+ tree instance (order M=4)
    btree = archivo.BPTree(table_format=table_format, name_key=name_key, max_num_child=4)
    
    
    # Búsquedas de prueba (en el mismo orden)
    CODIGOS_A_USAR = [115, 121, 112, 165, 134, 124, 188, 110, 180, 127, 101, 128, 118, 120, 126, 158, 141, 193, 173, 179, 143, 108, 105, 176, 172, 138, 183, 196, 189, 104, 186, 184, 153, 150, 175, 154, 178, 146, 145, 147, 142, 140, 139, 194, 171, 133, 135, 123, 197, 125, 198, 149, 130, 152, 199, 160, 137, 148, 107, 159, 111, 182, 117, 191, 129, 177, 116, 157, 131, 164, 195, 106, 119, 136, 109, 144, 166, 132, 185, 192, 174, 190, 122, 181, 102, 169, 113, 156, 168, 114, 162, 103, 187, 167, 163, 170, 161, 151, 155]
    print("\nBúsquedas de prueba:")
    for codigo in CODIGOS_A_USAR:
        resultado = btree.search(str(codigo))
        print(f"Buscando {codigo}: {resultado}")
    
    print("\nBusquedas por rango:")
    # Búsquedas por rango
    resultado_rango = btree.search_range("110", "150")
    for registro in resultado_rango:
        print(f"{registro[0]}, {registro[1]}, {registro[2]}")

test_index_page_indice()
    
