import pickle
import struct
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *



def get_bits(dato: any, nbits: int) -> str:
    """
    toma los ultimos n bits de un dato en binario.
    :param dato: dato a convertir
    :param nbits: cantidad de bits a tomar
    """
    if isinstance(dato, int): # numeros
        bits = bin(dato & (2 ** (nbits * 8) - 1))[2:]
    elif isinstance(dato, float): # float
        dato_bytes = struct.pack('d', dato) # TODO: hashear mas uniformemente
        bits = ''.join(f'{byte:08b}' for byte in dato_bytes)
    else:
        if isinstance(dato, str): # texto
            dato_bytes = dato.encode('utf-8')
        else: # otros
            dato_bytes = pickle.dumps(dato)

        bits = ''.join(f'{byte:08b}' for byte in dato_bytes)
    return bits[-nbits:] if nbits <= len(bits) else bits.zfill(nbits)

class BucketType:
    """
    Estructura que maneja el control de los buckets.
    BT.size = espacio en bytes
    BT.FORMAT = formato de los buckets
    BT.to_bytes = convierte el bucket a bytes
    BT.from_bytes = convierte bytes a un bucket
    BT.max_records = cantidad maxima de registros por bucket
    """
    def __init__(self, max_records: int):
        self.FORMAT = 'i' * max_records + 'iii' # *Records, local_depth, fullness, overflow_position
        self.size = struct.calcsize(self.FORMAT)
        self.max_records = max_records

    def to_bytes(self, bucket: dict) -> bytes:
        """
        Convierte el diccionario bucket a bytes.
        """
        return struct.pack(self.FORMAT,
                           *bucket['records'],
                           bucket['local_depth'],
                           bucket['fullness'],
                           bucket['overflow_position']
                           )

    def from_bytes(self, data: bytes) -> dict:
        """
        Convierte bytes a un diccionario bucket.
        """
        unpacked = struct.unpack(self.FORMAT, data)
        bucket = {
            'records': list(unpacked[0:self.max_records]),
            'local_depth': unpacked[-3],
            'fullness': unpacked[-2],
            'overflow_position': unpacked[-1]
        }
        return bucket

class TreeNodeType:
    """
    Estructura que maneja el control de los nodos del arbol.
    """
    def __init__(self):
        self.FORMAT = 'iiii'
        self.size = struct.calcsize(self.FORMAT)


    def to_bytes(self, treeNode: dict) -> bytes:
        """
        Convierte el nodo a bytes.
        """
        return struct.pack(self.FORMAT,
                            treeNode['bucket_position'],
                            treeNode['left'],
                            treeNode['right'],
                            treeNode['depth']
                           )

    def from_bytes(self, data: bytes) -> dict:
        """
        Convierte bytes a un nodo.
        """
        unpacked = struct.unpack(self.FORMAT, data)
        treeNode = {
            'bucket_position': unpacked[0],
            'left': unpacked[1],
            'right': unpacked[2],
            'depth': unpacked[3]
        }
        return treeNode

class HeaderType:
    """
    Estructura que maneja el control del encabezado.
    global_depth | data_last | bucket_last | node_last
    """
    def __init__(self):
        self.FORMAT = 'iiii'
        self.size = struct.calcsize(self.FORMAT)

    def read(self, file, index: int) -> int:
        """
        Lee el encabezado del archivo de índice
        """
        file.seek(4 * index)
        data = file.read(4)
        return struct.unpack('i', data)[0]

    def write(self, file, value: int, index: int) -> None:
        """
        Escribe en el encabezado del archivo de índice
        """
        file.seek(4 * index)
        file.write(struct.pack('i', value))


class Hash:
    def __init__(self, table_format, key: str,
                 buckets_file_name: str = 'Hash_struct/hash_buckets.bin',
                 index_file_name: str = 'Hash_struct/hash_index.bin',
                 data_file_name: str = 'Hash_struct/data_file.bin',
                 global_depth: int = 3,
                 max_records_per_bucket: int = 3):
        """
        Inicializa el hash extensible.
        :param table_format: formato de la tabla
        :param key: indice de ordenamiento
        :param buckets_file_name: nombre del archivo de buckets
        :param index_file_name: nombre del archivo de índice
        :param data_file_name: nombre del archivo de datos
        :param global_depth: profundidad global
        :param max_records_per_bucket: cantidad maxima de registros por bucket
        """
        self.index_file = index_file_name
        self.buckets_file = buckets_file_name
        self.data_file = data_file_name
        self.global_depth = global_depth
        self.max_records = max_records_per_bucket

        self.NT = TreeNodeType()
        self.RT = RegistroType(table_format, key)
        self.BT = BucketType(max_records_per_bucket)
        self.Header = HeaderType()
        self._initialize_files(global_depth, force=True)

    def _initialize_files(self, global_depth, force=False):
        """
        Inicializa los archivos de índice y datos.
        """
        if force or not os.path.exists(self.index_file):
            with open(self.index_file, 'wb') as f:
                f.write(struct.pack('i', global_depth))
                f.write(struct.pack('i', 0))
                f.write(struct.pack('i', 2))
                f.write(struct.pack('i', 3))
                f.write(self.NT.to_bytes({'bucket_position': -1, 'left': 1, 'right': 2, 'depth': 0}))
                f.write(self.NT.to_bytes({'bucket_position': 0, 'left': -1, 'right': -1, 'depth': 0}))
                f.write(self.NT.to_bytes({'bucket_position': 1, 'left': -1, 'right': -1, 'depth': 0}))

        if force or not os.path.exists(self.buckets_file):
            with open(self.buckets_file, 'wb') as f:
                # [0,0,0...0,0,0] + [localdepth, fullness, overflowPosition]
                f.write(struct.pack(self.BT.FORMAT, *([-1] * self.max_records + [1,0,-1])))
                f.write(struct.pack(self.BT.FORMAT, *([-1] * self.max_records + [1,0,-1])))

        if force or not os.path.exists(self.data_file):
            with open(self.data_file, 'wb') as f:
                f.write(struct.pack('i', 0))

    def _append_record(self, index_file, data_file, record):
        """
        Agrega un registro al archivo de datos
        """
        pos = self.Header.read(index_file,1) # pos = size (primer elemento libre)
        self.Header.write(index_file,pos + 1, 1)
        offset = pos * self.RT.size
        data_file.seek(offset)
        data_file.write(self.RT.to_bytes(record))
        return pos

    def _insert_value_in_bucket(self, buckets_file, index_file, bucket_position, data_position):
        """
        Inserta al bucket la referencia a la posicion de un registro
        """
        buckets_file.seek(bucket_position * self.BT.size)
        bucket = self.BT.from_bytes(buckets_file.read(self.BT.size))

        # Si el bucket no esta lleno, se agrega el registro
        if bucket['fullness'] < self.max_records:
            bucket['records'][bucket['fullness']] = data_position
            bucket['fullness'] += 1
            buckets_file.seek(bucket_position * self.BT.size)
            buckets_file.write(self.BT.to_bytes(bucket))
        else:
            if bucket['local_depth'] != self.global_depth:
                return False
            if bucket['overflow_position'] == -1:
                print("creando overflow")
                overflow_pos = self.Header.read(index_file, 2)
                self.Header.write(index_file, overflow_pos + 1, 2)
                bucket['overflow_position'] = overflow_pos
                emptyBucket = {'records': [-1]*self.max_records,
                               'local_depth': self.global_depth,
                               'fullness': 0,
                               'overflow_position': -1}
                buckets_file.seek(bucket_position * self.BT.size)
                buckets_file.write(self.BT.to_bytes(bucket))
                buckets_file.seek(overflow_pos * self.BT.size)
                buckets_file.write(self.BT.to_bytes(emptyBucket))
            self._insert_value_in_bucket(buckets_file, index_file, bucket['overflow_position'], data_position)
        return True

    def _add_to_hash(self, buckets_file, index_file, data_file, data_position, index_hash):
        node_index = 0
        k = 1
        while True:
            index_file.seek(self.Header.size + node_index * self.NT.size)
            node = self.NT.from_bytes(index_file.read(self.NT.size))
            bucket_position = node['bucket_position']
            if bucket_position == -1:
                if index_hash[-k] == '0':
                    node_index = node['left']
                else:
                    node_index = node['right']
                k += 1
            else:
                break

        inserted = self._insert_value_in_bucket(buckets_file, index_file, bucket_position, data_position)
        if not inserted:
            print("Splitting")
            buckets_file.seek(bucket_position * self.BT.size)
            old_bucket = self.BT.from_bytes(buckets_file.read(self.BT.size))
            # separar bucket buckets
            bucket_left_pos = bucket_position
            bucket_right_pos = self.Header.read(index_file, 2)
            self.Header.write(index_file, bucket_right_pos + 1, 2)
            empty_bucket = {'records': [-1] * self.max_records,
                           'local_depth': old_bucket['local_depth'] + 1,
                           'fullness': 0,
                           'overflow_position': -1}
            buckets_file.seek(bucket_left_pos * self.BT.size)
            buckets_file.write(self.BT.to_bytes(empty_bucket))
            buckets_file.seek(bucket_right_pos * self.BT.size)
            buckets_file.write(self.BT.to_bytes(empty_bucket))

            # separar index
            pos = self.Header.read(index_file, 3)
            ## nuevos nodos
            new_parent = self.NT.to_bytes({'bucket_position': -1,
                                'left': pos, 'right': (pos + 1), 'depth': node['depth'] + 1})
            new_node_left = self.NT.to_bytes({'bucket_position': bucket_left_pos,
                                'left': -1, 'right': -1, 'depth': node['depth']+1})
            new_node_right = self.NT.to_bytes({'bucket_position': bucket_right_pos,
                                'left': -1, 'right': -1, 'depth': node['depth']+1})


            index_file.seek(self.Header.size + pos * self.NT.size)
            index_file.write(new_node_left)
            index_file.seek(self.Header.size + (pos + 1) * self.NT.size)
            index_file.write(new_node_right)
            index_file.seek(self.Header.size + node_index * self.NT.size)
            index_file.write(new_parent)

            self.Header.write(index_file, pos + 2, 3)

            # reinsertar elementos
            for i in range(old_bucket['fullness']):
                data_file.seek(old_bucket['records'][i] * self.RT.size)
                record = self.RT.from_bytes(data_file.read(self.RT.size))
                self._aux_insert(buckets_file, index_file, data_file, record, old_bucket['records'][i])

            # reinserta el nuevo registro
            data_file.seek(data_position * self.RT.size)
            record = self.RT.from_bytes(data_file.read(self.RT.size))
            self._aux_insert(buckets_file, index_file, data_file, record, data_position)


    def _aux_insert(self, buckets_file, index_file, data_file, record, data_position):
        """
        Funcion para reinsertar recursivamente los registros que se dividieron
        """
        index_hash = get_bits(self.RT.get_key(record), self.global_depth)
        self._add_to_hash(buckets_file, index_file, data_file, data_position, index_hash)


    def insert(self, record, data_position=None):
        """
        Inserta un registro en el hash extensible.
        :param record: registro a insertar
        :param data_position: posicion del registro en el archivo de datos.
        Si no se especifica, se agrega al final del archivo (funcionalidad como indice principal).
        """
        with open(self.index_file, 'r+b') as index_file, \
              open(self.data_file, 'r+b') as data_file, \
               open(self.buckets_file, 'r+b') as buckets_file:
            if data_position is None:
                data_position = self._append_record(index_file, data_file, record)

            index_hash = get_bits(self.RT.get_key(record), self.global_depth)
            self._add_to_hash(buckets_file, index_file, data_file, data_position, index_hash)




    def imprimir(self):
        """
        Imprime todos los buckets y sus registros.
        """
        with open(self.index_file, 'r+b') as index_file, \
                open(self.data_file, 'r+b') as data_file, \
                open(self.buckets_file, 'r+b') as buckets_file:
            index_file.seek(self.Header.size)
            root = self.NT.from_bytes(index_file.read(self.NT.size))
            suffix = ""
            if root['bucket_position'] == -1:
                self._aux_imprimir(buckets_file, index_file, data_file, root['left'], "0" + suffix)
                self._aux_imprimir(buckets_file, index_file, data_file, root['right'], "1" + suffix)

    def _aux_imprimir(self, buckets_file, index_file, data_file, node_index, suffix):
        """
        Imprime los buckets y sus registros.
        """
        index_file.seek(self.Header.size + node_index * self.NT.size)
        node = self.NT.from_bytes(index_file.read(self.NT.size))
        if node['bucket_position'] == -1:
            self._aux_imprimir(buckets_file, index_file, data_file, node['left'], "0" + suffix)
            self._aux_imprimir(buckets_file, index_file, data_file, node['right'], "1" + suffix)
        else:
            buckets_file.seek(node['bucket_position'] * self.BT.size)
            bucket = self.BT.from_bytes(buckets_file.read(self.BT.size))
            print(f"Bucket {suffix}:")
            for i in range(bucket['fullness']):
                data_file.seek(bucket['records'][i] * self.RT.size)
                record = self.RT.from_bytes(data_file.read(self.RT.size))
                print(f"  {record}")

            overflow_position = bucket['overflow_position']
            while overflow_position != -1:
                buckets_file.seek(overflow_position * self.BT.size)
                bucket = self.BT.from_bytes(buckets_file.read(self.BT.size))
                print(f"  Overflow Bucket {suffix}:")
                for i in range(bucket['fullness']):
                    data_file.seek(bucket['records'][i] * self.RT.size)
                    record = self.RT.from_bytes(data_file.read(self.RT.size))
                    print(f"    {record}")
                overflow_position = bucket['overflow_position']

    def search(self, key):
        """
        Busca un registro en el hash extensible.
        :param key: clave a buscar
        :return: registro encontrado o None si no se encuentra
        """
        if self.RT.dict_format[self.RT.key] == 'i':
            key = int(key)
        elif self.RT.dict_format[self.RT.key] == 'f':
            key = float(key)
        elif self.RT.dict_format[self.RT.key] == 'd':
            key = float(key)

        with open(self.index_file, 'r+b') as index_file, \
                open(self.data_file, 'r+b') as data_file, \
                open(self.buckets_file, 'r+b') as buckets_file:
            index_hash = get_bits(key, self.global_depth)
            index_file.seek(self.Header.size)
            root = self.NT.from_bytes(index_file.read(self.NT.size))
            if index_hash[-1] == '0':
                return self._aux_search(buckets_file, index_file, data_file, root['left'], index_hash[:-1], key)
            else:
                return self._aux_search(buckets_file, index_file, data_file, root['right'], index_hash[:-1], key)

    def _aux_search(self, buckets_file, index_file, data_file, node_index, index_hash, key):
        """
        Funcion recursiva de busqueda
        """
        index_file.seek(self.Header.size + node_index * self.NT.size)
        node = self.NT.from_bytes(index_file.read(self.NT.size))
        if node['bucket_position'] == -1:
            if index_hash[-1] == '0':
                return self._aux_search(buckets_file, index_file, data_file, node['left'], index_hash[:-1], key)
            else:
                return self._aux_search(buckets_file, index_file, data_file, node['right'], index_hash[:-1], key)
        else:
            buckets_file.seek(node['bucket_position'] * self.BT.size)
            bucket = self.BT.from_bytes(buckets_file.read(self.BT.size))
            self._find_in_bucket(data_file, bucket, key)
            ans = self._find_in_bucket(data_file, bucket, key)
            if ans is not None:
                return ans
            overflow_position = bucket['overflow_position']
            while overflow_position != -1:
                buckets_file.seek(overflow_position * self.BT.size)
                bucket = self.BT.from_bytes(buckets_file.read(self.BT.size))
                ans = self._find_in_bucket(data_file, bucket, key)
                if ans is not None:
                    return ans
                overflow_position = bucket['overflow_position']
        return None

    def _find_in_bucket(self, data_file, bucket, key):
        """
        Busca un registro en un bucket.
        """
        for i in range(bucket['fullness']):
            data_file.seek(bucket['records'][i] * self.RT.size)
            record = self.RT.from_bytes(data_file.read(self.RT.size))
            if self.RT.get_key(record) == key:
                return record



table_format = {"nombre":"10s", "edad": "d"}
index_key = "nombre"
eh = Hash(table_format, index_key)

print(''.join(table_format.values()))

nums = random.sample(range(100,1000), 200)
nums = [1,2,3,4,5,6,7,8]

for i in range(len(nums)):
    nums[i] = nums[i] + random.random()

placed = nums[0:100]
not_placed = nums[100:200]

for i in placed:
    for j in not_placed:
        if i == j:
            print(f"Elemento {i} repetido")
            break

test_passed = True

try:
    for i in placed:
        eh.insert([f"data_{i}", i])
except Exception as e:
    print(f"Error al insertar: {e}")
    test_passed = False

if test_passed:
    print("Test de insert pasado correctamente")

for i in placed:
    if eh.search(i) is None:
        print(f"Elemento {i} no encontrado (falso negativo)")
        test_passed = False

for i in not_placed:
    if eh.search(i) is not None:
        print(f"Elemento {i} encontrado (falso positivo)")
        test_passed = False

if test_passed:
    print("Test de search pasado correctamente")


while True:
    print("\nSeleccione una opción:")
    print("1. Insertar elementos")
    print("2. Imprimir elementos")
    print("3. Buscar elemento")
    print("4. Salir")

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
        # Buscar elemento
        key = input("Ingrese la clave a buscar: ")
        result = eh.search(key)
        if result:
            print(f"Elemento encontrado: {result}")
        else:
            print("Elemento no encontrado.")
    elif choice == '4':
        # Salir del programa
        print("Terminando")
        break
    else:
        print("Opción inválida. Intente de nuevo.")