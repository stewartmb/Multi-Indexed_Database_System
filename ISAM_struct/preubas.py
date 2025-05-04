from isam import ISAM
# Crear/abrir estructura ISAM
isam = ISAM('ISAM_struct\data_file.bin','ISAM_struct\index_file.bin', 'ISAM_struct\overflow_file.bin')

# Insertar registros
isam.insert("003", "Ana Torres", "24")
isam.insert("001", "Juan Perez", "23")
isam.insert("005", "Maria Gomez", "24")
isam.insert("002", "Carlos Ruiz", "23")
isam.insert("004", "Luisa Velez", "25")

# Buscar registros
print(isam.search("002"))  # Devuelve el registro de Carlos Ruiz

# Visualizar estructura
isam.print_structure()
