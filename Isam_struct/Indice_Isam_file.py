import sys
import os
import struct
import csv
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *
import math
import heapq
from sympy import symbols, Eq, solve

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
        print("El numero de registros es menor que m, se ajustara a m-1")
        m = m-1
        n = m ** 2
    elif num_records >= (m**2*(m-1)):
        print("El numero de registros es mayor que m, se ajustara a m+1")
        m = m + 1
        n = m ** 2
    else:
        print("El numero de registros es correcto con m")

    # percentiles para posiciones 
    lista = []
    for i in range(n):
        percentil = i / n
        pos = round(num_records * percentil)
        lista.append(pos)
    print(float(num_records/(m**2*(m-1))))
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

    @classmethod
    def from_bytes(cls, data, M, format_key, indexp_format):
        # Verify data size
        print (f"Data size: {len(data)}, Expected size: {struct.calcsize(indexp_format)} , Format: {indexp_format}")
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


class ISAM():
    def __init__(self, table_format: dict , name_key: str ,
                 name_index_file = 'Isam_Struct/index_file.bin', 
                 name_data_file = 'Isam_Struct/data_file.bin',
                 ):
        
        self.index_file = name_index_file
        self.data_file = name_data_file

        self.RT = RegistroType(table_format, name_key)               # Formato de los datos
        self.format_key = table_format[name_key]                     # Formato de la clave (KEY)
        self.tam_registro = self.RT.size                             # Tamaño del registro
        self.prueba = True
        depends = self._initialize_files()
        if depends:
            self.build_index()
        else:
            self.M = self._read_header()[2]  
            self.indexp_format = get_index_format(self.M,self.format_key)   # Formato de la pagina (NODO)
            self.tam_indexp = struct.calcsize(self.indexp_format)        # Tamaño de la página de índice






    def _initialize_files (self):
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
        num_pages += 1
        self._write_header(num_pages, num_over,max_num_child ,pos_root)  # Actualiza el encabezado del archivo de índice

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
                    key, offset = struct.unpack(format_temp, data)
                    block.append((key, offset))
                if not block:
                    break

                # Ordenar y guardar en archivo temporal
                block.sort()
                temp_name = f'temp_block_{block_count}.bin'
                # print (f"Creando {temp_name} con {len(block)} registros")
                with open(temp_name, 'wb') as fout:
                    for key, offset in block:
                        fout.write(struct.pack(format_temp, key, offset))
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
                key, offset = struct.unpack(format_temp, data)
                # print(f"Agregando {key} al heap del bloque {i}")
                heapq.heappush(heap, (key, offset, i))

        with open(output_file, 'wb') as fout:
            while heap:
                key, offset, i = heapq.heappop(heap)
                fout.write(struct.pack(format_temp, key, offset))
                # print(f"Escribiendo {key} en {output_file}")

                # Leer siguiente elemento del mismo archivo
                data = open_files[i].read(record_size)
                if data:
                    next_key, next_offset = struct.unpack(format_temp, data)
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
        size = self._read_data_header()
        format_temp = f'{self.format_key}i'  # Formato (key, offset)
        record_size = struct.calcsize(format_temp)
        order_file = 'temp.bin'
        # 1. Escribir datos (key, offset) en temp.bin
        with open(order_file, 'wb') as f:
            for i in range(size):
                record = self._read_record(i)
                key = self.RT.get_key(record)
                offset = i
                f.write(struct.pack(format_temp, key, offset))
                print(key, offset, self._read_record(offset))
        print("temp.bin creado")

        # 2. Ordenar usando merge sort externo
        self.external_merge_sort_multi_temp(order_file, record_size, format_temp)

        # 3. Verificación
        print("Leyendo temp.bin ordenado:")
        file_size = os.path.getsize(order_file)
        total_records = file_size // record_size
        with open(order_file, 'rb') as f:
            for i in range(total_records):
                data = f.read(record_size)
                key, offset = struct.unpack(format_temp, data)
                print(key, offset, self._read_record(offset))

        # 3. Calcula M y lista de posiciones
        size = os.path.getsize(order_file)
        num_records = size // record_size
        print(f"Total de registros: {num_records}")
        self.M , posiciones= Calculate_M(num_records)
        self.indexp_format = get_index_format(self.M, self.format_key)
        self.tam_indexp = struct.calcsize(self.indexp_format)

        # actualizar encabezado del índice
        num_pages, num_over , _ ,  pos_root = self._read_header()
        self._write_header(num_pages, num_over, self.M,pos_root)  # Inicializa el encabezado del índice

        print(f"Valor de M calculado: {self.M}")
        lista = posiciones.copy()
        print("Lista de posiciones:", lista)
        # 4. Generar paginas (HOJAS) de data ordenada
        print(f"Generando paginas de indice con M={self.M} ")
        print()
        print("=== Generando hojas ===")
        with open(order_file, 'rb') as f:
            limit = lista.pop(0)
            limit = lista.pop(0) 
            page = Index_Page(leaf=True, M=self.M)
            for i in range(num_records):
                data = f.read(record_size)
                key, pos = struct.unpack(format_temp, data)
                if i == num_records -1:
                    page.keys[page.key_count] = key
                    page.childrens[page.key_count] = pos
                    self._add_index_page(page)
                # Si la lista de posiciones está vacía, crear una nueva página
                if i == limit and i != 0 :
                    self._add_index_page(page)
                    page = Index_Page(leaf=True, M=self.M)
                    limit = lista.pop(0) if lista else None
                # Agregar clave y offset a la página
                page.keys[page.key_count] = key
                page.childrens[page.key_count] = pos
                page.key_count += 1

        print("Leyendo index_file generado:")
        num_pages_data, num_over , max_num_child ,  pos_root = self._read_header()
        for i in range(num_pages_data):
            page = self._read_index_page(i)
            print(f"Página {i}: {page.keys}, {page.childrens}, next: {page.next}, Claves: {page.key_count}")
        
        # 5. Generar indices de primer nivel 
        print("=== Generando indices de primer nivel ===")
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
                    key, pos = struct.unpack(format_temp, data)
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
                    key, pos = struct.unpack(format_temp, data)
                    page = Index_Page(leaf=False, M=self.M)
                    page.childrens[0] = i
                    # print (page_root.keys , page_root.childrens, page_root.next, "|" ,page_root.key_count , "page root")
                    page_root.keys[page_root.key_count] = key
                    page_root.childrens[page_root.key_count+1] = pos_page
                    page_root.key_count += 1

                i += 1
            
            if page_root.key_count == self.M - 1:
                num_pages, num_over,_ , _ = self._read_header()
                self._add_index_page(page_root)
                # Actualizar el encabezado del índice con la nueva raíz
                self._write_header(num_pages+1, num_over, self.M, num_pages)
                
        num_pages, num_over ,_ , _= self._read_header()
        for i in range(num_pages_data, num_pages-1):
            page = self._read_index_page(i)
            print(f"Página {i}: {page.keys}, {page.childrens}, next: {page.next}, Claves: {page.key_count}")
        
        print("=== Generando root ===")
        page = self._read_index_page(num_pages-1)
        print(f"Página {num_pages-1}: {page.keys}, {page.childrens}, next: {page.next}, Claves: {page.key_count}")

        print (f"Formato de la llave: {self.format_key} | Formato del índice: {self.indexp_format}")
        print (f"Tamaño de la página de índice: {self.tam_indexp} bytes")
        print ("leyendo indice de primer nivel")

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
            return temp
        
    def search(self, key):
        """
        Busca un registro en el árbol B+.
        """

        print (f"{self.M} nodos hijos por página")
        print (f"Formato de la llave: {self.format_key} | Formato del índice: {self.indexp_format}")
        print (f"Tamaño de la página de índice: {self.tam_indexp} bytes")
        root = self._read_header()[2]  # posición de la raíz
        temp = self.search_aux(root, key)
        print (f"Buscando {key} en la raíz: {temp.keys} | Posición: {root}")
        results = []
        if temp == -1:
            return results
        else:
            while True:
                for i in range(temp.key_count):
                    if key < temp.keys[i]:
                        break
                    if temp.keys[i] == key:
                        results.append(temp.childrens[i])
                if temp.childrens[-1] != -1:
                    pos_children = temp.childrens[-1]
                    temp = self._read_index_page(pos_children)
                else:
                    break
            return results

    

    
    






        

