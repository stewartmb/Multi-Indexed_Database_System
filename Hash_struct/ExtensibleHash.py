import pickle
import struct
import os

from OpenGL.platform.entrypoint31 import records
from numpy.matlib import empty


# TODO: Falta implementar algun hasheo para estructuras no numericas ni strings
def getbits(dato, nbits):
    """
    toma los ultimos n bits de un dato en binario.
    :param dato: dato a convertir
    :param nbits: cantidad de bits a tomar
    """
    if isinstance(dato, int): # numeros
        bits = bin(dato & (2 ** (nbits * 8) - 1))[2:]
    else:
        if isinstance(dato, str): # texto
            dato_bytes = dato.encode('utf-8')
        else: # otros
            dato_bytes = pickle.dumps(dato)

        bits = ''.join(f'{byte:08b}' for byte in dato_bytes)
    return bits[-nbits:] if nbits <= len(bits) else bits.zfill(nbits)


def find_numbers_with_suffix(n, suffix):
    result = []
    for i in range(n + 1):
        bin_rep = bin(i)[2:]
        if bin_rep.endswith(suffix):
            result.append(i)
    return result

class RegistroType:
    """
    Estructura que maneja el control de los registros.
    size = espacio en bytes
    FORMAT = formato de los registros (struct)
    dict_format = formato de los registros (diccionario)
    to_bytes = convierte el registro a bytes
    from_bytes = convierte bytes a un registro
    get_key = obtiene el valor del indice de ordenamiento del registro
    """
    def __init__(self, dict_format, keyIndex):
        self.dict_format = dict_format
        self.keyIndex = keyIndex
        self.key = list(dict_format.keys())[keyIndex]
        self.FORMAT = ''.join(dict_format.values())
        self.size = struct.calcsize(self.FORMAT)

    def to_bytes(self, args):
        """
        Convierte el registro a bytes.
        """
        types = list(self.dict_format.values())
        for i in range(len(args)):
            if types[i] == 'i':
                args[i] = int(args[i])
            elif types[i] == 'f':
                args[i] = float(args[i])
            else:
                args[i] = args[i].encode('utf-8').ljust(20, b'\x00')

        return struct.pack(self.FORMAT, *args)

    def from_bytes(self, data):
        """
        Convierte bytes a un registro.
        """
        unpacked = list(struct.unpack(self.FORMAT, data))
        types = list(self.dict_format.values())
        for i in range(len(unpacked)):
            if types[i] == 'i':
                unpacked[i] = int(unpacked[i])
            elif types[i] == 'f':
                unpacked[i] = float(unpacked[i])
            else:
                unpacked[i] = unpacked[i].decode('utf-8').strip('\x00')

        return unpacked

    def get_key(self, lista):
        return lista[self.keyIndex]

class BucketType:
    """
    Estructura que maneja el control de los buckets.
    BT.size = espacio en bytes
    BT.FORMAT = formato de los buckets
    BT.to_bytes = convierte el bucket a bytes
    BT.from_bytes = convierte bytes a un bucket
    BT.max_records = cantidad maxima de registros por bucket
    """
    def __init__(self, max_records):
        self.FORMAT = 'i' * max_records + 'iii' # *Records, local_depth, fullness, overflow_position
        self.size = struct.calcsize(self.FORMAT)
        self.max_records = max_records

    def to_bytes(self, bucket):
        """
        Convierte el diccionario bucket a bytes.
        """
        return struct.pack(self.FORMAT,
                           *bucket['records'],
                           bucket['local_depth'],
                           bucket['fullness'],
                           bucket['overflow_position']
                           )

    def from_bytes(self, data):
        """
        Convierte bytes a un diccionario bucket.
        """
        unpacked = struct.unpack('i' * self.max_records + 'iii', data)
        bucket = {
            'records': list(unpacked[0:self.max_records]),
            'local_depth': unpacked[-3],
            'fullness': unpacked[-2],
            'overflow_position': unpacked[-1]
        }
        return bucket

class ExtensibleHash:
    def __init__(self, table_format, index_key, name_index_file='index_file.bin',
                 name_data_file='data_file.bin', global_depth = 3, max_records = 3):
        self.index_file = name_index_file
        self.data_file = name_data_file
        self.global_depth = global_depth
        self.max_records = max_records
        self.header = 3
        self.header_size = 4 * self.header
        self.hashindex = 2 ** global_depth
        self.hashindex_size = 4 * self.hashindex

        self.RT = RegistroType(table_format,1)
        self.BT = BucketType(max_records)
        self._initialize_files(global_depth, force=True)


    def _read_header_index(self, file, index):
        """
        Lee el encabezado del archivo de índice y devuelve una tupla
        """
        file.seek(4 * index)
        data = file.read(4)
        return struct.unpack('i', data)[0]

    def _write_header_index(self, file, value, index):
        """
        Escribe en el encabezado del archivo de índice los elementos de args
        """
        file.seek(4 * index)
        file.write(struct.pack('i', value))

    def _initialize_files(self, global_depth, force=False):
        """
        Inicializa los archivos de índice y datos.
        """
        if force or not os.path.exists(self.index_file):
            with open(self.index_file, 'wb') as f:
                f.write(struct.pack('i', global_depth))
                f.write(struct.pack('i', 0))
                f.write(struct.pack('i', 2))
                for i in range(self.hashindex):
                    if i % 2 == 0:
                        f.write(struct.pack('i', 0))
                    else:
                        f.write(struct.pack('i', 1))

                # [0,0,0...0,0,0] + [localdepth, fullness, overflowPosition]
                f.write(struct.pack(self.BT.FORMAT, *([-1] * self.max_records + [1,0,-1])))
                f.write(struct.pack(self.BT.FORMAT, *([-1] * self.max_records + [1,0,-1])))

        if force or not os.path.exists(self.data_file):
            with open(self.data_file, 'wb') as f:
                f.write(struct.pack('i', 0))

    def _write_record(self, data_file, position, record):
        """
        Escribe un registro en una posicion del archivo de datos
        """
        offset = position * self.RT.size
        data_file.seek(offset)
        data_file.write(self.RT.to_bytes(record))

    def _insert_value_in_bucket(self, index_file, bucket_position, register_position):
        """
        Inserta al bucket la referencia a la posicion de un registro
        """
        index_file.seek(self.header_size + self.hashindex_size + bucket_position * self.BT.size)
        bucket = self.BT.from_bytes(index_file.read(self.BT.size))

        # Si el bucket no esta lleno, se agrega el registro
        if bucket['fullness'] < self.max_records:
            bucket['records'][bucket['fullness']] = register_position
            bucket['fullness'] += 1
            index_file.seek(self.header_size + self.hashindex_size + bucket_position * self.BT.size)
            index_file.write(self.BT.to_bytes(bucket))
        else:
            return False

        return True

    def insert(self, record):
        """
        Inserta un registro en datafile y su puntero en el hash extensible.
        :param record: registro a insertar
        :return: True si se inserto, False si no se pudo insertar
        """
        # bucket_index_position = posicion del puntero al bucket
        index_hash = getbits(self.RT.get_key(record), self.global_depth)
        bucket_index_position = int(index_hash, 2)

        with open(self.index_file, 'r+b') as index_file, open(self.data_file, 'r+b') as data_file:
            register_position = self._append_record(index_file, data_file, record)
            self._add_to_hash(index_file, data_file, bucket_index_position, register_position, index_hash)

    def insert_with_position(self, index_file, data_file, record, register_position):
        """
                Inserta un registro en el hash extensible (sabiendo su posicion en el datafile).
                :param record: registro a insertar
                :return: True si se inserto, False si no se pudo insertar
                """
        # bucket_index_position = posicion del puntero al bucket
        index_hash = getbits(self.RT.get_key(record), self.global_depth)
        bucket_index_position = int(index_hash, 2)
        self._add_to_hash(index_file, data_file, bucket_index_position, register_position, index_hash)


    def _add_to_hash(self, index_file, data_file, bucket_index_position, register_position, index_hash):
        index_file.seek(self.header_size + bucket_index_position * 4)
        bucket_position = struct.unpack('i', index_file.read(4))[0]
        inserted = self._insert_value_in_bucket(index_file, bucket_position, register_position)
        if (not inserted):
            print("No se pudo insertar")
            index_file.seek(self.header_size + self.hashindex_size + bucket_position * self.BT.size)
            old_bucket = self.BT.from_bytes(index_file.read(self.BT.size))
            # crear nuevos buckets
            bucket1_pos = bucket_position
            bucket2_pos = self._read_header_index(index_file,2)
            self._write_header_index(index_file, bucket2_pos + 1, 2)
            emptyBucket = {'records': [-1, -1, -1],
                           'local_depth': old_bucket['local_depth'] + 1,
                           'fullness': 0,
                           'overflow_position': -1}
            index_file.seek(self.header_size + self.hashindex_size + bucket1_pos * self.BT.size)
            index_file.write(self.BT.to_bytes(emptyBucket))
            index_file.seek(self.header_size + self.hashindex_size + bucket2_pos * self.BT.size)
            index_file.write(self.BT.to_bytes(emptyBucket))

            # actualizar punteros
            current_pattern = index_hash[-old_bucket['local_depth']:]

            for i in find_numbers_with_suffix(2**self.global_depth, '0' + current_pattern):
                index_file.seek(self.header_size + i * 4)
                index_file.write(struct.pack('i', bucket1_pos))
            for i in find_numbers_with_suffix(2**self.global_depth, '1' + current_pattern):
                index_file.seek(self.header_size + i * 4)
                index_file.write(struct.pack('i', bucket2_pos))

            # reinsertar elementos
            for i in range(old_bucket['fullness']):
                data_file.seek(old_bucket['records'][i] * self.RT.size)
                registro = self.RT.from_bytes(data_file.read(self.RT.size))
                self.insert_with_position(index_file, data_file, registro, old_bucket['records'][i])

            # reinserta el nuevo registro
            data_file.seek(register_position * self.RT.size)
            registro = self.RT.from_bytes(data_file.read(self.RT.size))
            self.insert_with_position(index_file, data_file, registro, register_position)




    def _append_record(self, index_file, data_file, record):
        size = self._read_header_index(index_file, 1)
        pos = size
        self._write_record(data_file, size, record)
        self._write_header_index(index_file, size + 1, 1)
        return pos

    def imprimir(self):
        """
        Imprime todos los buckets y sus registros.
        """
        with open(self.index_file, 'rb') as index_file, open(self.data_file, 'rb') as data_file:
            index_file.seek(0)
            global_depth = struct.unpack('i', index_file.read(4))[0]
            print(f"Global depth: {global_depth}")
            index_file.seek(4)
            size = struct.unpack('i', index_file.read(4))[0]
            print(f"Size: {size}")

            # Iterar buckets
            for i in range(self._read_header_index(index_file, 2)):
                index_file.seek(self.header_size + self.hashindex_size + i * self.BT.size)
                bucket = self.BT.from_bytes(index_file.read(self.BT.size))
                print(f"Bucket {i}: {bucket['records']}, fullness: {bucket['fullness']}, local depth: {bucket['local_depth']}")
                # Iterar registros
                for j in range(bucket['fullness']):
                    data_file.seek(bucket['records'][j] * self.RT.size)
                    registro = self.RT.from_bytes(data_file.read(self.RT.size))
                    print(f"Registro {j}: {registro}")




# class Bucket:
#     def __init__(self, splitable=True):
#         self.records = []
#         self.full = 0
#         self.overflow = None
#         self.splitable = splitable
#
#     def insert(self, record):
#         if self.full < MAX_RECORDS:
#             self.records.append(record)
#             self.full += 1
#             return True
#         else:
#             if self.splitable:
#                 return False
#             else:
#                 if self.overflow is None:
#                     self.overflow = Bucket(splitable=False)
#                 self.overflow.insert(record)
#                 return True
#
#     def search(self, record):
#         if record in self.records:
#             return True
#         elif self.overflow is not None:
#             return self.overflow.search(record)
#         else:
#             return False
#
#     def delete(self, record):
#         if record in self.records:
#             self.records.remove(record)
#             self.full -= 1
#             return True
#         elif self.overflow is not None:
#             return self.overflow.delete(record)
#         else:
#             return False
#
# class Node:
#     def __init__(self, bucket, level):
#         self.bucket = bucket
#         self.zero = None
#         self.one = None
#         self.level = level
#
#     def split(self):
#         self.bucket = None
#         if self.level == 1:
#             print("Splitting bucket")
#             self.zero = Node(Bucket(splitable=False), self.level - 1)
#             self.one = Node(Bucket(splitable=False), self.level - 1)
#         else:
#             self.zero = Node(Bucket(), self.level - 1)
#             self.one = Node(Bucket(), self.level - 1)
#
#     def insert(self, record, hash):
#         if self.bucket is None:
#             if hash[MAX_D - self.level] == "0":
#                 return self.zero.insert(record, hash)
#             else:
#                 return self.one.insert(record, hash)
#         else:
#             if self.bucket.insert(record):
#                 return True
#             else:
#                 records = self.bucket.records
#                 records.append(record)
#                 self.split()
#                 for r in records:
#                     hash = posbucket(r)
#                     if hash[MAX_D - self.level] == "0":
#                         self.zero.insert(r, hash)
#                     else:
#                         self.one.insert(r, hash)
#
#
#     def print(self, prefix=""):
#         if self.bucket is not None:
#             print(f"Bucket ({prefix}):", self.bucket.records)
#             current = self.bucket
#             while current.overflow is not None:
#                 current = current.overflow
#                 print(f"  Overflow ({prefix}):", current.records)
#         else:
#             self.zero.print(prefix + "0")
#             self.one.print(prefix + "1")
#
#     def search(self, record, hash):
#         if self.bucket is not None:
#             return self.bucket.search(record)
#         else:
#             if hash[MAX_D - self.level] == "0":
#                 return self.zero.search(record, hash)
#             else:
#                 return self.one.search(record, hash)
#
#     def delete(self, record, hash):
#         if self.bucket is not None:
#             if self.bucket.records.remove(record):
#                 self.bucket.full -= 1
#                 if self.bucket.full == 0:
#                     self.bucket = None
#                 return True
#
#         else:
#             if hash[MAX_D - self.level] == "0":
#                 return self.zero.delete(record, hash)
#             else:
#                 return self.one.delete(record, hash)
#
# class ExtensibleHash:
#     def __init__(self):
#         self.head = Node(Bucket(), MAX_D)
#         self.head.split()
#
#     def insert(self, record):
#         hash = posbucket(record)
#         if self.head.insert(record, hash):
#             return True
#
#     def search(self, record):
#         hash = posbucket(record)
#         return self.head.search(record, hash)
#
#     def delete(self, record):
#         hash = posbucket(record)
#         return self.head.delete(record, hash)
#
#     def print(self):
#         print("Printing buckets")
#         self.head.print()



#
# rt = RegistroType(1)
# b = rt.to_bytes("001", "Juan Perez", "01")
# print(rt.from_bytes(b))
#
# print(rt.FORMAT)
#
# bt = BucketType(5)
# b = bt.to_bytes([1,2], 1, 2, 3)
# print(bt.from_bytes(b))



table_format = {"nombre":"10s", "edad": "i", "ciudad": "25s"}
index_key = 1
eh = ExtensibleHash(table_format, index_key)

print(''.join(table_format.values()))


while True:
    print("\nSeleccione una opción:")
    print("1. Insertar elementos")
    print("2. Imprimir elementos")
    print("3. Salir")

    choice = input("Ingrese su opción: ")

    if choice == '1':
        # Insertar elementos
        elements = input("Ingrese los elementos a insertar (separados por comas, ej. 033, g, 02): ")
        elements = elements.split(",")
        eh.insert([elem.strip() for elem in elements])
    elif choice == '2':
        # Imprimir elementos
        eh.imprimir()
    elif choice == '3':
        # Salir del programa
        print("¡Adiós!")
        break
    else:
        print("Opción inválida. Intente de nuevo.")