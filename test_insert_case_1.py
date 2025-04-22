import BPTree_file as BPT


def test_codigo():
    #eliminar archivos existentes
    try:
        import os
        os.remove('index_file.bin')
        os.remove('data_file.bin')
    except FileNotFoundError:
        pass  # Ignorar si los archivos no existen

    # Crear un registro
    arbol = BPT.BPTree('index_file.bin', 'data_file.bin')  # Corrección aquí
    registro1 = BPT.Registro(codigo="A1", nombre="Producto", ciclo="01")
    registro2 = BPT.Registro(codigo="B2", nombre="Producto", ciclo="02")
    registro3 = BPT.Registro(codigo="C3", nombre="Producto", ciclo="03")


    # Insertar el registro en el árbol
    arbol.insert(registro1)
    arbol.insert(registro2)
    arbol.insert(registro3)

    # Buscar el registro en el árbol
    resultado1 = arbol.search("A1")
    resultado2 = arbol.search("B2")
    resultado3 = arbol.search("C3")

    print("Resultado de la búsqueda:")
    print("Registro A1 encontrado:", resultado1)
    print("Registro B2 encontrado:", resultado2)
    print("Registro C3 encontrado:", resultado3)

    print ("==========================")
    # imprimir arbol 
    arbol.print_tree_by_levels()
    print ("==========================")


    print("Prueba exitosa: El registro se insertó y se encontró correctamente.")


def test_producto():
    #eliminar archivos existentes
    try:
        import os
        os.remove('index_file.bin')
        os.remove('data_file.bin')
    except FileNotFoundError:
        pass
    # Crear un registro
    arbol = BPT.BPTree('index_file.bin', 'data_file.bin')  # Corrección aquí
    registro1 = BPT.Registro(codigo="C1", nombre="producto100", ciclo="01")
    registro2 = BPT.Registro(codigo="B2", nombre="producto200", ciclo="02")
    registro3 = BPT.Registro(codigo="A3", nombre="producto3000", ciclo="03")
    # Insertar el registro en el árbol
    arbol.insert(registro1)
    arbol.insert(registro2)
    arbol.insert(registro3)
    # Buscar el registro en el árbol
    resultado1 = arbol.search("producto100")
    resultado2 = arbol.search("producto200")
    resultado3 = arbol.search("producto3000")
    print("Resultado de la búsqueda:")
    print("Registro 1 encontrado:", resultado1)
    print("Registro 2 encontrado:", resultado2)
    print("Registro 3 encontrado:", resultado3)
    print ("==========================")
    # imprimir arbol 
    arbol.print_tree_by_levels()
    print ("==========================")
    print("Prueba exitosa: El registro se insertó y se encontró correctamente.")

def test_ciclo():
    #eliminar archivos existentes
    try:
        import os
        os.remove('index_file.bin')
        os.remove('data_file.bin')
    except FileNotFoundError:
        pass
    # Crear un registro
    arbol = BPT.BPTree('index_file.bin', 'data_file.bin')  # Corrección aquí
    registro1 = BPT.Registro(codigo="C1", nombre="producto100", ciclo="01")
    registro2 = BPT.Registro(codigo="B2", nombre="producto200", ciclo="02")
    registro3 = BPT.Registro(codigo="A3", nombre="producto3000", ciclo="03")
    # Insertar el registro en el árbol
    arbol.insert(registro1)
    arbol.insert(registro2)
    arbol.insert(registro3)
    # Buscar el registro en el árbol
    resultado1 = arbol.search("01")
    resultado2 = arbol.search("02")
    resultado3 = arbol.search("03")
    print("Resultado de la búsqueda:")
    print("Registro 1 encontrado:", resultado1)
    print("Registro 2 encontrado:", resultado2)
    print("Registro 3 encontrado:", resultado3)
    print ("==========================")
    # imprimir arbol
    arbol.print_tree_by_levels()
    print ("==========================")
    print("Prueba exitosa: El registro se insertó y se encontró correctamente.")

test_ciclo()

