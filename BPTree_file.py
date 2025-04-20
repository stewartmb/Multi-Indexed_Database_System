import struct 
import os

TAM_ENCABEZAD_DAT = 4  # Tamaño del encabezado en bytes (cantidad de registros)
TAM_ENCABEZAD_IND = 8  # Tamaño del encabezado en bytes (cantidad de registros y puntero al root)
M = 4  # Grado del árbol B+ (número máximo de hijos por nodo)

### RECORD FORMAT ###
RECORD_FORMAT = '3s20s2s'  # Formato de los datos: 3s (codigo), 20s (nombre), 2s (ciclo)
TAM_REGISTRO = struct.calcsize(RECORD_FORMAT)  # Tamaño del registro en bytes


### INDEX FORMAT ###
ORDEN_KEY = 1 # Orden de la clave (1: codigo, 2: nombre, 3: ciclo)

def get_key_format(orden_key):
    """
    Genera el formato de la clave dinámicamente basado en el orden de la clave.
    """
    if orden_key == 1:
        return '3s'
    elif orden_key == 2:
        return '20s'
    elif orden_key == 3:
        return '2s'
    else:
        raise ValueError("Orden de clave no válido")
FORMAT_KEY = get_key_format(ORDEN_KEY)  # Formato de la clave (3s, 20s o 2s)

def get_index_format(M): # Se hizo con la finalidad que al variar M, el formato del índice cambie automáticamente
    """
    Genera el formato del índice dinámicamente basado en M.
    """
    return f'b{(M-1) * FORMAT_KEY}{M * "i"}ii'

INDEXP_FORMAT = get_index_format(M)
TAM_INDEXP = struct.calcsize(INDEXP_FORMAT)


class Registro:
    """
    Clase que representa un registro en el archivo.  
    """

    def __init__(self, codigo, nombre, ciclo):
        self.codigo = codigo
        self.nombre = nombre
        self.ciclo = ciclo

    
    def to_bytes(self):
        """
        Convierte el registro a bytes.
        """
        return struct.pack(RECORD_FORMAT, 
                           self.codigo.encode('utf-8').ljust(3, b'\x00'), 
                           self.nombre.encode('utf-8').ljust(20, b'\x00'), 
                           self.ciclo.zfill(2).encode('utf-8')  
        )
    
    @classmethod
    def from_bytes(cls, data):
        """
        Convierte bytes a un registro.
        """
        if len(data) != TAM_REGISTRO:
            raise ValueError("Tamaño incorrecto al leer registro")
        unpacked = struct.unpack(RECORD_FORMAT, data)
        return cls(
            codigo=unpacked[0].decode('utf-8').strip('\x00'),
            nombre=unpacked[1].decode('utf-8').strip('\x00'),
            ciclo=unpacked[2].decode('utf-8').strip('\x00')
        )
    
class IndexPage:
    """
    Clase que representa una página de índices (nodo del b+tree) en el archivo.
    """
    def __init__(self, leaf=True):
        self.leaf = leaf  # Indica si es una hoja 'bool'
        self.keys = [''] * (M-1) # claves de orden (codigo o ciclo o nombre)
        """
        self.childrens = []  
        Si hoja != True ---->  M Punteros a hijos (nodos) 'lista de posiciones en "index_file.bin" '
        Si hoja == True ---->  M-1 Punteros a registros (hojas) 'lista de posiciones en "data_file.bin" '
                               1 Puntero a siguiente hoja (hoja) 'lista de posiciones en "index_file.bin" '
        """
        self.childrens = [-1] * M # POSICION DE HIJOS (Inicialmente -1 ,sin hijos)
        self.father = -1  # Enlace al padre
        self.key_count = 0  # Claves ocupadas en el nodo

    def to_bytes(self):
        """
        Convierte la página de índice a bytes.
        """
        encoded_keys = []
        for i in range(M - 1):  # Para que soporte dinamicamente el tamaño de la clave
            key = str(self.keys[i]) if self.keys[i] else ''
            key = key.encode('utf-8')
            key = key.ljust(struct.calcsize(FORMAT_KEY), b'\x00')
            encoded_keys.append(key)

        return struct.pack(
            INDEXP_FORMAT,
            self.leaf,  
            *encoded_keys, 
            *self.childrens,
            self.father,  
            self.key_count  

    )

    
    @classmethod
    def from_bytes(cls, data):
        """
        Convierte bytes a una página de índice.
        """
        if len(data) != TAM_INDEXP:
            raise ValueError("Tamaño incorrecto al leer página de índice")

        unpacked = struct.unpack(INDEXP_FORMAT, data)

        leaf_flag = bool(unpacked[0])
        raw_keys = unpacked[1:M]  # M-1 claves
        childrens = list(unpacked[M:-2])  # M punteros

        page = cls(leaf=leaf_flag)
        page.keys = [k.decode('utf-8').strip('\x00') for k in raw_keys]
        page.childrens = childrens
        page.father = unpacked[-2]  # Enlace al padre
        page.key_count = unpacked[-1]  # Claves ocupadas en el nodo

        return page

class BPTree:
    """
    Clase que representa un árbol B+.
    """
    def __init__(self, name_index_file = 'index_file.bin', name_data_file = 'data_file.bin'):
        self.root = -2  # Inicializa la raíz como un nodo hoja
        self.index_file = name_index_file
        self.data_file = name_data_file
        self._initialize_files()  # Inicializa los archivos de índice y datos
    
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
            offset = TAM_ENCABEZAD_IND + page_number * TAM_INDEXP
            f.seek(offset)
            data = f.read(TAM_INDEXP)
            if len(data) != TAM_INDEXP:
                raise ValueError("Tamaño incorrecto al leer página de índice")
            return IndexPage.from_bytes(data)  # Devuelve la página de índice reconstruida desde los bytes
                      
    def _write_index_page(self, page_number, page):
        """
        Escribe una página de índice al final del archivo.
        """
        with open(self.index_file, 'r+b') as f:
            offset = TAM_ENCABEZAD_IND + page_number * TAM_INDEXP
            f.seek(offset)
            f.write(page.to_bytes())  

    def _add_index_page(self, page):
        """
        Agrega una nueva página de índice al final del archivo.
        """
        size , root_position = self._read_header_index()
        self._write_index_page(size, page) 
        size += 1
        self._write_header_index(size, root_position)  # Actualiza el encabezado del archivo de índice

    ### MANEJO DE RECORDS (registros en el data_file.bin)###

    def _read_record(self, position):
        """
        Lee un registro del archivo de datos.
        """
        with open(self.data_file, 'rb') as f:
            offset = TAM_ENCABEZAD_DAT + position * TAM_REGISTRO
            f.seek(offset)
            data = f.read(TAM_REGISTRO)
            if len(data) != TAM_REGISTRO:
                raise ValueError("Tamaño incorrecto al leer registro")
            return Registro.from_bytes(data)  
        
    def _write_record(self, position, record):
        """
        Escribe un registro del archivo de datos.
        """
        with open(self.data_file, 'r+b') as f:
            offset = TAM_ENCABEZAD_DAT + position * TAM_REGISTRO
            f.seek(offset)
            f.write(record.to_bytes())  # Escribe el registro en la posición especificada
            
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

    def search_aux(self, pos_node ,key):
        if pos_node == -2:
            return -1
        else:
            temp = self._read_index_page(pos_node)
            while (temp.leaf == False):
                for i in range(temp.key_count):
                    if key < temp.keys[i]:
                        pos_children = temp.childrens[i]
                        temp = self._read_index_page(pos_children)
                        break
                    if i == temp.key_count - 1:
                        pos_children = temp.childrens[i + 1]
                        temp = self._read_index_page(pos_children)
                        break
            for i in range(temp.key_count):
                if temp.keys[i] == key:
                    return temp.childrens[i]  # Retorna un posicion de registro en data_file.bin
            return -1
    
    def search(self, key):
        """
        Busca un registro en el árbol B+.
        """
        pos_record = self.search_aux(self.root, key)
        if pos_record == -1:
            return None
        else:
            record = self._read_index_page(pos_record)
            return record  # Regresa la tupla del registro encontrado
    
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
            
    def key_insert(self, page , key ): 
        """
        Inserta un key en la página.
        """
        index = self.find_index(page, key)
        # Desplaza las claves a la derecha para hacer espacio
        for i in range(page.key_count, index, -1):
            page.keys[i] = page.keys[i - 1]
        page.keys[index] = key

    def child_insert(self, page , pos_page ,index):
        """
        Inserta un puntero a la página hija en la posición index.
        """
        for i in range(page.key_count, index, -1):
            page.childrens[i] = page.childrens[i - 1]
        page.childrens[index] = pos_page
        return page
    
    def insert(self, key, record):
        """
        Inserta un registro en el árbol B+.
        """
        # Agrega el registro al archivo de datos
        pos_new_record = self._read_header_data() # posicion del nuevo registro
        self._add_record(record) # se inserta el registro en el data_file.bin
    

        ## CASO 1: El árbol está vacío ##
        if self.root == -2 or self.root == -1:
            # Crea una nueva página raíz
            new_page = IndexPage(leaf=True)
            new_page.keys[0] = key
            new_page.childrens[0] = 0
            new_page.key_count = 1
            position = self._read_header_index()[0] # Cantidad de páginas
            self._add_index_page(new_page) # Se agrega la nueva página al index_file.bin
            self.root = position
            self._write_header_index(position, self.root)








        



        
    
        
    
                





        



