import os
import csv
from sequential_corrigiendo import Sequential, Record

def test_sequential_operations():
    for fname in ["test.bin", "aux.bin"]:
        try:
            if os.path.exists(fname):
                os.remove(fname)
        except Exception as e:
            print(f"No se pudo eliminar {fname}. Error: {e}")

    print("\n=== Creando Sequential File ===")
    seq = Sequential("test.bin", k=3, maxi=5)
    
    # Verificar header inicial
    start_pos, aux, k_count, aux_count = seq.get_header()
    print(f"Header inicial: start_pos={start_pos}, aux={aux}, k_count={k_count}, aux_count={aux_count}")
    assert k_count == 0 and aux_count == 0

    # Insertar registros de prueba
    print("\n=== Insertando registros ===")
    records = [
        Record(5, "Producto A", 100, "2023-01-01"),
        Record(2, "Producto B", 200, "2023-01-02"),
        Record(8, "Producto C", 300, "2023-01-03"),
        Record(4, "Producto D", 400, "2023-01-04"),
        Record(7, "Producto E", 500, "2023-01-05")
    ]
    """
        ,
        Record(3, "Producto E", 500, "2023-01-05"),
        Record(1, "Producto D", 400, "2023-01-04")
        Record(7, "Producto E", 500, "2023-01-05"),
        Record(3, "Producto F", 600, "2023-01-06"),
        Record(9, "Producto G", 700, "2023-01-07"),
        Record(4, "Producto H", 800, "2023-01-08"),
        Record(6, "Producto I", 900, "2023-01-09"),
        Record(10, "Producto J", 1000, "2023-01-10")"""

    for record in records:
        seq.insert(record)
        print(f"Insertado: {record}")
        _, _, _, aux_count = seq.get_header()
        print(f"aux_count actual: {aux_count}")
    
    seq.print_all()

    """# Prueba de búsqueda
    print("\n=== Probando búsqueda ===")
    for i in range(1, 11):
        found = seq.search(i)
        if found:
            print(f"Encontrado ID {i}: {found}")
        else:
            print(f"No encontrado ID {i}")

    # Prueba de búsqueda por rango
    print("\n=== Probando búsqueda por rango (IDs 3-7) ===")
    range_results = seq.search_range(3, 7)
    for res in range_results:
        print(res)

    # Prueba de eliminación
    print("\n=== Probando eliminación ===")
    print("Eliminando ID 2:", seq.delete(2))
    _, _, k_count, _ = seq.get_header()
    print(f"k_count después de eliminar ID 2: {k_count}")
    
    print("Eliminando ID 5:", seq.delete(5))
    _, _, k_count, _ = seq.get_header()
    print(f"k_count después de eliminar ID 5: {k_count}")
    
    print("Eliminando ID 8:", seq.delete(8))  # Debería triggerear rebuild por k=3
    _, _, k_count, _ = seq.get_header()
    print(f"k_count después de eliminar ID 8: {k_count}")
    
    seq.print_all()

    # Insertar más registros para probar archivo auxiliar
    print("\n=== Insertando más registros para probar archivo auxiliar ===")
    more_records = [
        Record(12, "Producto K", 1100, "2023-01-11"),
        Record(11, "Producto L", 1200, "2023-01-12"),
        Record(13, "Producto M", 1300, "2023-01-13"),
        Record(14, "Producto N", 1400, "2023-01-14"),
        Record(15, "Producto O", 1500, "2023-01-15")  # Debería triggerear rebuild por maxi=5
    ]

    for record in more_records:
        seq.insert(record)
        print(f"Insertado: {record}")
        _, _, _, aux_count = seq.get_header()
        print(f"aux_count actual: {aux_count}")
    
    seq.print_all()

    # Prueba final de búsqueda
    print("\n=== Prueba final de búsqueda ===")
    for i in range(1, 16):
        found = seq.search(i)
        if found:
            print(f"Encontrado ID {i}: {found}")
        else:
            print(f"No encontrado ID {i}")

    # Prueba final de búsqueda por rango
    print("\n=== Prueba final de búsqueda por rango (IDs 5-12) ===")
    range_results = seq.search_range(5, 12)
    for res in range_results:
        print(res)

def test_with_csv():
    # Limpiar archivos anteriores
    for fname in ["sequential_csv.dat", "aux_csv.bin"]:
        if os.path.exists(fname):
            os.remove(fname)

    # Crear instancia de Sequential
    seq = Sequential("sequential_csv.dat")

    # Insertar datos desde CSV
    print("\n=== Insertando datos desde CSV ===")
    with open("sales_dataset_random.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Saltar encabezado
        for row in reader:
            id = int(row[0])
            nombre = row[1]
            codigo = int(row[2])
            fecha = row[4]
            seq.insert(Record(id, nombre, codigo, fecha))
    
    seq.print_all()

    # Prueba de búsqueda
    print("\n=== Probando búsqueda con datos CSV ===")
    for i in range(1, 11):
        found = seq.search(i)
        if found:
            print(f"Encontrado ID {i}: {found}")
        else:
            print(f"No encontrado ID {i}")

    # Prueba de eliminación
    print("\n=== Probando eliminación con datos CSV ===")
    for i in range(1, 6):
        print(f"Eliminando ID {i}: {seq.delete(i)}")
    
    seq.print_all()
"""
if __name__ == "__main__":
    print("=== PRUEBAS CON DATOS DE PRUEBA ===")
    test_sequential_operations()
    
    """print("\n\n=== PRUEBAS CON DATOS DEL CSV ===")
    test_with_csv()"""