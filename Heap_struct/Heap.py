import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *



class Heap:
    HEADER_FORMAT = 'i'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, table_format, key: str,
                 data_file_name: str = 'data_file.bin', force_create: bool = False):
        self.filename = data_file_name
        self.RT = RegistroType(table_format, key)
        self.record_total_size = self.RT.size + 1  # +1 byte para el flag de eliminado

        if not os.path.exists(self.filename):
            with open(self.filename, 'wb') as f:
                f.write(struct.pack(self.HEADER_FORMAT, 0))  # encabezado inicial: 0 registros
        elif os.path.getsize(self.filename) < self.HEADER_SIZE:
            with open(self.filename, 'wb') as f:
                f.write(struct.pack(self.HEADER_FORMAT, 0))  # encabezado inicial: 0 registros

        if force_create:
            with open(self.filename, 'wb') as f:
                f.write(struct.pack(self.HEADER_FORMAT, 0))

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

    def read(self, pos: int) -> list | None:
        if pos < 0 or pos >= self._read_header():
            return None
        with open(self.filename, 'rb') as f:
            f.seek(self.HEADER_SIZE + (pos * self.record_total_size))
            data = f.read(self.RT.size)
            flag = f.read(1)
            registro = self.RT.from_bytes(data)
            if flag == b'\x01':
                return None
            return registro

    def mark_deleted(self, pos):
        with open(self.filename, 'r+b') as f:
            f.seek(self.HEADER_SIZE + (pos * self.record_total_size) + self.RT.size)
            f.write(b'\x01')


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
h = Heap(format_dict, key="id", data_file_name="data_test.bin", force_create=True)


# Insertar registros
pos1 = h.insert([1, "Alice", True])
pos2 = h.insert([2, "Bob", False])

print(h.read(pos1))
print(h.read(pos2))

h.mark_deleted(pos1)
print(h.read(pos1))

pos3 = h.insert([3, "Charlie", True])
print("Out of range y eliminados = None:")
for i in range(-2,5):
    print(i, h.read(i))
