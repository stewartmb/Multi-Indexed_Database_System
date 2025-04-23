import BPTree_file as BPTree
def test_registro():
    # Crear un registro
    registro = BPTree.Registro(codigo="A1", nombre="Producto", ciclo="01")

    # Convertir el registro a bytes
    registro_bytes = registro.to_bytes()
    print("Bytes del registro:", registro_bytes)

    # Reconstruir el registro desde los bytes
    registro_reconstruido = BPTree.Registro.from_bytes(registro_bytes)
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
    page = BPTree.IndexPage(leaf=True)
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
    reconstructed_page = BPTree.IndexPage.from_bytes(page_bytes)
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

test_registro()
test_index_page()
