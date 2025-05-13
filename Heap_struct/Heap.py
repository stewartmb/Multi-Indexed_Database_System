import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *



class Heap:
    HEADER_FORMAT = 'i'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, table_format, key: str,
                 data_file_name: str = 'data_file.bin'):
        self.filename = data_file_name
        self.RT = RegistroType(table_format, key)
        self.record_total_size = self.RT.size + 1  # +1 byte para el flag de eliminado

        if not os.path.exists(self.filename):
            with open(self.filename, 'wb') as f:
                f.write(struct.pack(self.HEADER_FORMAT, 0))  # encabezado inicial: 0 registros
        elif os.path.getsize(self.filename) < self.HEADER_SIZE:
            with open(self.filename, 'wb') as f:
                f.write(struct.pack(self.HEADER_FORMAT, 0))  # encabezado inicial: 0 registros

    def _read_header(self):
        with open(self.filename, 'rb') as f:
            return struct.unpack(self.HEADER_FORMAT, f.read(self.HEADER_SIZE))[0]

    def _write_header(self, count):
        with open(self.filename, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack(self.HEADER_FORMAT, count))

    def insert(self, registro):
        with open(self.filename, 'ab') as f:
            offset = self._read_header() * self.record_total_size + self.HEADER_SIZE
            f.seek(offset)
            data = self.RT.to_bytes(registro)
            f.write(data)
            f.write(b'\x00')

        count = self._read_header()
        self._write_header(count + 1)
        return count

    def _select_all(self, include_deleted=False):
        registros = []
        count = self._read_header()

        with open(self.filename, 'rb') as f:
            f.seek(self.HEADER_SIZE)
            for _ in range(count):
                data = f.read(self.RT.size)
                flag = f.read(1)
                if not data or not flag:
                    break
                if flag == b'\x01' and not include_deleted:
                    continue
                registro = self.RT.from_bytes(data)
                registros.append(registro)
        return registros


# Define el formato del registro
format_dict = {
    "id": "i",
    "nombre": "20s",
    "activo": "?"
}

# Crear la instancia del Heap
heap = Heap(format_dict, key="id", data_file_name="data_test.bin")

# Insertar registros
heap.insert([1, "Alice", True])
heap.insert([2, "Bob", False])
heap.insert([3, "Charlie", True])

# Leer e imprimir todos los registros
registros = heap._select_all()
print(registros)
print("Registros activos:")
for r in registros:
    print(r)
print("DDDD")
# Leer todos incluyendo eliminados (aún no se ha eliminado ninguno)
registros_todos = heap._select_all(include_deleted=True)
print("\nRegistros (incluyendo eliminados):")
for r in registros_todos:
    print(r)