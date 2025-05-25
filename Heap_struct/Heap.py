import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *

class Heap:
    HEADER_FORMAT = 'ii'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, table_format, key: str,
                 data_file_name: str, force_create: bool = False):
        self.filename = data_file_name
        self.RT = RegistroType(table_format, key)
        self.record_total_size = self.RT.size + 1  # +1 byte para el flag de eliminado
        self.key = key

        if not os.path.exists(self.filename):
            with open(self.filename, 'wb') as f:
                f.write(struct.pack(self.HEADER_FORMAT, 0, 0))  # encabezado inicial: 0 registros
        elif os.path.getsize(self.filename) < self.HEADER_SIZE:
            with open(self.filename, 'wb') as f:
                f.write(struct.pack(self.HEADER_FORMAT, 0, 0))  # encabezado inicial: 0 registros

        if force_create:
            with open(self.filename, 'wb') as f:
                f.write(struct.pack(self.HEADER_FORMAT, 0, 0))

    def _read_header(self):
        with open(self.filename, 'rb') as f:
            return struct.unpack(self.HEADER_FORMAT, f.read(self.HEADER_SIZE))[0]
        
    def _read_deleted(self):
        with open(self.filename, 'rb') as f:
            return struct.unpack(self.HEADER_FORMAT, f.read(self.HEADER_SIZE))[1]

    def _write_header(self, count, deleted):
        with open(self.filename, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack(self.HEADER_FORMAT, count, deleted))
    
    def is_deleted(self, pos):
        if self.read(pos):
            return False
        return True

    def insert(self, registro):
        with open(self.filename, 'ab') as f:
            offset = self._read_header() * self.record_total_size + self.HEADER_SIZE
            f.seek(offset)
            data = self.RT.to_bytes(registro)
            f.write(data)
            f.write(b'\x00')

        count = self._read_header()
        self._write_header(count + 1, self._read_deleted())
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
        deleted_count = self._read_deleted()
        deleted_count += 1
        if deleted_count == 30:
            return True
        self._write_header(self._read_header(), deleted_count)
        return False


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

    def search(self, left, right):
        """
        Busca registros en el rango [left, right] (incluyendo ambos extremos).
        """
        registros = []
        count = self._read_header()

        with open(self.filename, 'rb') as f:
            f.seek(self.HEADER_SIZE)
            for i in range(count):
                data = f.read(self.RT.size)
                flag = f.read(1)
                if not data or not flag:
                    break
                if flag == b'\x01':
                    continue
                registro = self.RT.from_bytes(data)
                if left <= self.RT.get_key(registro) <= right:
                    registros.append(i)
        return registros

    def get_all(self):
        """
        Busca registros en el rango [left, right] (incluyendo ambos extremos).
        """
        registros = []
        count = self._read_header()

        with open(self.filename, 'rb') as f:
            f.seek(self.HEADER_SIZE)
            for i in range(count):
                data = f.read(self.RT.size)
                flag = f.read(1)
                if not data or not flag:
                    break
                if flag == b'\x01':
                    continue
                registros.append(i)
        return registros