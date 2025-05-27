import pickle
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *
from Heap_struct.Heap import *

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
    def __init__(self, power):
        self.length = 2**power
        self.FORMAT = 'i'*self.length + '?'
        self.size = struct.calcsize(self.FORMAT)


    def to_bytes(self, treeNode: list, isleaf: bool) -> bytes:
        """
        Convierte el nodo a bytes.
        """
        return struct.pack(self.FORMAT,
                            *treeNode,
                            isleaf
                           )

    def from_bytes(self, data: bytes) -> tuple:
        """
        Convierte bytes a un nodo.
        """
        unpacked = struct.unpack(self.FORMAT, data)
        return list(unpacked[:-1]), unpacked[-1]

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
    def __init__(self, table_format: dict,
                 key: str,
                 buckets_file_name: str,
                 index_file_name: str,
                 data_file_name: str,
                 GD: int = 4,
                 max_records_per_bucket: int = 4,
                 power: int = 4,
                 force_create: bool = False):
        
        if power < 1:
            print("ERROR: power debe ser mayor a 0")
            raise ValueError("power debe ser mayor a 0")
        if power > 10:
            print("WARN: seguro?")
        if power > 20:
            print("ERROR: power no puede ser mayor a 20")
            raise ValueError("power no puede ser mayor a 20")

        global_depth = GD*power
        self.index_file = index_file_name
        self.buckets_file = buckets_file_name
        self.global_depth = global_depth
        self.max_records = max_records_per_bucket
        self.power = power

        self.NT = TreeNodeType(power)
        self.RT = RegistroType(table_format, key)
        self.BT = BucketType(max_records_per_bucket)
        self.HEAP = Heap(table_format, key, data_file_name, force_create=force_create)
        self.Header = HeaderType()

        self._initialize_files(global_depth, power, force=force_create)

    # utility functions
    def _initialize_files(self, global_depth, power, force=False):
        """
        Inicializa los archivos de índice y datos.
        """
        if force or (not os.path.exists(self.index_file)) or (os.path.getsize(self.index_file) < self.Header.size):
            with open(self.index_file, 'wb') as f:
                # 0 = global_depth, 1 = data_last, 2 = bucket_last, 3 = node_last
                f.write(struct.pack('i', global_depth))
                f.write(struct.pack('i', 0))
                f.write(struct.pack('i', 2**power))
                f.write(struct.pack('i', 1 + 2**power))
                # root
                f.write(self.NT.to_bytes([i+1 for i in range(2**power)], isleaf=False))
                for i in range(2**power):
                    f.write(self.NT.to_bytes([i]*(2**power), isleaf=True))


        if force or (not os.path.exists(self.buckets_file)) or (os.path.getsize(self.buckets_file) < self.Header.size):
            with open(self.buckets_file, 'wb') as f:
                # [0,0,0...0,0,0] + [localdepth, fullness, overflowPosition]
                for i in range(2**power):
                    f.write(struct.pack(self.BT.FORMAT, *([-1] * self.max_records + [1,0,-1])))

    def _insert_value_in_bucket(self, buckets_file, index_file, bucket_position, data_position):
        """
        Inserta la posición del dato en el bucket. Si el bucket está lleno y en profundidad máxima,
        se maneja con overflow por push-front. Si no está en profundidad máxima, retorna False para disparar un split.
        """
        buckets_file.seek(bucket_position * self.BT.size)
        bucket = self.BT.from_bytes(buckets_file.read(self.BT.size))

        # Si el bucket no está lleno, simplemente insertamos
        if bucket['fullness'] < self.max_records:
            bucket['records'][bucket['fullness']] = data_position
            bucket['fullness'] += 1
            buckets_file.seek(bucket_position * self.BT.size)
            buckets_file.write(self.BT.to_bytes(bucket))
            return True

        # Si el bucket está lleno pero su profundidad es menor que la global → split
        if bucket['local_depth'] < self.global_depth:
            return False

        # Si está lleno y en profundidad máxima → manejar con push-front de overflow
        new_bucket_pos = self.Header.read(index_file, 2)
        self.Header.write(index_file, new_bucket_pos + 1, 2)

        new_bucket = {
            'records': [-1] * self.max_records,
            'fullness': 1,
            'local_depth': self.global_depth,
            'overflow_position': bucket['overflow_position']  # encadena al antiguo primer overflow
        }
        new_bucket['records'][0] = data_position

        # El bucket base apunta ahora al nuevo overflow (nuevo "head" de la cadena)
        bucket['overflow_position'] = new_bucket_pos

        # Escribimos ambos buckets
        buckets_file.seek(bucket_position * self.BT.size)
        buckets_file.write(self.BT.to_bytes(bucket))

        buckets_file.seek(new_bucket_pos * self.BT.size)
        buckets_file.write(self.BT.to_bytes(new_bucket))

        return True



    def _add_to_hash(self, buckets_file, index_file, data_position, index_hash: str):
        node_index = 0
        k = 1
        # Busca el nodo correspondiente en el árbol de índice
        while True:
            index_file.seek(self.Header.size + node_index * self.NT.size)
            node, isleaf = self.NT.from_bytes(index_file.read(self.NT.size))
            if not isleaf:
                selection = 0
                # Si no es hoja, seguimos bajando por el árbol
                for i in range(self.power): 
                    if index_hash[self.power-i] == '1':
                        selection += 2**(self.power - i - 1)
                node_index = node[selection]
            else:
                # Si es hoja, hemos encontrado el bucket
                bucket_position = node[0]
                break
            

        inserted = self._insert_value_in_bucket(buckets_file, index_file, bucket_position, data_position)
        if not inserted:
            #print("Splitting")
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
                record = self.HEAP.read(old_bucket['records'][i])
                if record != None:
                    self._aux_insert(buckets_file, index_file, record, old_bucket['records'][i])

            # reinserta el nuevo registro
            record = self.HEAP.read(data_position)
            if record != None:
                self._aux_insert(buckets_file, index_file, record, data_position)

    def _find_in_bucket(self, bucket, key, matches):
        """
        Busca un registro en un bucket.
        """
        for i in range(bucket['fullness']):
            record = self.HEAP.read(bucket['records'][i])
            if record != None:
                if self.RT.get_key(record) == key:
                    matches.append(bucket['records'][i])
        return matches

    # Funciones recursivas
    def _aux_insert(self, buckets_file, index_file, record, data_position):
        """
        Funcion para reinsertar recursivamente los registros que se dividieron
        """
        index_hash = get_bits(self.RT.get_key(record), self.global_depth)
        self._add_to_hash(buckets_file, index_file, data_position, index_hash)

    def _aux_search(self, buckets_file, index_file, node_index, index_hash, key):
        """
        Funcion recursiva de busqueda
        """
        index_file.seek(self.Header.size + node_index * self.NT.size)
        node = self.NT.from_bytes(index_file.read(self.NT.size))
        if node['bucket_position'] == -1:
            if index_hash[-1] == '0':
                return self._aux_search(buckets_file, index_file, node['left'], index_hash[:-1], key)
            else:
                return self._aux_search(buckets_file, index_file, node['right'], index_hash[:-1], key)
        else:
            matches = []
            buckets_file.seek(node['bucket_position'] * self.BT.size)
            bucket = self.BT.from_bytes(buckets_file.read(self.BT.size))
            self._find_in_bucket(bucket, key, matches)

            overflow_position = bucket['overflow_position']
            while overflow_position != -1:
                buckets_file.seek(overflow_position * self.BT.size)
                bucket = self.BT.from_bytes(buckets_file.read(self.BT.size))
                self._find_in_bucket(bucket, key, matches)
                overflow_position = bucket['overflow_position']
            return matches

    def insert(self, record, data_position=None):
        """
        Inserta un registro en el hash extensible.
        :param record: registro a insertar
        :param data_position: posicion del registro en el archivo de datos.
        Si no se especifica, se agrega al final del archivo (funcionalidad como indice principal).
        """
        with open(self.index_file, 'r+b') as index_file, \
               open(self.buckets_file, 'r+b') as buckets_file:
            if data_position is None:
                data_position = self.HEAP.insert(record)

            index_hash = get_bits(self.RT.get_key(record), self.global_depth)
            self._add_to_hash(buckets_file, index_file, data_position, index_hash)

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
                open(self.buckets_file, 'r+b') as buckets_file:
            index_hash = get_bits(key, self.global_depth)
            index_file.seek(self.Header.size)
            root = self.NT.from_bytes(index_file.read(self.NT.size))
            if index_hash[-1] == '0':
                return self._aux_search(buckets_file, index_file, root['left'], index_hash[:-1], key)
            else:
                return self._aux_search(buckets_file, index_file, root['right'], index_hash[:-1], key)
            