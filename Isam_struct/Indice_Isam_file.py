import sys
import os
import struct
import csv
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *
import math
import heapq
from sympy import symbols, Eq, solve
from Heap_struct.Heap import Heap
from collections import deque

# Constantes generales
TAM_ENCABEZAD_DAT = 4  # Tamaño del encabezado en bytes (cantidad de registros)
TAM_ENCABEZAD_IND = 16  # Tamaño del encabezado en bytes (cantidad de pages(data), cantidad de pages(overflow), M , y pososicion del root)

def Calculate_M(num_records):
    """
    Calcula el valor de M basado en el número de registros.
    """
    x = symbols('x')
    ecuacion = Eq(x**2 * (x-1), num_records * 1.25)
    soluciones = solve(ecuacion, x)
    soluciones_reales = [s.evalf() for s in soluciones if s.is_real]
    m = soluciones_reales[0] if soluciones_reales else None
    m = round(m) if m is not None else None
    n = m ** 2
    if num_records < n:
        m = m-1
        n = m ** 2
    elif num_records >= (m**2*(m-1)):
        m = m + 1
        n = m ** 2

    # percentiles para posiciones 
    lista = []
    for i in range(n):
        percentil = i / n
        pos = round(num_records * percentil)
        lista.append(pos)
    return m, lista

class Index_Page():
    def __init__(self, leaf=True, M=None):
        self.leaf = leaf
        self.keys = [None] * (M-1)
        self.childrens = [-1] * M
        self.next = -1 
        self.key_count = 0
        self.M = M

    def to_bytes(self, format_key, indexp_format):
        # Convert leaf to integer (1 for True, 0 for False)
        leaf_int = 1 if self.leaf else 0
        
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
        pack_args = [leaf_int] + packed_keys + self.childrens + [self.next, self.key_count]
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


    # eliminar un elemento de la pagina de indice
    def remove_key(self, key):
        """
        Elimina una clave y su hijo asociado de la página de índice.
        """
        for i in range(self.key_count):
            if self.keys[i] == key:
                # Desplazar los elementos hacia la izquierda
                for j in range(i, self.key_count - 1):
                    self.keys[j] = self.keys[j + 1]
                    self.childrens[j] = self.childrens[j + 1]
                # Actualizar el conteo de claves
                self.key_count -= 1
                self.keys[self.key_count] = None
                self.childrens[self.key_count] = -1 


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
        for i in range(M - 1):
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
        instance.next = unpacked[-2]
        instance.key_count = unpacked[-1]

        return instance
    

def get_index_format(M, format_key): # Se hizo con la finalidad que al variar M, el formato del índice cambie automáticamente
    """
    Genera el formato del índice dinámicamente basado en M.
    """
    format = f'b{(M-1) * format_key}{M * "i"}ii'
    return format

class Index_temp:
    def __init__(self, key, pos :int = -1):
        self.key = key
        self.pos = pos

    def to_bytes(self, format_key):
        key_to_pack = self.key
        if key_to_pack is None:
            if format_key in ('i', 'q', 'Q'):
                key_to_pack = -2147483648
            elif format_key in ('f', 'd'):
                key_to_pack = float('nan')
            elif format_key in ('b', '?'):
                key_to_pack = -128
            elif 's' in format_key:
                max_length = int(format_key[:-1])
                key_to_pack = b'\x00' * max_length
            else:
                key_to_pack = 0
        else:
            if 's' in format_key and isinstance(key_to_pack, str):
                max_length = int(format_key[:-1])
                key_to_pack = key_to_pack.encode('utf-8')[:max_length].ljust(max_length, b'\x00')
            elif format_key in ('i', 'q', 'Q'):
                key_to_pack = int(key_to_pack)
            elif format_key in ('f', 'd'):
                key_to_pack = float(key_to_pack)
            elif format_key in ('b', '?'):
                key_to_pack = bool(key_to_pack)
        format_index = f'{format_key}i'
        return struct.pack(format_index, key_to_pack, self.pos)
        
    @classmethod
    def from_bytes(self, data, format_key):
        format_index = f'{format_key}i'
        unpacked_data = struct.unpack(format_index, data)
        key = unpacked_data[0]
        pos = unpacked_data[1]

        if format_key == 'i' or format_key == 'q' or format_key == 'Q':
            key = int(key) if key != -2147483648 else None
        elif format_key == 'f' or format_key == 'd':
            key = float(key) if not math.isnan(key) else None
        elif format_key == 'b' or format_key == '?':
            key = bool(key) if key != -128 else None
        elif 's' in format_key:
            max_length = int(format_key[:-1])
            key = key.decode('utf-8').rstrip('\x00') if key != b'\x00' * max_length else None
        return Index_temp(key, pos)
    
    def __str__(self):
        return f"key: {self.key}, pos: {self.pos})"
    

class ISAM():
    def __init__(self, table_format: dict , name_key: str ,
                 name_index_file = 'Isam_Struct/index_file.bin', 
                 name_data_file = 'Isam_Struct/data_file.bin',
                 force_create = False):
        self.HEAP = Heap(table_format =table_format, key =name_key, data_file_name=name_data_file, force_create=force_create)
        self.index_file = name_index_file
        self.data_file = name_data_file


        self.RT = RegistroType(table_format, name_key)               # Formato de los datos
        self.format_key = table_format[name_key]                     # Formato de la clave (KEY)
        self.tam_registro = self.RT.size                             # Tamaño del registro

        depends = self._initialize_files()
        if depends:
            self.build_index()
        else:
            self.M = self._read_header()[2]  
            self.indexp_format = get_index_format(self.M,self.format_key)   # Formato de la pagina (NODO)
            self.tam_indexp = struct.calcsize(self.indexp_format)        # Tamaño de la página de índice


    ### IMPRIMIR ISAM ###

    def print_ISAM_by_levels(self):
        """
        Imprime el ISAM por niveles, mostrando claves y punteros en cada nodo, incluyendo los overflow.
        """
        num_pages, num_over, _, pos_root = self._read_header()
        
        if pos_root == -1:
            print("Árbol vacío")
            return
        
        # Inicializar cola para BFS
        queue = deque()
        queue.append((pos_root, 0, "Root"))  # (posición, nivel, tipo)
        
        current_level = 0
        print("\n=== Estructura ISAM ===")
        
        while queue:
            pos, level, node_type = queue.popleft()
            
            # Manejar cambio de nivel
            if level != current_level:
                print()
                current_level = level
            
            # Leer la página
            page = self._read_index_page(pos)
            
            # Imprimir información del nodo
            print(f"[Nivel {level} {node_type} Pos:{pos}] ", end="")
            print("Keys:", [k for k in page.keys[:page.key_count] if k is not None], end=" | ")
            print("Children:", [c for c in page.childrens[:page.key_count+1] if c != -1], end="")
            
            # Para hojas, mostrar next
            if page.leaf:
                print(f" | Next: {page.next}", end="")
                
                # Si tiene overflow, agregar a la cola
                if page.next != -1:
                    queue.append((page.next, level, "Overflow"))
            print()
            
            # Agregar hijos no hoja a la cola
            if not page.leaf:
                for child_pos in page.childrens[:page.key_count+1]:
                    if child_pos != -1:
                        queue.append((child_pos, level+1, "Interno"))
        
        # Mostrar información de páginas
        print("\n=== Resumen ===")
        print(f"Total páginas de datos: {num_pages}")
        print(f"Total páginas de overflow: {num_over}")
        print(f"Orden del árbol (M): {self.M}")
        print(f"Posición raíz: {pos_root}")



    def _initialize_files(self):
        """
        Inicializa los archivos de índice y datos.
        """
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'wb') as f:
                f.write(struct.pack('iiii', 0, 0, 1,-1)) # Inicializa el encabezado del archivo de índice (0 datos, -2 indica que recien inicia)
                depends =  True                                      # Construye el índice estático
        else:
            depends= False
        
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'wb') as f:
                f.write(struct.pack('i', 0)) # Inicializa el encabezado del archivo de datos
        
        return depends

    ### MANEJO DE ENCABEZADOS ###
    def _read_header(self):
        with open(self.index_file, 'rb') as f:
            f.seek(0)
            header = f.read(TAM_ENCABEZAD_IND)
            num_pages, num_over , max_num_child ,  pos_root = struct.unpack('iiii', header)
        return num_pages, num_over, max_num_child, pos_root
    
    def _write_header(self, num_pages, num_over, max_num_child, pos_root):
        with open(self.index_file, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack('iiii',num_pages, num_over,max_num_child ,pos_root))   

    ### MANEJO DE DATOS (CASE INDEPENT) ###
    def _read_data_header(self):
        """
        Lee el encabezado del archivo de datos.
        """
        with open(self.data_file, 'rb') as f:
            f.seek(0)
            header = f.read(TAM_ENCABEZAD_DAT)
            size = struct.unpack('i', header)[0]
        return size
    
    def add_record(self, record : list):
        """
        Agrega un nuevo registro al final del archivo de datos y actualiza el encabezado.
        """
        with open(self.data_file, 'r+b') as f:
            # Leer el tamaño actual desde el encabezado
            f.seek(0)
            header = f.read(TAM_ENCABEZAD_DAT)
            size = struct.unpack('i', header)[0]
            # Calcular el offset para el nuevo registro
            offset = TAM_ENCABEZAD_DAT + size * self.RT.size
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
            offset = TAM_ENCABEZAD_DAT + pos * self.RT.size
            f.seek(offset)
            data = f.read(self.RT.size)
            return self.RT.from_bytes(data)

    ### MANEJO DE PÁGINAS DE ÍNDICE (nodos del arbol)###

    def _read_index_page(self, page_number):
        """
        Lee una página de índice del archivo.
        """
        with open(self.index_file, 'rb') as f:
            offset = TAM_ENCABEZAD_IND + page_number * self.tam_indexp
            f.seek(offset)
            data = f.read(self.tam_indexp)
            return Index_Page.from_bytes(data, self.M, self.format_key, self.indexp_format)    
                          
    def _write_index_page(self, page_number, page):
        """
        Escribe una página de índice al final del archivo.
        """
        with open(self.index_file, 'r+b') as f:
            offset = TAM_ENCABEZAD_IND + page_number * self.tam_indexp
            f.seek(offset)
            f.write(page.to_bytes(self.format_key, self.indexp_format))  # Escribe la página en la posición especificada

    def _add_index_page(self, page):
        """
        Agrega una nueva página de índice al final del archivo.
        """
        num_pages, num_over , max_num_child ,  pos_root= self._read_header()
        self._write_index_page(num_pages, page) 
        self._write_header(num_pages +1, num_over,max_num_child ,pos_root)  # Actualiza el encabezado del archivo de índice
        return num_pages
    
    def _add_overflow_page(self, page):
        """
        Agrega una nueva página de overflow al final del archivo.
        """
        num_pages, num_over , max_num_child ,  pos_root= self._read_header()
        self._write_index_page(num_pages + num_over, page) 
        self._write_header( num_pages, num_over + 1,max_num_child ,pos_root)
        return num_pages + num_over

    ### FUNCIONES PARA GENERAR LOS INDICES DEL ISAM ###

    ## MERGE SORT EXTERNO ###
    def external_merge_sort_multi_temp(self, file_path, record_size, format_temp, max_records_in_memory=10):
        """
        Ordenamiento externo tipo merge sort usando múltiples archivos temporales.
        """
        # 1. Dividir en bloques ordenados
        temp_files = self._split_into_sorted_blocks_multi(file_path, record_size, format_temp, max_records_in_memory)

        # 2. Mezclar los bloques ordenados
        self._merge_sorted_blocks_multi(temp_files, file_path, record_size, format_temp)

        # 3. Eliminar archivos temporales
        for temp in temp_files:
            os.remove(temp)

    def _split_into_sorted_blocks_multi(self, input_file, record_size, format_temp, max_records):
        """
        Divide el archivo original en varios bloques ordenados y los guarda en archivos temporales separados.
        """
        temp_files = []
        with open(input_file, 'rb') as fin:
            block_count = 0
            while True:
                block = []
                for _ in range(max_records):
                    data = fin.read(record_size)
                    if not data:
                        break
                    record_temp = Index_temp.from_bytes(data, self.format_key)
                    key = record_temp.key
                    offset = record_temp.pos
                    block.append((key, offset))
                if not block:
                    break

                # Ordenar y guardar en archivo temporal
                block.sort()
                temp_name = f'temp_block_{block_count}.bin'
                # print (f"Creando {temp_name} con {len(block)} registros")
                with open(temp_name, 'wb') as fout:
                    for key, offset in block:
                        temp_record = Index_temp(key, offset)
                        fout.write(temp_record.to_bytes(self.format_key))
                temp_files.append(temp_name)
                block_count += 1

        return temp_files

    def _merge_sorted_blocks_multi(self, temp_files, output_file, record_size, format_temp):
        """
        Mezcla múltiples archivos ordenados usando un heap (merge k-ways).
        """
        open_files = [open(fname, 'rb') for fname in temp_files]
        heap = []

        # Inicializar el heap con el primer registro de cada archivo
        for i, f in enumerate(open_files):
            data = f.read(record_size)
            if data:
                record_temp = Index_temp.from_bytes(data, self.format_key)
                key = record_temp.key
                offset = record_temp.pos
                # print(f"Agregando {key} al heap del bloque {i}")
                heapq.heappush(heap, (key, offset, i))

        with open(output_file, 'wb') as fout:
            while heap:
                key, offset, i = heapq.heappop(heap)
                record_temp = Index_temp(key, offset)
                fout.write(record_temp.to_bytes(self.format_key))
                # print(f"Escribiendo {key} en {output_file}")

                # Leer siguiente elemento del mismo archivo
                data = open_files[i].read(record_size)
                if data:
                    record_temp = Index_temp.from_bytes(data, self.format_key)
                    next_key = record_temp.key
                    next_offset = record_temp.pos
                    heapq.heappush(heap, (next_key, next_offset, i))
                #     print(f"Agregando {next_key} al heap del bloque {i}")
                # else:
                #     print(f"Bloque {i} agotado")


        # Cerrar archivos
        for f in open_files:
            f.close()

    ## CONSTRUCCION DE INDICES ESTATICOS ##

    def build_index(self):
        """
        Construye el índice estático ordenado en el mismo archivo temp.bin.
        """
        size = self.HEAP._read_header()
        format_temp = f'{self.format_key}i'  # Formato (key, offset)
        record_size = struct.calcsize(format_temp)
        order_file = 'temp.bin'
        # 1. Escribir datos (key, offset) en temp.bin
        with open(order_file, 'wb') as f:
            for i in range(size):
                record = self.HEAP.read(i)
                if record is not None:
                    key = self.RT.get_key(record)
                    offset = i
                    record_temp = Index_temp(key, offset)
                    f.write(record_temp.to_bytes(self.format_key))

        # 2. Ordenar usando merge sort externo
        self.external_merge_sort_multi_temp(order_file, record_size, format_temp)

        # 3. Verificación
        file_size = os.path.getsize(order_file)
        total_records = file_size // record_size
        HOLA = []
        with open(order_file, 'rb') as f:
            for i in range(total_records):
                data = f.read(record_size)
                record_temp = Index_temp.from_bytes(data, self.format_key)
                key = record_temp.key
                offset = record_temp.pos
                HOLA.append(key)

        # 3. Calcula M y lista de posiciones
        size = os.path.getsize(order_file)
        num_records = size // record_size
        self.M ,posiciones= Calculate_M(num_records)
        self.indexp_format = get_index_format(self.M, self.format_key)
        self.tam_indexp = struct.calcsize(self.indexp_format)

        # actualizar encabezado del índice
        num_pages, num_over , _ ,  pos_root = self._read_header()
        self._write_header(num_pages, num_over, self.M,pos_root)  # Inicializa el encabezado del índice

        lista = posiciones.copy()
        # 4. Generar paginas (HOJAS) de data ordenada
        # print(f"Generando paginas de indice con M={self.M} ")
        # print()
        # print("=== Generando hojas ===")
        with open(order_file, 'rb') as f:
            limit = lista.pop(0)
            limit = lista.pop(0) 
            page = Index_Page(leaf=True, M=self.M)
            for i in range(num_records):
                data = f.read(record_size)
                record_temp = Index_temp.from_bytes(data, self.format_key)
                key = record_temp.key
                pos = record_temp.pos
                if i == num_records -1:
                    page.keys[page.key_count] = key
                    page.childrens[page.key_count] = pos
                    page.key_count += 1
                    self._add_index_page(page)
                    break
                # Si la lista de posiciones está vacía, crear una nueva página
                if i == limit and i != 0 :
                    self._add_index_page(page)
                    page = Index_Page(leaf=True, M=self.M)
                    limit = lista.pop(0) if lista else None
                # Agregar clave y offset a la página
                page.keys[page.key_count] = key
                page.childrens[page.key_count] = pos
                page.key_count += 1

        num_pages_data, num_over , max_num_child ,  pos_root = self._read_header()
        for i in range(num_pages_data):
            page = self._read_index_page(i)
            # print(f"Página {i}: {page.keys}, {page.childrens}, next: {page.next}, Claves: {page.key_count}")
        
        # 5. Generar indices de primer nivel 
        # print("=== Generando indices de primer nivel ===")
        lista = posiciones.copy()
        with open(order_file, 'rb') as f:
            i = 1
            page = Index_Page(leaf=False, M=self.M)
            page.childrens[0] = 0  
            pos_page, num_over , max_num_child ,  pos_root= self._read_header()
            page_root = Index_Page(leaf=False, M=self.M)
            page_root.childrens[0] = pos_page
            for num in range(1,len(lista)):
                if i % self.M != 0 :
                    # print(lista[num], "Nueva pagina")
                    f.seek(lista[num] * record_size)
                    data = f.read(record_size)
                    record_temp = Index_temp.from_bytes(data, self.format_key)
                    key = record_temp.key
                    pos = record_temp.pos
                    # print( f"Agregando clave {key} y posicion {pos}")
                    page.keys[page.key_count] = key
                    page.childrens[page.key_count+1] = i
                    page.key_count += 1
                else:
                    # print (page.keys , page.childrens, page.next, "|" ,page.key_count)
                    self._add_index_page(page)
                    pos_page,_ , _,_= self._read_header()
                    f.seek(lista[num] * record_size)
                    data = f.read(record_size)
                    record_temp = Index_temp.from_bytes(data, self.format_key)
                    key = record_temp.key
                    pos = record_temp.pos
                    page = Index_Page(leaf=False, M=self.M)
                    page.childrens[0] = i
                    # print (page_root.keys , page_root.childrens, page_root.next, "|" ,page_root.key_count , "page root")
                    page_root.keys[page_root.key_count] = key
                    page_root.childrens[page_root.key_count+1] = pos_page
                    page_root.key_count += 1

                i += 1
            # print (page.keys , page.childrens, page.next, "|" ,page.key_count)
            self._add_index_page(page)
            if page_root.key_count == self.M - 1:
                num_pages, num_over,_ , _ = self._read_header()
                self._add_index_page(page_root)
                # Actualizar el encabezado del índice con la nueva raíz
                self._write_header(num_pages+1, num_over, self.M, num_pages)
                
        num_pages, num_over ,_ , _= self._read_header()
        for i in range(num_pages_data, num_pages-1):
            page = self._read_index_page(i)
        #     print(f"Página {i}: {page.keys}, {page.childrens}, next: {page.next}, Claves: {page.key_count}")
        
        # print("=== Generando root ===")
        page = self._read_index_page(num_pages-1)
        # print(f"Página {num_pages-1}: {page.keys}, {page.childrens}, next: {page.next}, Claves: {page.key_count}")

        # print (f"Formato de la llave: {self.format_key} | Formato del índice: {self.indexp_format}")
        # print (f"Tamaño de la página de índice: {self.tam_indexp} bytes")
        # print ("leyendo indice de primer nivel")

        # eliminar archivo temporal
        if os.path.exists(order_file):
            os.remove(order_file)

    ### FUNCIONES DEL ISAM ###

    ## BUSQUEDA ##

    def search_aux(self, pos_node ,key_min):
        if pos_node == -2:
            return -1
        else:
            temp = self._read_index_page(pos_node)
            while (temp.leaf == False):
                for i in range(temp.key_count):
                    if key_min <= temp.keys[i]:
                        pos_children = temp.childrens[i]
                        temp = self._read_index_page(pos_children)
                        break
                    if i == temp.key_count - 1:
                        pos_children = temp.childrens[i + 1]
                        temp = self._read_index_page(pos_children)
                        break
            return pos_children
    
    def search_in_overflow(self, page_leaf : Index_Page, key1 , key2 , detener):
        result_overflow = []
        if page_leaf.next == -1:
            return result_overflow , detener
        else:
            overflow = page_leaf.next
            while overflow != -1:
                temp = self._read_index_page(overflow)
                for i in range(temp.key_count):
                    if temp.keys[i] >= key1 and temp.keys[i] <= key2:
                        result_overflow.append(temp.childrens[i])
                    if temp.keys[i] > key2:
                        detener = True
                overflow = temp.next
            return result_overflow , detener


    def search(self, key):
        """
        Busca un registro en el árbol B+.
        """
        _, _ , _ ,  pos_root = self._read_header()  # posición de la raíz
        pos_leaf = self.search_aux(pos_root, key)
        detener = False
        results = []
        if pos_leaf == -1:
            return results
        else:
            while True:
                temp = self._read_index_page(pos_leaf)
                for i in range(temp.key_count):
                    if temp.keys[i] > key:
                        detener = True
                    if temp.keys[i] == key:
                        if self.HEAP.read(temp.childrens[i]) is not None:
                            results.append(temp.childrens[i])
                search_overflow, detener = self.search_in_overflow(temp, key, key ,detener)
                results.extend(search_overflow)
                if not detener:
                    pos_leaf = pos_leaf+1
                    if pos_leaf == self.M **2:
                        break
                else:
                    break
            return results
        
    ## BUSQUEDA POR RANGO ##

    def search_range(self, key1, key2):
        """
        Busca un registro en el árbol B+.
        """
        _, _ , _ ,  pos_root = self._read_header()  # posición de la raíz
        pos_children = self.search_aux(pos_root, key1)
        detener = False
        results = []
        if pos_children == -1:
            return results
        else:
            while True:
                temp = self._read_index_page(pos_children)
                for i in range(temp.key_count):
                    if temp.keys[i] > key2:
                        detener = True
                    if temp.keys[i] >= key1 and temp.keys[i] <= key2:
                        if self.HEAP.read(temp.childrens[i]) is not None:
                            results.append(temp.childrens[i])
                search_overflow, detener = self.search_in_overflow(temp, key1, key2 ,detener)
                results.extend(search_overflow)
                if not detener:
                    pos_children = pos_children+1
                    if pos_children == self.M **2:
                        break
                else:
                    break
            return results        
        
    ## INSERTION ##

    def add(self, record: list = None, pos_new_record :int = None):
        """
        Inserta un registro en el árbol B+.
        """
        # Le el encabezado del archivo de índice
        if record is not None and pos_new_record is not None:
            return "Error: Debe ingresar solo uno de los dos argumentos (record o pos_new_record)"
        if record is None and pos_new_record is None:
            return "Error: Debe ingresar uno de los dos argumentos (record o pos_new_record)"
        if record is not None:
            pos_new_record = self.HEAP.insert(record)
            key = self.RT.get_key(record)  # Obtiene la clave del registro

        if pos_new_record is not None:
            record = self.HEAP.read(pos_new_record)
            key = self.RT.get_key(record)  # Obtiene la clave del registro

        _, _ , _ ,  pos_root = self._read_header()  # posición de la raíz
        pos_leaf = self.search_aux(pos_root, key)
        page_leaf = self._read_index_page(pos_leaf)

        if page_leaf.key_count < self.M - 1:
            # Si la página hoja tiene espacio, insertar directamente
            page_leaf.keys[page_leaf.key_count] = key
            page_leaf.childrens[page_leaf.key_count] = pos_new_record
            page_leaf.key_count += 1
            self._write_index_page(pos_leaf, page_leaf)
        
        else:
            # Buscar el último nodo de overflow
            while page_leaf.next != -1:
                pos_leaf = page_leaf.next
                page_leaf = self._read_index_page(pos_leaf)
            if page_leaf.key_count < self.M - 1:
                # Si el último nodo de overflow tiene espacio, insertar ahí
                page_leaf.keys[page_leaf.key_count] = key
                page_leaf.childrens[page_leaf.key_count] = pos_new_record
                page_leaf.key_count += 1
                self._write_index_page(pos_leaf, page_leaf)
            else:
                # Si no hay espacio, crear un nuevo nodo de overflow
                new_overflow = Index_Page(leaf=True, M=self.M)
                new_overflow.keys[0] = key
                new_overflow.childrens[0] = pos_new_record
                new_overflow.key_count = 1
                new_overflow.next = -1
                pos_overflow = self._add_overflow_page(new_overflow)
                # conectar el nuevo nodo de overflow al último nodo de overflow
                page_leaf.next = pos_overflow
                self._write_index_page(pos_leaf, page_leaf)


    ## DELETE ##

    def delete(self, key):
        """
        Elimina un registro del árbol B+.
        """
        _, _ , _ ,  pos_root = self._read_header()
        first_pos_leaf = self.search_aux(pos_root, key)
        page_leaf = self._read_index_page(first_pos_leaf)

        resultado = self.search(key)
        
        if resultado == []:
            return
        
        while True:
                detener = self.delete_in_one_leaf( first_pos_leaf, key, detener=False)
                if not detener:
                    first_pos_leaf = first_pos_leaf+1
                    if first_pos_leaf == self.M **2:
                        break
                else:
                    break
    
    def delete_in_one_leaf(self, first_pos_leaf ,key , detener = False):
        page_leaf = self._read_index_page(first_pos_leaf)
        if page_leaf.next == -1:
            page_replace = Index_Page(leaf=True, M=self.M)
            for i in range(page_leaf.key_count):
                if page_leaf.keys[i] > key:
                    detener = True
                if page_leaf.keys[i] != key:
                    page_replace.keys[page_replace.key_count] = page_leaf.keys[i]
                    page_replace.childrens[page_replace.key_count] = page_leaf.childrens[i]
                    page_replace.key_count += 1
            self._write_index_page(first_pos_leaf, page_replace)
            return detener
        else:
            #conseguir la posicion de todos los nodos de overflow
            page_replace = Index_Page(leaf=True, M=self.M)
            for i in range(page_leaf.key_count):
                if page_leaf.keys[i] > key:
                    detener = True
                elif page_leaf.keys[i] != key:
                    page_replace.keys[page_replace.key_count] = page_leaf.keys[i]
                    page_replace.childrens[page_replace.key_count] = page_leaf.childrens[i]
                    page_replace.key_count += 1
            page_replace.next = page_leaf.next
            self._write_index_page(first_pos_leaf, page_replace)
            overflow_pos = []
            overflow_pos.append(page_leaf.next)
            while page_leaf.next != -1:
                page_leaf = self._read_index_page(page_leaf.next)
                overflow_pos.append(page_leaf.next)
            prev_pos = first_pos_leaf
            for j in range (len(overflow_pos)):
                if overflow_pos[j] == -1:
                    break
                page_overflow = self._read_index_page(overflow_pos[j])
                overflow_replace = Index_Page(leaf=True, M=self.M)
                for i in range(page_overflow.key_count):
                    if page_overflow.keys[i] > key:
                        detener = True
                    elif page_overflow.keys[i] != key:
                        overflow_replace.keys[overflow_replace.key_count] = page_overflow.keys[i]
                        overflow_replace.childrens[overflow_replace.key_count] = page_overflow.childrens[i]
                        overflow_replace.key_count += 1
                overflow_replace.next = page_overflow.next
                if overflow_replace.key_count > 0:
                    self._write_index_page(overflow_pos[j], overflow_replace)
                    prev_pos = overflow_pos[j]
                else: 
                    page_prev = self._read_index_page(prev_pos)
                    page_prev.next = overflow_replace.next
                    self._write_index_page(prev_pos, page_prev)
            return detener 


        

