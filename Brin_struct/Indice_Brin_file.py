import sys
import os
import struct
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *
import math
from Heap_struct.Heap import Heap


# Constantes generales
TAM_ENCABEZAD_PAGE = 4  # Tamaño del encabezado en bytes (cantidad de paginas)
TAM_ENCABEZAD_BRIN = 5  # Tamaño del encabezado en bytes (cantidad de pages)
TAM_ENCABEZAD_DATA = 4  # Tamaño del encabezado en bytes (cantidad de registros)


def get_index_format(M, format_key): # Se hizo con la finalidad que al variar M, el formato del índice cambie automáticamente
    """
    Genera el formato del índice dinámicamente basado en M.
    """
    format = f'{(M) * format_key}{M * "i"}{format_key * 2}i?i'
    return format

class Index_Page():
    def __init__(self, M=None):
        self.keys = [None] * (M)                # Lista de claves, inicialmente todas son None
        self.childrens = [-1] * M               # Lista de posiciones, inicialmente todas son -1 (no hay hijos)
        self.range_values = [None, None]        # Valores mínimo y máximo de la página
        self.key_count = 0                      # Contador de claves
        self.is_order = True                    # Indica si la página está ordenada
        self.father_brin = -1                   # Posición del padre, inicialmente -1 (sin padre)
        self.M = M                              # Número máximo de claves por página

    def to_bytes(self, format_key, indexp_format):
        # Prepare keys for packing

        def binary_format(list):
            packed_keys = []
            for key in list:
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
            return packed_keys
        
        # Empaquetar claves
        packed_keys1 = binary_format(self.keys)
        packed_keys2 = binary_format(self.range_values)

        # Prepare all arguments for packing
        pack_args = packed_keys1 + self.childrens + packed_keys2 + [self.key_count, self.is_order , self.father_brin]
        return struct.pack(indexp_format, *pack_args)


    @classmethod
    def from_bytes(cls, data, M, format_key, indexp_format):
        # Verify data size
        expected_size = struct.calcsize(indexp_format)
        if len(data) != expected_size:
            raise ValueError(f"Data size mismatch: expected {expected_size}, got {len(data)}")

        # Unpack all data
        unpacked = list(struct.unpack(indexp_format, data))

        # Create instance
        instance = cls(M=M)

        # Handle keys
        for i in range(M):
            key_value = unpacked[i]
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
        instance.childrens = list(unpacked [M: M + M])
        for i in range(2* M, 2 * M + 2):
            value = unpacked[i]
            if format_key == 'i' or format_key == 'q' or format_key == 'Q':
                instance.range_values[i - 2 * M] = value if value != -2147483648 else None
            elif format_key == 'f' or format_key == 'd':
                instance.range_values[i - 2 * M] = value if not math.isnan(value) else None
            elif format_key == 'b' or format_key == '?':
                instance.range_values[i - 2 * M] = value if value != -128 else None
            elif 's' in format_key:
                instance.range_values[i - 2 * M] = value.decode('utf-8').strip('\x00') if value != b'\x00' * len(value) else None
        instance.key_count = unpacked[-3]
        instance.is_order = unpacked[-2]
        instance.father_brin = unpacked[-1]

        return instance

    def binary_find_index(self, key):
        """
        Encuentra el índice donde se debe descender por biseccion.
        """
        low = 0
        high = self.key_count - 1
        while low <= high:
            mid = (low + high) // 2
            if self.keys[mid] < key:
                low = mid + 1
            else:
                high = mid - 1
        return low

class Indice_Brin():
    def __init__(self, K):
        self.range_values = [None,None]                      # Valor mínimo y máximo de la página (formato: formato_key)
        self.pages = [-1] * K                                # Lista de posiciones de las páginas, inicialmente todas son -1 (no hay páginas)
        self.page_count = 0                                  # Contador de páginas
        self.is_order = True                                 # Indica si el índice BRIN está ordenado
        self.K = K                                           # Número máximo de páginas por índice BRIN

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
        pack_args = packed_keys + self.pages + [self.page_count, self.is_order]
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
            key_value = unpacked[i]
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
        instance.page_count = unpacked[-2]
        instance.is_order = unpacked[-1]

        return instance
    

class BRIN:
    def __init__(self, table_format: dict , name_key: str ,
                 name_index_file = 'Brin_struct/index_file.bin',
                 name_page_file = 'Brin_struct/page_file.bin',
                 name_data_file = 'Brin_struct/data_file.bin',
                 max_num_pages: int = 70,
                 max_num_keys: int = 35,
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
        self.tam_page = struct.calcsize(self.format_page)              # Tamaño de una página
        self.format_index = f'{self.format_key*2}{'i' * self.K}i?'   # Formato del índice BRIN
        self.tam_index = struct.calcsize(self.format_index)              # Tamaño del índice BRIN

        self._initialize_files()                                     # Inicializa los archivos de índice y página
        self.HEAP = Heap(table_format, name_key, name_data_file, force_create=force_create)

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
                f.write(struct.pack('i?', 0, True))
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
            num_brins, is_order = struct.unpack('i?', header)
            return num_brins, is_order

    def _write_header_index(self, num_indexes , is_order):
        """
        Escribe el encabezado del archivo de índice BRIN.
        """
        with open(self.index_file, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack('i?', num_indexes , is_order))
    
    def _update_order(self, is_order):
        """
        Actualiza el orden del índice BRIN en el encabezado.
        """
        num_brins, _ = self._read_header_index()
        self._write_header_index(num_brins, is_order)

    ### MANEJO DE PÁGINAS DE ÍNDICE ###

    def _read_page(self, page_number):
        """
        Lee una página del archivo de páginas.
        """
        with open(self.page_file, 'rb') as f:
            f.seek(TAM_ENCABEZAD_PAGE + page_number * self.tam_page)
            data = f.read(self.tam_page)
            return Index_Page.from_bytes(data, self.M, self.format_key, self.format_page)
        
    def _write_page(self, page_number, page : Index_Page):
        """
        Escribe una página en el archivo de páginas.
        """
        with open(self.page_file, 'r+b') as f:
            f.seek(TAM_ENCABEZAD_PAGE + page_number * self.tam_page)
            f.write(page.to_bytes(self.format_key, self.format_page))
    
    def _add_page(self, page):
        """
        Agrega una nueva página al archivo de páginas.
        """
        num_pages = self._read_header_page()
        self._write_page(num_pages, page)
        self._write_header_page(num_pages + 1)
        return num_pages
    
    ### MANEJO DE INDICES BRIN ###
    def _read_brin(self, index_number):
        """
        Lee un índice BRIN del archivo de índice.
        """
        with open(self.index_file, 'rb') as f:
            f.seek(TAM_ENCABEZAD_BRIN + index_number * self.tam_index)
            data = f.read(self.tam_index)
            return Indice_Brin.from_bytes(data, self.K, self.format_key, self.format_index)
        
    def _write_brin(self, index_number, brin : Indice_Brin):
        """
        Escribe un índice BRIN en el archivo de índice.
        """
        with open(self.index_file, 'r+b') as f:
            f.seek(TAM_ENCABEZAD_BRIN + index_number * self.tam_index)
            f.write(brin.to_bytes(self.format_key, self.format_index))
    
    def _add_brin(self , key , pos_new_record):
        """
        Agrega un nuevo índice BRIN al archivo de índice.
        """
        num_brins, is_order = self._read_header_index()

        brin = Indice_Brin(self.K)
        brin.range_values[0] = key
        brin.range_values[1] = key
        
        # Generar la pagina 
        page = Index_Page(self.M)
        page.keys[0] = key
        page.childrens[0] = pos_new_record
        page.key_count = 1
        page.range_values[0] = key
        page.range_values[1] = key
        page.father_brin = num_brins
        
        # Agrega la página al índice BRIN
        pos_page = self._add_page(page)
        brin.pages[0] = pos_page
        brin.page_count = 1

        if num_brins -1 >= 0:
            # Actualizar order
            prev_brin = self._read_brin(num_brins - 1)
            if prev_brin.range_values[1] > key:
                is_order = False  # Si el nuevo índice no está ordenado, actualizar el encabezado
        self._write_brin(num_brins, brin)
        self._write_header_index(num_brins + 1, is_order)

        page = self._read_page(pos_page)
        brin = self._read_brin(num_brins)
        return num_brins , pos_page
    
    def _update_ranges(self, pos_page : Index_Page, key):
        """
        Actualiza los valores de rango de una página.
        """
        page = self._read_page(pos_page)

        # Actualiza los valores de rango de la página
        if key >= page.range_values[1]:
            page.range_values[1] = key
        else:
            page.is_order = False  # Si se actualiza el valor mínimo, la página ya no está ordenada
        if key <= page.range_values[0]:
            page.range_values[0] = key
        
        # Actualiza el padre del índice BRIN
        father_brin = self._read_brin(page.father_brin)
        if key >= father_brin.range_values[1]:
            father_brin.range_values[1] = key
        else:
            father_brin.is_order = False
        
        if key <= father_brin.range_values[0]:
            father_brin.range_values[0] = key

        prev_brin = self._read_brin(page.father_brin - 1) if page.father_brin > 0 else None

        if prev_brin and key < prev_brin.range_values[0]:
            self._update_order(False)

        self._write_brin(page.father_brin, father_brin)  # Actualiza el índice BRIN del padre
        self._write_page(pos_page, page)  # Actualiza la página en el archivo de páginas

    def binary_search_all(self, key):
        """
        Encuentra el índice donde se debe evaluar el brin.
        """
        # Leer todas los brins del archivo de índice
        low = 0
        first_occurrence = -1   # Para guardar el primer x encontrado
        floor_index = -1        # Para guardar el mayor valor < x    
        high = self._read_header_index()[0] - 1
        while low <= high:
            mid = (low + high) // 2
            min_value = self._read_brin(mid).range_values[0]
            if min_value == key:
                first_occurrence = mid
                high = mid - 1
            elif min_value < key:
                floor_index = mid
                low = mid + 1
            else:
                high = mid - 1
        return first_occurrence if first_occurrence != -1 else floor_index

    def binary_find_index(self, brin : Indice_Brin, key):
        """
        Encuentra el índice donde se debe descender por biseccion.
        """
        low = 0
        high = brin.page_count - 1
        first_occurrence = -1   # Para guardar el primer x encontrado
        floor_index = -1        # Para guardar el mayor valor < x    
        while low <= high:
            mid = (low + high) // 2
            pos_page = brin.pages[mid]
            page = self._read_page(pos_page)  # Leer la página correspondiente
            min_value = page.range_values[0]
            if min_value == key:
                first_occurrence = mid
                high = mid - 1
            elif min_value < key:
                floor_index = mid
                low = mid + 1
            else:
                high = mid - 1
        return first_occurrence if first_occurrence != -1 else floor_index



    def print_all_brins(self):
        """
        Imprime todos los índices BRIN del archivo de índice.
        """
        num_brins, is_order = self._read_header_index()
        if num_brins == 0:
            print("No hay índices BRIN.")
            return
        
        # Imprime el encabezado del índice BRIN
        print(f"Encabezado del índice BRIN: Número de BRINs: {num_brins}, Ordenado: {is_order}")
        
        for i in range(num_brins):
            brin = self._read_brin(i)
            print(f"BRIN {i}: Rango: {brin.range_values}, Páginas: {brin.page_count}, Ordenado: {brin.is_order}")
            for j in range(brin.page_count):
                pos_page = brin.pages[j]
                page = self._read_page(pos_page)
                print(f"  Página {j}: Claves: {page.keys[:page.key_count]}, Hijos: {page.childrens[:page.key_count]}, Rango: {page.range_values}, Ordenada: {page.is_order}")


    ### FUNCIONES ###

    def add(self, record: list = None, pos_new_record :int = None):
        """
        Inserta un registro en el árbol B+.
        """
        # Le el encabezado del archivo de índice
        if record is not None and pos_new_record is not None:
            return "Error: Debe ingresar solo uno de los dos argumentos (record o pos_new_record)"
        elif record is None and pos_new_record is None:
            return "Error: Debe ingresar uno de los dos argumentos (record o pos_new_record)"
        elif record is not None:
            pos_new_record = self.HEAP.insert(record)
            key = self.RT.get_key(record)  # Obtiene la clave del registro

        else:
            record = self.HEAP.read(pos_new_record)
            key = self.RT.get_key(record)  # Obtiene la clave del registro


        num_brins, is_order = self._read_header_index()

        if num_brins == 0:
            # Si no hay índices BRIN, crea uno nuevo
            return self._add_brin(key, pos_new_record)
        
        else:
            # Lee el último índice BRIN
            pos_brin = num_brins - 1
            brin = self._read_brin(pos_brin)

            # Lee la última página del índice BRIN
            pos_last_page = self._read_header_page() - 1
            last_page = self._read_page(pos_last_page)


            # Verifica si hay espacio en su ultima pagina
            if last_page.key_count < self.M:
                # Si hay espacio, agrega el registro a la última página
                last_page.keys[last_page.key_count] = key
                last_page.childrens[last_page.key_count] = pos_new_record
                last_page.key_count += 1
                self._write_page(pos_last_page, last_page)
                self._update_ranges(pos_last_page, key)
                last_page = self._read_page(pos_last_page)  # Leer la página actualizada
                return
            
            else:
                # Si no hay espacio, verifica si se puede crear una nueva pagina al índice BRIN
                if brin.page_count < self.K:
                    # Si hay espacio en el índice BRIN, crea una nueva página
                    new_page = Index_Page(self.M)
                    new_page.keys[0] = key
                    new_page.childrens[0] = pos_new_record
                    new_page.key_count = 1
                    new_page.range_values[0] = key
                    new_page.range_values[1] = key
                    new_page.father_brin = pos_brin

                    # Agrega la nueva página al índice BRIN
                    pos_new_page = self._add_page(new_page)

                    brin.pages[brin.page_count] = pos_new_page
                    brin.page_count += 1
                    self._write_brin(pos_brin, brin)
                    self._update_ranges(pos_new_page, key)
                    return
                else:
                    # Si no hay espacio en el índice BRIN, crea un nuevo índice BRIN
                    pos_new_brin = self._add_brin(key, pos_new_record)
                    return
                        
    
    def search(self, key):
        """
        Busca un registro específico en el índice BRIN.
        """
        num_brins, is_order = self._read_header_index()
        results = []
        if num_brins == 0:
            return results
        
        # Buscar brins que contengan el rango del key
        list_pos_brin = []
        if is_order:
            # Si el índice BRIN está ordenado, realiza una búsqueda binaria
            pos_brin = self.binary_search_all(key)
            for i in range(pos_brin, num_brins):
                brin = self._read_brin(i)
                if brin.range_values[0] <= key <= brin.range_values[1]:
                    list_pos_brin.append(i)
                elif brin.range_values[0] > key:
                    break
        else:
            # Si el índice BRIN no está ordenado, busca secuencialmente
            for i in range(num_brins):
                brin = self._read_brin(i)
                if brin.range_values[0] <= key <= brin.range_values[1]:
                    list_pos_brin.append(i)
        

        # Buscar en las páginas de los brins encontrados 
        for pos_brin in list_pos_brin:
            brin = self._read_brin(pos_brin)
            pos_page = self.binary_find_index(brin, key)
            # Si el brin está ordenado, busca en la página correspondiente
            if brin.is_order:
                for i in range(pos_page, brin.page_count):
                    pos_page = brin.pages[i]
                    page = self._read_page(pos_page)
                    if page.range_values[0] <= key <= page.range_values[1]:
                        
                        # Si la página contiene el key, busca en las claves
                        if page.is_order:
                            # Si la página está ordenada, busca el índice del key
                            index = page.binary_find_index(key)
                            for j in range(index, page.key_count):
                                if page.keys[j] == key:
                                    results.append(page.childrens[j])
                                elif page.keys[j] > key:
                                    break
                        else:
                            # Si la página no está ordenada, busca secuencialmente
                            for j in range(page.key_count):
                                if page.keys[j] == key:
                                    results.append(page.childrens[j])

                    elif page.range_values[0] > key:
                        break
                            
            else:
                # Si el brin no está ordenado, busca en todas las páginas
                for i in range(brin.page_count):
                    pos_page = brin.pages[i]
                    page = self._read_page(pos_page)
                    if page.range_values[0] <= key <= page.range_values[1]:
                        if page.is_order:
                            # Si la página está ordenada, busca el índice del key
                            index = page.binary_find_index(key)
                            for j in range(index, page.key_count):
                                if page.keys[j] == key:
                                    results.append(page.childrens[j])
                                elif page.keys[j] > key:
                                    break
                        else:
                            # Si la página no está ordenada, busca secuencialmente
                            for j in range(page.key_count):
                                if page.keys[j] == key:
                                    results.append(page.childrens[j])
        return results
    

    def search_range(self, key1 , key2):
        """
        Busca un registro específico en el índice BRIN.
        """
        num_brins, is_order = self._read_header_index()
        results = []
        if num_brins == 0:
            return results
        
        # Buscar brins que contengan el rango del key
        list_pos_brin = []
        if is_order:
            # Si el índice BRIN está ordenado, realiza una búsqueda binaria
            pos_brin = self.binary_search_all(key1)
            for i in range(pos_brin, num_brins):
                brin = self._read_brin(i)
                if max (brin.range_values[0], key1) <= min(brin.range_values[1], key2):
                    list_pos_brin.append(i)
                elif brin.range_values[0] > key2:
                    break
        else:
            # Si el índice BRIN no está ordenado, busca secuencialmente
            for i in range(num_brins):
                brin = self._read_brin(i)
                if max (brin.range_values[0], key1) <= min(brin.range_values[1], key2):
                    list_pos_brin.append(i)
        

        # Buscar en las páginas de los brins encontrados 
        for pos_brin in list_pos_brin:
            brin = self._read_brin(pos_brin)
            pos_page = self.binary_find_index(brin, key1)
            # Si el brin está ordenado, busca en la página correspondiente
            if brin.is_order:
                for i in range(pos_page, brin.page_count):
                    pos_page = brin.pages[i]
                    page = self._read_page(pos_page)
                    if max (page.range_values[0], key1) <= min(page.range_values[1], key2):
                        
                        # Si la página contiene el key, busca en las claves
                        if page.is_order:
                            # Si la página está ordenada, busca el índice del key
                            index = page.binary_find_index(key1)
                            for j in range(index, page.key_count):
                                if key1 <= page.keys[j] <= key2:
                                    results.append(page.childrens[j])
                                elif page.keys[j] > key2:
                                    break
                        else:
                            # Si la página no está ordenada, busca secuencialmente
                            for j in range(page.key_count):
                                if key1 <= page.keys[j] <= key2:
                                    results.append(page.childrens[j])

                    elif page.range_values[0] > key2:
                        break
                            
            else:
                # Si el brin no está ordenado, busca en todas las páginas
                for i in range(brin.page_count):
                    pos_page = brin.pages[i]
                    page = self._read_page(pos_page)
                    if max (page.range_values[0], key1) <= min(page.range_values[1], key2):
                        if page.is_order:
                            # Si la página está ordenada, busca el índice del key
                            index = page.binary_find_index(key1)
                            for j in range(index, page.key_count):
                                if key1 <= page.keys[j] <= key2:
                                    results.append(page.childrens[j])
                                elif page.keys[j] > key2:
                                    break
                        else:
                            # Si la página no está ordenada, busca secuencialmente
                            for j in range(page.key_count):
                                if key1 <= page.keys[j] <= key2:
                                    results.append(page.childrens[j])
        return results
    

    def delete(self, key):
        """
        Elimina un registro específico del índice BRIN.
        """
        results = self.search(key)
        if not results:
            return "No se encontró el registro con la clave especificada."

        num_brins, is_order = self._read_header_index()
        results = []
        if num_brins == 0:
            return 
        
        # Buscar brins que contengan el rango del key
        list_pos_brin = []
        if is_order:
            # Si el índice BRIN está ordenado, realiza una búsqueda binaria
            pos_brin = self.binary_search_all(key)
            for i in range(pos_brin, num_brins):
                brin = self._read_brin(i)
                if brin.range_values[0] <= key <= brin.range_values[1]:
                    list_pos_brin.append(i)
                elif brin.range_values[0] > key:
                    break
        else:
            # Si el índice BRIN no está ordenado, busca secuencialmente
            for i in range(num_brins):
                brin = self._read_brin(i)
                if brin.range_values[0] <= key <= brin.range_values[1]:
                    list_pos_brin.append(i)
        

        # Buscar en las páginas de los brins encontrados 
        for pos_brin in list_pos_brin:
            brin = self._read_brin(pos_brin)
            pos_page = self.binary_find_index(brin, key)
            # Si el brin está ordenado, busca en la página correspondiente
            if brin.is_order:
                for i in range(pos_page, brin.page_count):
                    pos_page = brin.pages[i]
                    page = self._read_page(pos_page)
                    if page.range_values[0] <= key <= page.range_values[1]:
                        
                        # Si la página contiene el key, busca en las claves
                        if page.is_order:
                            # Si la página está ordenada, busca el índice del key
                            index = page.binary_find_index(key)
                            for j in range(index, page.key_count):
                                if page.keys[j] == key:
                                    page.keys[j] =  float('nan')  # Marca la clave como eliminada
                                elif page.keys[j] > key:
                                    break
                        else:
                            # Si la página no está ordenada, busca secuencialmente
                            for j in range(page.key_count):
                                if page.keys[j] == key:
                                    page.keys[j] =  float('nan')  # Marca la clave como eliminada

                    elif page.range_values[0] > key:
                        break
                            
            else:
                # Si el brin no está ordenado, busca en todas las páginas
                for i in range(brin.page_count):
                    pos_page = brin.pages[i]
                    page = self._read_page(pos_page)
                    if page.range_values[0] <= key <= page.range_values[1]:
                        if page.is_order:
                            # Si la página está ordenada, busca el índice del key
                            index = page.binary_find_index(key)
                            for j in range(index, page.key_count):
                                if page.keys[j] == key:
                                    page.keys[j] =  float('nan')  # Marca la clave como eliminada
                                elif page.keys[j] > key:
                                    break
                        else:
                            # Si la página no está ordenada, busca secuencialmente
                            for j in range(page.key_count):
                                if page.keys[j] == key:
                                    page.keys[j] =  float('nan')  # Marca la clave como eliminada
        return



                    
    



        


