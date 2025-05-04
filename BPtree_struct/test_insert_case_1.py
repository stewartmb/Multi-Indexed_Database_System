import BPTree_file as BPT


def test_codigo():
    #eliminar archivos existentes
    try:
        import os
        os.remove('BPtree_struct/index_file.bin')
        os.remove('BPtree_struct/data_file.bin')
    except FileNotFoundError:
        pass
    # Crear un registro
    arbol = BPT.BPTree('BPtree_struct/index_file.bin', 'BPtree_struct/data_file.bin')  # Corrección aquí  # Corrección aquí
    registro1 = BPT.Registro(codigo="A1", nombre="Producto", ciclo="01")
    registro2 = BPT.Registro(codigo="B2", nombre="Producto", ciclo="02")
    registro3 = BPT.Registro(codigo="C3", nombre="Producto", ciclo="03")
    registro4 = BPT.Registro(codigo="D4", nombre="Producto", ciclo="04")
    registro5 = BPT.Registro(codigo="E5", nombre="Producto", ciclo="05")
    registro6 = BPT.Registro(codigo="F6", nombre="Producto", ciclo="06")
    registro7 = BPT.Registro(codigo="G7", nombre="Producto", ciclo="07")
    registro8 = BPT.Registro(codigo="H8", nombre="Producto", ciclo="08")
    registro9 = BPT.Registro(codigo="I9", nombre="Producto", ciclo="09")
    registro10 = BPT.Registro(codigo="J10", nombre="Producto", ciclo="10")
    registro11 = BPT.Registro(codigo="K11", nombre="Producto", ciclo="11")
    registro12 = BPT.Registro(codigo="L12", nombre="Producto", ciclo="12")
    registro13 = BPT.Registro(codigo="M13", nombre="Producto", ciclo="13")
    registro14 = BPT.Registro(codigo="N14", nombre="Producto", ciclo="14")
    registro15 = BPT.Registro(codigo="O15", nombre="Producto", ciclo="15")
    registro16 = BPT.Registro(codigo="P16", nombre="Producto", ciclo="16")
    registro17 = BPT.Registro(codigo="Q17", nombre="Producto", ciclo="17")
    registro18 = BPT.Registro(codigo="R18", nombre="Producto", ciclo="18")
    registro19 = BPT.Registro(codigo="S19", nombre="Producto", ciclo="19")
    registro20 = BPT.Registro(codigo="T20", nombre="Producto", ciclo="20")


    # Insertar el registro en el árbol
    print(" registro 1:")
    arbol.add(registro1)
    arbol.print_tree_by_levels()
    print(" registro 2:")
    arbol.add(registro2)
    arbol.print_tree_by_levels()
    print(" registro 3:")
    arbol.add(registro3)
    arbol.print_tree_by_levels()
    print(" registro 4:")
    arbol.add(registro4)
    arbol.print_tree_by_levels()
    print(" registro 5:")
    arbol.add(registro5)
    arbol.print_tree_by_levels()
    print(" registro 6:")
    arbol.add(registro6)
    arbol.print_tree_by_levels()
    print(" registro 7:")
    arbol.add(registro7)
    arbol.print_tree_by_levels()
    print(" registro 8:")
    arbol.add(registro8)        
    arbol.print_tree_by_levels()
    print(" registro 9:")
    arbol.add(registro9)
    arbol.print_tree_by_levels()
    print(" registro 10:")
    arbol.add(registro10)
    arbol.print_tree_by_levels()
    print(" registro 11:")
    arbol.add(registro11)
    arbol.print_tree_by_levels()
    print(" registro 12:")
    arbol.add(registro12)
    arbol.print_tree_by_levels()
    print(" registro 13:")
    arbol.add(registro13)
    arbol.print_tree_by_levels()
    print(" registro 14:")
    arbol.add(registro14)
    arbol.print_tree_by_levels()
    print(" registro 15:")
    arbol.add(registro15)
    arbol.print_tree_by_levels()
    print(" registro 16:")
    arbol.add(registro16)
    arbol.print_tree_by_levels()
    print(" registro 17:")
    arbol.add(registro17)
    arbol.print_tree_by_levels()
    print(" registro 18:")
    arbol.add(registro18)
    arbol.print_tree_by_levels()
    print(" registro 19:")
    arbol.add(registro19)
    arbol.print_tree_by_levels()
    print(" registro 20:")
    arbol.add(registro20)
    arbol.print_tree_by_levels()





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
        os.remove('BPtree_struct/index_file.bin')
        os.remove('BPtree_struct/data_file.bin')
    except FileNotFoundError:
        pass
    # Crear un registro
    arbol = BPT.BPTree('BPtree_struct/index_file.bin', 'BPtree_struct/data_file.bin')  # Corrección aquí
    registro1 = BPT.Registro(codigo="C1", nombre="producto100", ciclo="01")
    registro2 = BPT.Registro(codigo="B2", nombre="producto200", ciclo="02")
    registro3 = BPT.Registro(codigo="A3", nombre="producto3000", ciclo="03")
    # Insertar el registro en el árbol
    arbol.add(registro1)
    arbol.add(registro2)
    arbol.add(registro3)
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
    arbol = BPT.BPTree('BPtree_struct/index_file.bin', 'BPtree_struct/data_file.bin')  # Corrección aquí
    registro1 = BPT.Registro(codigo="C1", nombre="producto100", ciclo="01")
    registro2 = BPT.Registro(codigo="B2", nombre="producto200", ciclo="02")
    registro3 = BPT.Registro(codigo="A3", nombre="producto3000", ciclo="03")
    # Insertar el registro en el árbol
    arbol.add(registro1)
    arbol.add(registro2)
    arbol.add(registro3)
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

test_codigo()

