import unittest
import os
from Hash import Hash  # Reemplazar con el nombre real del archivo
import random



print("Creado")
format = {"nombre": "12s", "edad": "i", "altura": "d"}
key = "edad"
hash = Hash(
    table_format=format,
    key=key,
    data_file_name="hash_test_data.bin",
    buckets_file_name="hash_test_buckets.bin",
    index_file_name="hash_test_index.bin",
    GD=4,
    max_records_per_bucket=5,
    force_create=True
)

print("Insertando")
hash.insert(["Pepe", 18, 123.12])     # Pos 0
hash.insert(["Juan", 19, 764.46])     # Pos 1
hash.insert(["Lucas", 18, 925.34])    # Pos 2
hash.insert(["Alfonso", 18, 585.21])  # Pos 3
hash.insert(["Estefano", 20, 468.83]) # Pos 4
hash.insert(["Carlos", 19, 875.27])   # Pos 5


# Lista de nombres comunes para elegir
nombres = ["Ana", "Pedro", "Maria", "Luis", "Marta", "Javier", "Sofia", "David", "Laura", "Daniel", 
           "Isabel", "Antonio", "Sandra", "Francisco", "Raquel", "Jose", "Carlos", "Elena", "Pablo", "Veronica", "Ruben"]

# Función para generar los nuevos datos
def generar_datos(num_datos):
    datos = []
    for _ in range(num_datos):
        nombre = random.choice(nombres)
        edad = random.randint(18, 40)  # Edad entre 18 y 40
        monto = round(random.uniform(100, 1000), 2)  # Monto entre 100 y 1000
        datos.append([nombre, edad, monto])
    return datos

# Generar 20 nuevos datos
nuevos_datos = generar_datos(100)

for dato in nuevos_datos:
    hash.insert(dato)

print(nuevos_datos)

print("Busqueda")
positions = hash.search(18)
registros = [hash.HEAP.read(pos) for pos in positions]
print("Registros encontrados:", registros)

print("Terminado")
for f in ["hash_test_data.bin", "hash_test_buckets.bin", "hash_test_index.bin"]:
    if os.path.exists(f):
        os.remove(f)