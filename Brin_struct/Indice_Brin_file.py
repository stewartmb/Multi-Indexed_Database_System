import sys
import os
import struct
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *
import math
from Heap_struct.Heap import Heap


# Constantes generales
TAM_ENCABEZAD_PAGE = 4  # Tamaño del encabezado en bytes (cantidad de paginas)
TAM_ENCABEZAD_BRIN = 4  # Tamaño del encabezado en bytes (cantidad de pages)
TAM_ENCABEZAD_DATA = 4  # Tamaño del encabezado en bytes (cantidad de registros)


def get_index_format(M, format_key): # Se hizo con la finalidad que al variar M, el formato del índice cambie automáticamente
    """
    Genera el formato del índice dinámicamente basado en M.
    """
    format = f'b{(M) * format_key}{M * "i"}ii'
    return format

class Index_Page():
    def __init__(self, M=None):
        self.keys = [None] * (M)                # Lista de claves, inicialmente todas son None
        self.childrens = [-1] * M               # Lista de posiciones, inicialmente todas son -1 (no hay hijos)
        self.key_count = 0                      # Contador de claves
        self.M = M                              # Número máximo de claves por página

    def to_bytes(self, format_key, indexp_format):
        # Prepare keys for packing
        packed_keys = []
        for key in self.keys:
            if key is None:
                # For None values, use a sentinel value that fits the format
                if format_key == 'i':  # Entero
                    packed_keys.append(-2147483648)  # -2³¹ (fuera del rango normal)
                elif format_key == 'f':  # Float
                    packed_keys.append(float('nan'))  # NaN representa None
                elif format_key == 'b' or format_key == '?':  # Boolean
                    packed_keys.append(-128)  # Special value for None
                elif 's' in format_key:  # String (ej: '3s')
                    packed_keys.append(b'\x00' * int(format_key[:-1]))  # Bytes nulos
                else:
                    packed_keys.append(0)  # Default fallback
            else:
                # Convertir a bytes si es string
                if 's' in format_key and isinstance(key, str):
                    max_length = int(format_key[:-1])  # Elimina la 's' y convierte a entero
                    truncated_key = key[:max_length]
                    packed_keys.append(truncated_key.encode('utf-8'))
                # Asegurar tipo correcto
                elif format_key == 'i' or format_key == 'q' or format_key == 'Q':
                    packed_keys.append(int(key))
                elif format_key == 'f' or format_key == 'd':
                    packed_keys.append(float(key))
                elif format_key == 'b' or format_key == '?':
                    packed_keys.append(bool(key))
                else:
                    packed_keys.append(key)

        # Prepare all arguments for packing
        pack_args = packed_keys + self.childrens + [self.key_count]
        return struct.pack(indexp_format, *pack_args)
    

    def order_page(self):
        """
        Ordena las claves y sus hijos en una página de índice.
        """
        # Combina claves y hijos en una lista de tuplas
        keys_children = list(zip(self.keys[:self.key_count], self.childrens[:self.key_count]))
        # Ordena la lista por claves
        keys_children.sort(key=lambda x: x[0])
        # Desempaqueta las claves y los hijos ordenados
        self.keys[:self.key_count] = [k for k, _ in keys_children]
        self.childrens[:self.key_count] = [c for _, c in keys_children]


    @classmethod
    def from_bytes(cls, data, M, format_key, indexp_format):
        # Verify data size
        expected_size = struct.calcsize(indexp_format)
        if len(data) != expected_size:
            raise ValueError(f"Data size mismatch: expected {expected_size}, got {len(data)}")

        # Unpack all data
        unpacked = list(struct.unpack(indexp_format, data))

        # Create instance
        instance = cls(leaf=bool(unpacked[0]), M=M)

        # Handle keys
        for i in range(M):
            key_value = unpacked[i + 1]
            if format_key == 'i' or format_key == 'q' or format_key == 'Q':
                instance.keys[i] = key_value if key_value != -2147483648 else None
            elif format_key == 'f' or format_key == 'd':
                instance.keys[i] = key_value if not math.isnan(key_value) else None
            elif format_key == 'b' or format_key == '?':
                instance.keys[i] = key_value if key_value != -128 else None
            elif 's' in format_key:  # String (bytes → str)
                instance.keys[i] = key_value.decode('utf-8').strip('\x00') if key_value != b'\x00' * len(key_value) else None
            else:
                instance.keys[i] = key_value

        # Handle children and metadata
        children_start = M
        instance.childrens = list(unpacked[children_start:children_start + M])
        instance.key_count = unpacked[-1]

        return instance
    

class Indice_Brin():
    def __init__(self, K):
        self.range_values = [None,None]                      # Valor mínimo y máximo de la página (formato: formato_key)
        self.pages = [-1] * K                                # Lista de posiciones de las páginas, inicialmente todas son -1 (no hay páginas)
        self.page_count = 0                                  # Contador de páginas
        self.K = K                                            # Número máximo de páginas por índice BRIN

    def to_bytes(self , format_key, format_index):        
        # Prepare keys for packing
        packed_keys = []
        for key in self.range_values:
            if key is None:
                # For None values, use a sentinel value that fits the format
                if format_key == 'i':  # Entero
                    packed_keys.append(-2147483648)  # -2³¹ (fuera del rango normal)
                elif format_key == 'f':  # Float
                    packed_keys.append(float('nan'))  # NaN representa None
                elif format_key == 'b' or format_key == '?':  # Boolean
                    packed_keys.append(-128)  # Special value for None
                elif 's' in format_key:  # String (ej: '3s')
                    packed_keys.append(b'\x00' * int(format_key[:-1]))  # Bytes nulos
                else:
                    packed_keys.append(0)  # Default fallback
            else:
                # Convertir a bytes si es string
                if 's' in format_key and isinstance(key, str):
                    max_length = int(format_key[:-1])  # Elimina la 's' y convierte a entero
                    truncated_key = key[:max_length]
                    packed_keys.append(truncated_key.encode('utf-8'))
                # Asegurar tipo correcto
                elif format_key == 'i' or format_key == 'q' or format_key == 'Q':
                    packed_keys.append(int(key))
                elif format_key == 'f' or format_key == 'd':
                    packed_keys.append(float(key))
                elif format_key == 'b' or format_key == '?':
                    packed_keys.append(bool(key))
                else:
                    packed_keys.append(key)

        # Prepare all arguments for packing
        pack_args = packed_keys + self.pages + [self.page_count]
        return struct.pack(format_index, *pack_args)
    

    @classmethod
    def from_bytes(cls, data, K, format_key, format_index):
        # Verify data size
        expected_size = struct.calcsize(format_index)
        if len(data) != expected_size:
            raise ValueError(f"Data size mismatch: expected {expected_size}, got {len(data)}")

        # Unpack all data
        unpacked = list(struct.unpack(format_index, data))

        # Create instance
        instance = cls(K=K)

        # Handle keys
        for i in range(2):
            key_value = unpacked[i + 1]
            if format_key == 'i' or format_key == 'q' or format_key == 'Q':
                instance.range_values[i] = key_value if key_value != -2147483648 else None
            elif format_key == 'f' or format_key == 'd':
                instance.range_values[i] = key_value if not math.isnan(key_value) else None
            elif format_key == 'b' or format_key == '?':
                instance.range_values[i] = key_value if key_value != -128 else None
            elif 's' in format_key:  # String (bytes → str)
                instance.range_values[i] = key_value.decode('utf-8').strip('\x00') if key_value != b'\x00' * len(key_value) else None
            else:
                instance.range_values[i] = key_value

        # Handle children and metadata
        instance.pages = unpacked[2:2+K]
        instance.page_count = unpacked[-1]

        return instance
        


class BRIN:
    def __init__(self, table_format: dict , name_key: str ,
                 name_index_file = 'Brin_struct/index_file.bin',
                 name_page_file = 'Brin_struct/page_file.bin',
                 name_data_file = 'Brin_struct/data_file.bin',
                 max_num_pages: int = 100,
                 max_num_keys: int = 100,
                 force_create = False):

        self.index_file = name_index_file
        self.page_file = name_page_file
        self.data_file = name_data_file

        self.RT = RegistroType(table_format, name_key)               # funciones para manejar el registro
        self.format_key = table_format[name_key]                     # Formato de la clave (KEY)
        self.tam_registro = self.RT.size                             # Tamaño del registro

        self.M = max_num_keys                                        # Número máximo de claves por página
        self.K = max_num_pages                                       # Número máximo de páginas por índice BRIN

        self.format_page = get_index_format(self.M, self.format_key)  # Formato de una pagina
        self.format_index = f'{self.format_key*2}{'i' * self.K}i'   # Formato del índice BRIN

        self._initialize_files()                                     # Inicializa los archivos de índice y página
        self.HEAP = Heap(name_data_file, table_format, name_key, force_create=force_create)

    def _initialize_files(self):
        """
        Inicializa los archivos de índice y página.
        """
        # Crear o limpiar el archivo de índice
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'wb') as f:
                f.write(struct.pack('i', 0)) 
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'wb') as f:
                f.write(struct.pack('i', 0))
        if not os.path.exists(self.page_file):
            with open(self.page_file, 'wb') as f:
                f.write(struct.pack('i', 0))

    ### MANEJO DE ENCABEZADOS ###

    ## Encabezado de archivo para paginas ##
    def _read_header_page(self):
        """
        Lee el encabezado del archivo de páginas.
        """
        with open(self.page_file, 'rb') as f:
            header = f.read(TAM_ENCABEZAD_PAGE)
            if not header:
                return 0
            return struct.unpack('i', header)[0]

    def _write_header_page(self, num_pages):
        """
        Escribe el encabezado del archivo de páginas.
        """
        with open(self.page_file, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack('i', num_pages))
    
    ## Encabezado de archivo para indice BRIN ##
    def _read_header_index(self):
        """
        Lee el encabezado del archivo de índice BRIN.
        """
        with open(self.index_file, 'rb') as f:
            header = f.read(TAM_ENCABEZAD_BRIN)
            if not header:
                return 0
            return struct.unpack('i', header)[0]
        
    def _write_header_index(self, num_indexes):
        """
        Escribe el encabezado del archivo de índice BRIN.
        """
        with open(self.index_file, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack('i', num_indexes))
    
    ## Encabezado de archivo para datos ##
    def _read_header_data(self):
        """
        Lee el encabezado del archivo de datos.
        """
        with open(self.data_file, 'rb') as f:
            header = f.read(TAM_ENCABEZAD_DATA)
            if not header:
                return 0
            return struct.unpack('i', header)[0]
    
    def _write_header_data(self, num_records):
        """
        Escribe el encabezado del archivo de datos.
        """
        with open(self.data_file, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack('i', num_records))

    ### MANEJO DE DATOS (CASE INDEPENT) ###

    def _read_data_header(self):
        """
        Lee el encabezado del archivo de datos.
        """
        with open(self.data_file, 'rb') as f:
            f.seek(0)
            header = f.read(TAM_ENCABEZAD_DATA)
            size = struct.unpack('i', header)[0]
        return size
    
    def add_record(self, record : list):
        """
        Agrega un nuevo registro al final del archivo de datos y actualiza el encabezado.
        """
        with open(self.data_file, 'r+b') as f:
            # Leer el tamaño actual desde el encabezado
            f.seek(0)
            header = f.read(TAM_ENCABEZAD_DATA)
            size = struct.unpack('i', header)[0]
            # Calcular el offset para el nuevo registro
            offset = TAM_ENCABEZAD_DATA + size * self.RT.size
            f.seek(offset)
            f.write(self.RT.to_bytes(record))
            # Actualizar el encabezado con el nuevo tamaño
            f.seek(0)
            f.write(struct.pack('i', size + 1))
            return size

    def _read_record(self, pos : int):
        """
        Lee un registro desde el archivo de datos en la posición dada.
        """
        with open(self.data_file, 'rb') as f:
            offset = TAM_ENCABEZAD_DATA + pos * self.RT.size
            f.seek(offset)
            data = f.read(self.RT.size)
            return self.RT.from_bytes(data)



        





