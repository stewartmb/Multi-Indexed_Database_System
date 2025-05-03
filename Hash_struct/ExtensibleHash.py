import pickle
import struct
import os


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

    def _read_header_variable(self, file, index):
        """
        Lee el encabezado del archivo de índice
        """
        file.seek(4 * index)
        data = file.read(4)
        return struct.unpack('i', data)[0]

    def _write_header_variable(self, file, value, index):
        """
        Escribe en el encabezado del archivo de índice
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
            if bucket['local_depth'] != self.global_depth:
                return False
            if bucket['overflow_position'] == -1:
                print("creando overflow")
                overflow_pos = self._read_header_variable(index_file, 2)
                self._write_header_variable(index_file, overflow_pos + 1, 2)
                bucket['overflow_position'] = overflow_pos
                emptyBucket = {'records': [-1, -1, -1],
                               'local_depth': 3,
                               'fullness': 0,
                               'overflow_position': -1}
                index_file.seek(self.header_size + self.hashindex_size + bucket_position * self.BT.size)
                index_file.write(self.BT.to_bytes(bucket))
                index_file.seek(self.header_size + self.hashindex_size + overflow_pos * self.BT.size)
                index_file.write(self.BT.to_bytes(emptyBucket))

            self._insert_value_in_bucket(index_file, bucket['overflow_position'], register_position)
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
            print(f"No se pudo insertar { register_position} en el bucket {bucket_position}, se necesita dividir el bucket")
            index_file.seek(self.header_size + self.hashindex_size + bucket_position * self.BT.size)
            old_bucket = self.BT.from_bytes(index_file.read(self.BT.size))
            # crear nuevos buckets
            bucket1_pos = bucket_position
            bucket2_pos = self._read_header_variable(index_file, 2)
            self._write_header_variable(index_file, bucket2_pos + 1, 2)
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
        size = self._read_header_variable(index_file, 1)
        pos = size
        self._write_record(data_file, size, record)
        self._write_header_variable(index_file, size + 1, 1)
        return pos

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

            printed = []
            for i in range(self.hashindex):
                index_file.seek(self.header_size + i * 4)
                bucket_position = struct.unpack('i', index_file.read(4))[0]
                index_file.seek(self.header_size + self.hashindex_size + bucket_position * self.BT.size)
                bucket = self.BT.from_bytes(index_file.read(self.BT.size))
                if bucket_position in printed:
                    continue
                print(f"Bucket {bin(i)[2:].rjust(bucket['local_depth'],'0')}:")
                print(bucket)
                printed.append(bucket_position)




table_format = {"nombre":"10s", "edad": "f"}
index_key = 1
eh = ExtensibleHash(table_format, index_key)

print(''.join(table_format.values()))

# nums = random.sample(range(100), 100)
#
# for i in nums:
#     eh.insert(["Juan", i])


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