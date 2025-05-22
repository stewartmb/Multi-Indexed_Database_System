import struct 
import sys
import os
import math
from collections import deque
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *

TAM_ENCABEZAD_DAT = 4  # Tamaño del encabezado en bytes (cantidad de registros)
TAM_ENCABEZAD_IND = 8  # Tamaño del encabezado en bytes (cantidad de registros y puntero al root)



def get_index_format(M, format_key): # Se hizo con la finalidad que al variar M, el formato del índice cambie automáticamente
    """
    Genera el formato del índice dinámicamente basado en M.
    """
    format = f'b{(M-1) * format_key}{M * "i"}ii'
    return format

class BPTree:
    """
    Clase que representa un árbol B+.
    """
    def __init__(self, table_format , name_key: str ,
                 name_index_file = 'BPTree_struct/index_file.bin', 
                 name_data_file = 'BPTree_struct/data_file.bin',
                 max_num_child = None,):
        
        self.index_file = name_index_file
        self.data_file = name_data_file

        self.RT = RegistroType(table_format, name_key)               # Formato de los datos

        self.format_key = table_format[name_key]                     # Formato de la clave (KEY)
        self.indexp_format = get_index_format(max_num_child, self.format_key)    # Formato de la pagina (NODO)
        self.tam_indexp = struct.calcsize(self.indexp_format)        # Tamaño de la página de índice
        self._initialize_files()                                     # Inicializa los archivos de índice y datos
        self.M = max_num_child  # Orden del árbol B+
        self.tam_registro = self.RT.size                             # Tamaño del registro

    
    def _initialize_files (self):
        """
        Inicializa los archivos de índice y datos.
        """
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'wb') as f:
                f.write(struct.pack('ii', 0, -2)) # Inicializa el encabezado del archivo de índice (0 datos, -2 indica que recien inicia)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'wb') as f:
                f.write(struct.pack('i', 0)) # Inicializa el encabezado del archivo de datos

    ### IMPRIMIT ARBOL ###

    def print_tree_by_levels(self):
        """
        Imprime el árbol B+ por niveles, mostrando claves y punteros en cada nodo.
        """
        header = self._read_header_index()
        root = header[1]

        if root == -2 or root == -1:
            return

        queue = deque()
        queue.append(root)
        level = 0

        while queue:
            level_size = len(queue)
            print(f"Nivel {level}: ", end="")

            for _ in range(level_size):
                pos = queue.popleft()
                page = self._read_index_page(pos)
                keys_str = ', '.join(str(k) for k in page.keys[:page.key_count])
                if page.leaf:
                    print(f"{pos}[{keys_str}]{page.father} ", end="")
                else:
                    childrens_str = ', '.join(str(c) for c in page.childrens[:page.key_count + 1])
                    print(f"{pos}[{keys_str}]{page.father} -> [{childrens_str}] ", end="")

                    for i in range(page.key_count + 1):
                        if page.childrens[i] != -1:
                            queue.append(page.childrens[i])
            
            print()  # Salto de línea al final del nivel
            level += 1


    ### MANEJO DE ENCABEZADOS ###

    def _read_header_index(self):
        """
        Lee el encabezado del archivo de índice.
        """
        with open(self.index_file, 'rb') as f:
            data = f.read(TAM_ENCABEZAD_IND)
            if len(data) != TAM_ENCABEZAD_IND:
                raise ValueError("Tamaño incorrecto al leer encabezado de índice")
            return struct.unpack('ii', data)  # (cantidad de registros, puntero al root)
        
    def _write_header_index(self, num_pages, root_position):
        """
        Escribe el encabezado del archivo de índice.
        """
        with open(self.index_file, 'r+b') as f:
            f.seek(0)  # Mueve el puntero al inicio del archivo
            f.write(struct.pack('ii', num_pages, root_position))  # Escribe el encabezado (cantidad de registros, puntero al root)
            
    def _read_header_data(self):
        """
        Lee el encabezado del archivo de datos.
        """
        with open(self.data_file, 'rb') as f:
            data = f.read(TAM_ENCABEZAD_DAT)
            if len(data) != TAM_ENCABEZAD_DAT:
                raise ValueError("Tamaño incorrecto al leer encabezado de datos")
            return struct.unpack('i', data)[0]  # (cantidad de registros)
        
    def _write_header_data(self, num_records):
        """
        Escribe el encabezado del archivo de datos.
        """
        with open(self.data_file, 'r+b') as f:
            f.seek(0)  # Mueve el puntero al inicio del archivo
            f.write(struct.pack('i', num_records))  # Escribe el encabezado (cantidad de registros)

    ### MANEJO DE PÁGINAS DE ÍNDICE (nodos del arbol)###

    def _read_index_page(self, page_number):
        """
        Lee una página de índice del archivo.
        """

        with open(self.index_file, 'rb') as f:
            offset = TAM_ENCABEZAD_IND + page_number * self.tam_indexp
            f.seek(offset)
            data = f.read(self.tam_indexp)
            if len(data) != self.tam_indexp:
                raise ValueError("Tamaño incorrecto al leer página de índice")
            return IndexPage.from_bytes(data, self.M, self.format_key, self.indexp_format)    
                          
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
        size , root_position = self._read_header_index()
        self._write_index_page(size, page) 
        size += 1
        self._write_header_index(size, root_position)  # Actualiza el encabezado del archivo de índice

    def _update_root(self, root_position):
        """
        Actualiza la raíz del árbol B+.
        """
        self._write_header_index(self._read_header_index()[0], root_position)

    ### MANEJO DE RECORDS (registros en el data_file.bin)###

    def _read_record(self, position):
        """
        Lee un registro del archivo de datos.
        """
        with open(self.data_file, 'rb') as f:
            offset = TAM_ENCABEZAD_DAT + position * self.tam_registro
            f.seek(offset)
            data = f.read(self.tam_registro)
            if len(data) != self.tam_registro:
                raise ValueError("Tamaño incorrecto al leer registro")
            return self.RT.from_bytes(data)  
        
    def _write_record(self, position, record):
        """
        Escribe un registro del archivo de datos.
        """
        with open(self.data_file, 'r+b') as f:
            offset = TAM_ENCABEZAD_DAT + position * self.tam_registro
            f.seek(offset)
            f.write(self.RT.to_bytes(record))  # Escribe el registro en la posición especificada
            
    def _add_record(self, record):
        """
        Agrega un nuevo registro al final del archivo de datos.
        """
        size = self._read_header_data()
        self._write_record(size, record) 
        size += 1
        self._write_header_data(size)
    
    ### FUNCIONES DE MANEJO DEL ÁRBOL B+ ###

    ## BUSQUEDA ##

    def search_leaf(self, key):
        """
        Busca la posicion de la hoja correspondiente a la key dado.
        """
        root = self._read_header_index()[1]  # posición de la raíz
        pos_node = root
        if pos_node == -2:
            return -1 # El árbol está vacío
        else:
            temp = self._read_index_page(pos_node)
            while (temp.leaf == False):
                for i in range(temp.key_count):
                    if key < temp.keys[i]:
                        pos_node = temp.childrens[i]
                        temp = self._read_index_page(pos_node)
                        break
                    if i == temp.key_count - 1:
                        pos_node = temp.childrens[i + 1]
                        temp = self._read_index_page(pos_node)
                        break
            return pos_node # Retorna un posicion de la hoja en donde deberia estar el registro
    
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
            return temp # Retorna un posicion de la hoja en donde deberia estar el registro


    def search(self, key):
        """
        Busca un registro en el árbol B+.
        """
        root = self._read_header_index()[1]  # posición de la raíz
        temp = self.search_aux(root, key)
        results = []
        if temp == -1:
            return results
        else:
            while True:
                for i in range(temp.key_count):
                    if key < temp.keys[i]:
                        break
                    if temp.keys[i] == key:
                        record = self._read_record(temp.childrens[i])
                        results.append(record)
                if temp.childrens[-1] != -1:
                    pos_children = temp.childrens[-1]
                    temp = self._read_index_page(pos_children)
                else:
                    break
            return results

    def search_range(self, key1, key2):
        """
        Busca un rango de registros en el árbol B+.
        """
        root = self._read_header_index()[1]  # posición de la raíz
        temp = self.search_aux(root, key1)
        results = []
        if temp == -1:
            return results
        else:
            while True:
                for i in range(temp.key_count):
                    if key2 < temp.keys[i]:
                        break
                    if temp.keys[i] >= key1 and temp.keys[i] <= key2:
                        record = self._read_record(temp.childrens[i])
                        results.append(record)
                if temp.childrens[-1] != -1:
                    pos_children = temp.childrens[-1]
                    temp = self._read_index_page(pos_children)
                else:
                    break
            return results # Regresa la lista de registros encontrados
    
    
    ## INSERCION ##

    def find_index(self, page, key):
        """
        Encuentra el índice donde se debe insertar la clave en la página.
        """
        for i in range(page.key_count):
            if key < page.keys[i]:
                return i
            if i == page.key_count - 1:
                return i + 1 
            
    def key_insert_left(self, page , key , pos_children ): 
        """
        Inserta un key en la página.
        """
        index = self.find_index(page, key)
        # Desplaza las claves a la derecha para hacer espacio
        for i in range(page.key_count, index, -1):
            page.keys[i] = page.keys[i - 1]
            page.childrens[i] = page.childrens[i - 1]
        page.keys[index] = key
        page.childrens[index] = pos_children
        page.key_count += 1
        return page
    
    def key_insert_internal(self, page , key , pos_children ):
        """
        Inserta un key en la página.
        """
        index = self.find_index(page, key)
        # Desplaza las claves a la derecha para hacer espacio
        for i in range(page.key_count, index, -1):
            page.keys[i] = page.keys[i - 1]
            page.childrens[i + 1] = page.childrens[i]
        page.keys[index] = key
        page.childrens[index + 1] = pos_children
        page.key_count += 1
        return page

    def split_leaf(self, pos_page , key, pos_record):
        """
        Divide una page_leaf llena en dos páginas.
        """
        page = self._read_index_page(pos_page)
        index = self.find_index(page, key)
        temp_keys = page.keys[:self.M-1].copy()  # Copia las claves
        temp_childrens = page.childrens[:self.M-1].copy()
        # Desplaza las claves y punteros a la derecha para hacer espacio
        temp_keys.insert(index, key)  # Inserta la nueva clave
        temp_childrens.insert(index, pos_record)  # Inserta el puntero al registro
        # Divide la página en dos
        header = self._read_header_index()
        pos_new_page = header[0]  # posición de la nueva página
        new_page = IndexPage(leaf=page.leaf, M = self.M)  # Crea una nueva página de índic
        # Asigna las claves y punteros a la nueva página
        mid_index = (self.M - 1) // 2
        is_even = False
        if self.M % 2 == 0:
            is_even = True
        pos_next_page = page.childrens[-1]  # Puntero al siguiente nodo
        # Reinicializa la página original
        page.keys = [None] * (self.M-1)
        page.childrens = [-1] * self.M
        # Actualiza la página original
        page.keys[:mid_index+is_even] = temp_keys[:mid_index+is_even]
        page.childrens[:mid_index+is_even] = temp_childrens[:mid_index+is_even]
        page.key_count = mid_index+is_even 
        # Asigna las claves y punteros a la nueva página
        new_page.keys[:mid_index+1] = temp_keys[mid_index+is_even:]
        new_page.childrens[:mid_index+1] = temp_childrens[mid_index+is_even:]
        new_page.key_count = mid_index +1
        new_page.father = page.father  # Asigna el padre
        up = temp_keys[mid_index + is_even]
        # Actualiza el puntero al siguiente nodo
        new_page.childrens[self.M-1] = pos_next_page
        page.childrens[self.M-1] = pos_new_page 
        # Escribe las páginas actualizadas en el archivo
        self._write_index_page(pos_page, page)
        self._add_index_page(new_page)
        return up, pos_new_page  # Devuelve la clave que se sube al padre
    
    def split_parent(self, pos_page , key, pos_record):
        """
        Divide una página llena en dos páginas.
        """
        page = self._read_index_page(pos_page)
        index = self.find_index(page, key)
        temp_keys = page.keys[:self.M-1].copy()  # Copia las claves
        temp_childrens = page.childrens[:self.M].copy()
        # Desplaza las claves y punteros a la derecha para hacer espacio
        temp_keys.insert(index, key)  # Inserta la nueva clave
        temp_childrens.insert(index+1, pos_record)  # Inserta el puntero al registro
        # Divide la página en dos
        header = self._read_header_index()
        pos_new_page = header[0]  # posición de la nueva página
        new_page = IndexPage(leaf=page.leaf,  M = self.M)  # Crea una nueva página de índic
        # Asigna las claves y punteros a la nueva página
        mid_index = (self.M - 1) // 2
        is_even = False
        if self.M % 2 == 0:
            is_even = True
        pos_next_page = page.childrens[-1]  # Puntero al siguiente nodo
        # Reinicializa la página original
        page.keys = [None] * (self.M-1)
        page.childrens = [-1] * self.M
        # Actualiza la página original
        page.keys[:mid_index+is_even] = temp_keys[:mid_index+is_even]
        page.childrens[:mid_index+is_even+1] = temp_childrens[:mid_index+is_even+1]
        page.key_count = mid_index+is_even 
        # Asigna las claves y punteros a la nueva página
        new_page.keys[:mid_index] = temp_keys[mid_index+1+is_even:]
        new_page.childrens[:mid_index+1] = temp_childrens[mid_index+1+is_even:]
        new_page.key_count = mid_index 
        new_page.father = page.father  # Asigna el padre
        up = temp_keys[mid_index+is_even]
        # Actualizar padres de los nodos hijos
        for i in range(page.key_count+1):
            if page.childrens[i] != -1:
                child_page = self._read_index_page(page.childrens[i])
                child_page.father = pos_page
                self._write_index_page(page.childrens[i], child_page)
        for i in range(new_page.key_count+1):
            if new_page.childrens[i] != -1:
                child_page = self._read_index_page(new_page.childrens[i])
                child_page.father = pos_new_page
                self._write_index_page(new_page.childrens[i], child_page)
        # Escribe las páginas actualizadas en el archivo
        self._write_index_page(pos_page, page)
        self._add_index_page(new_page)
        return up, pos_new_page  # Devuelve la clave que se sube al padre
    


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
            pos_new_record = self._read_header_data() 
            # record = self.RT.correct_format(record)  # Formatea el registro
            self._add_record(record)
            key = self.RT.get_key(record)  # Obtiene la clave del registro

        if pos_new_record is not None:
            record = self._read_record(pos_new_record)
            key = self.RT.get_key(record)  # Obtiene la clave del registro 

        header = self._read_header_index()
        root = header[1] # posición de la raíz
        pos_new_index = header[0] # cantidad de páginas
       
        ## CASO 1: El árbol está vacío ##
        if root == -2 or root == -1:
            # Crea una nueva página de índice
            new_page = IndexPage(leaf=True, M = self.M)
            new_page.keys[0] = key
            new_page.childrens[0] = pos_new_record
            new_page.key_count = 1
            self._add_index_page(new_page) # Se agrega la nueva página al index_file.bin
            self._update_root(pos_new_index) # Se actualiza la raíz del árbol
            return
        
        ## CASO 2: El árbol no está vacío ##
        pos_leaf = self.search_leaf(key) # Busca la posición de la hoja donde se debe insertar el registro
        
        ### CASO 2.1: La raíz no está llena ###
        leaf_page = self._read_index_page(pos_leaf) # Lee la página
        
        if leaf_page.key_count < self.M - 1 : # Si la página tiene espacio
            # Inserta la clave y el puntero al registro
            new_leaf_page = self.key_insert_left(leaf_page, key, pos_new_record)
            self._write_index_page(pos_leaf, new_leaf_page)
            return
        ### CASO 2.2: La raíz está llena ###
        else:
            key_up,pos_new_index = self.split_leaf(pos_leaf, key, pos_new_record) # Divide la página llena

            # Comienza el proceso de propagación hacia arriba
            current_pos = pos_leaf
            current_page = self._read_index_page(current_pos)
            parent_pos = current_page.father

            while True:
                ### CASO 2.2.1: Si el padre no existe, se crea uno nuevo ###
                if parent_pos == -1:
                    pos_new_root = self._read_header_index()[0]
                    new_root = IndexPage(leaf=False,  M = self.M)
                    new_root.keys[0] = key_up
                    new_root.childrens[0] = current_pos
                    new_root.childrens[1] = pos_new_index
                    new_root.key_count = 1

                    # Actualizar padres de los nodos hijos
                    current_page.father = pos_new_root
                    new_page = self._read_index_page(pos_new_index)
                    new_page.father = pos_new_root
                    self._write_index_page(current_pos, current_page)
                    self._write_index_page(pos_new_index, new_page)

                    # Actualizar la raíz del árbol
                    self._update_root(pos_new_root)
                    self._add_index_page(new_root)
                    break
                else:
                    parent_page = self._read_index_page(parent_pos)
                    # Si el padre no está lleno, se inserta la clave
                    if parent_page.key_count < self.M - 1:
                        new_parent_page = self.key_insert_internal(parent_page, key_up, pos_new_index)
                        self._write_index_page(parent_pos, new_parent_page)
                        break
                    # Si el padre está lleno, se divide
                    else:
                        key_up, pos_new_index = self.split_parent(parent_pos, key_up, pos_new_index)
                        current_pos = parent_pos
                        current_page = self._read_index_page(current_pos)
                        parent_pos = current_page.father

class IndexPage():
    def __init__(self, leaf=True, M=None):
        self.leaf = leaf
        self.keys = [None] * (M-1)
        self.childrens = [-1] * M
        self.father = -1
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
        pack_args = [leaf_int] + packed_keys + self.childrens + [self.father, self.key_count]
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
        instance.father = unpacked[-2]
        instance.key_count = unpacked[-1]

        return instance