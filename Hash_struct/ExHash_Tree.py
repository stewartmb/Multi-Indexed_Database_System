import pickle
import struct
import os
import random

from PIL.ImageChops import offset


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


    def to_bytes(self, treeNode):
        """
        Convierte el nodo a bytes.
        """
        return struct.pack(self.FORMAT,
                            treeNode['bucket_position'],
                            treeNode['left'],
                            treeNode['right'],
                            treeNode['depth']
                           )

    def from_bytes(self, data):
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

    def read(self, file, index):
        """
        Lee el encabezado del archivo de índice
        """
        file.seek(4 * index)
        data = file.read(4)
        return struct.unpack('i', data)[0]

    def write(self, file, value, index):
        """
        Escribe en el encabezado del archivo de índice
        """
        file.seek(4 * index)
        file.write(struct.pack('i', value))

class ExtensibleHash:
    def __init__(self, table_format, index_key,
                 buckets_file_name='hash_buckets.bin',
                 index_file_name='hash_index.bin',
                 data_file_name='data_file.bin',
                 global_depth=3,
                 max_records=3):
        self.index_file = index_file_name
        self.buckets_file = buckets_file_name
        self.data_file = data_file_name
        self.global_depth = global_depth
        self.max_records = max_records

        self.NT = TreeNodeType()
        self.RT = RegistroType(table_format, index_key)
        self.BT = BucketType(max_records)
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
        print(record)
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

        print(f"bucket_position: {bucket_position}")

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
                print(f"reinserta {old_bucket['records'][i]}")
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
        index_hash = getbits(self.RT.get_key(record), self.global_depth)
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

            index_hash = getbits(self.RT.get_key(record), self.global_depth)
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



class ExtensibleHash1:
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

        self.RT = RegistroType(table_format,index_key)
        self.BT = BucketType(max_records)
        self._initialize_files(global_depth, force=True)


    def search(self, key):
        """
        Busca un registro en el hash extensible.
        :return: True si se encontro, False si no se encontro
        """
        index_hash = getbits(key, self.global_depth)
        bucket_index_position = int(index_hash, 2)

        with open(self.index_file, 'r+b') as index_file, open(self.data_file, 'r+b') as data_file:
            index_file.seek(self.header_size + bucket_index_position * 4)
            bucket_position = struct.unpack('i', index_file.read(4))[0]
            index_file.seek(self.header_size + self.hashindex_size + bucket_position * self.BT.size)
            bucket = self.BT.from_bytes(index_file.read(self.BT.size))
            # Iterar registros
            goto_overflow = True
            while goto_overflow:
                for i in range(bucket['fullness']):
                    data_file.seek(bucket['records'][i] * self.RT.size)
                    registro = self.RT.from_bytes(data_file.read(self.RT.size))
                    if self.RT.get_key(registro) == key:
                        return registro
                if bucket['overflow_position'] != -1:
                    bucket_position = bucket['overflow_position']
                    index_file.seek(self.header_size + self.hashindex_size + bucket_position * self.BT.size)
                    bucket = self.BT.from_bytes(index_file.read(self.BT.size))
                else:
                    goto_overflow = False




table_format = {"nombre":"10s", "edad": "i"}
index_key = 1
eh = ExtensibleHash(table_format, index_key)

print(''.join(table_format.values()))

nums = random.sample(range(50), 50)

for i in nums:
    eh.insert(["amen", i])


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
        key = int(input("Ingrese la clave a buscar: "))
        result = eh.search(key)
        if result:
            print(f"Elemento encontrado: {result}")
        else:
            print("Elemento no encontrado.")
    elif choice == '4':
        # Salir del programa
        print("¡Adiós!")
        break
    else:
        print("Opción inválida. Intente de nuevo.")