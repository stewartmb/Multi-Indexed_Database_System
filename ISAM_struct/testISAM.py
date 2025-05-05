# Pruebas del ISAM (Con archivos)
from ISAM_struct.ISAM_File import ISAM, Registro

# Crear/abrir estructura ISAM
isam = ISAM('ISAM_struct/data_file.bin', 'ISAM_struct/index_file.bin', 'ISAM_struct/overflow_file.bin')

# Crear objetos Registro
registro1 = Registro("003", "Ana Torres", "24")
registro2 = Registro("001", "Juan Perez", "23")
registro3 = Registro("005", "Maria Gomez", "24")
registro4 = Registro("002", "Carlos Ruiz", "23")
registro5 = Registro("004", "Luisa Velez", "25")

# Insertar registros (ahora con objetos Registro)
isam.insert_record(registro1)
isam.insert_record(registro2)
isam.insert_record(registro3)
isam.insert_record(registro4)
isam.insert_record(registro5)

# Buscar registros (devuelve objetos Registro)
encontrado = isam.search_record("002")
if encontrado:
    print(f"Registro encontrado: {encontrado}")
    print(f"Nombre: {encontrado.nombre}")
    print(f"Ciclo: {encontrado.ciclo}")
else:
    print("Registro no encontrado")

# Visualizar estructura
isam.print_structure()