import sys
import os
import struct
import csv
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *
import math

# Constantes generales
TAM_ENCABEZADO = 12        # Encabezado de datos.bin: 4+4+4 = 12 bytes | pos_root(i) + num_aux(i) + tam_aux(i)
TAM_DATA = 4              # Tamaño de los datos (4 bytes)


class Index_Record:
    def __init__(self, key, pos :int , next :int = -1):
        self.key = key
        self.pos = pos
        self.next = next

    def to_bytes(self, format_key):
        key_to_pack = self.key
        if key_to_pack is None:
            if format_key in ('i', 'q', 'Q'):
                key_to_pack = -2147483648
            elif format_key == 'f':
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
        format_index = f'{format_key}ii'
        return struct.pack(format_index, key_to_pack, self.pos, self.next)
        
    @classmethod
    def from_bytes(self, data, format_key):
        format_index = f'{format_key}ii'
        unpacked_data = struct.unpack(format_index, data)
        key = unpacked_data[0]
        pos = unpacked_data[1]
        next_pos = unpacked_data[2]

        if format_key == 'i' or format_key == 'q' or format_key == 'Q':
            key = int(key) if key != -2147483648 else None
        elif format_key == 'f' or format_key == 'd':
            key = float(key) if not math.isnan(key) else None
        elif format_key == 'b' or format_key == '?':
            key = bool(key) if key != -128 else None
        elif 's' in format_key:
            max_length = int(format_key[:-1])
            key = key.decode('utf-8').rstrip('\x00') if key != b'\x00' * max_length else None
        return Index_Record(key, pos, next_pos)
    
    def __str__(self):
        return f"key: {self.key}, pos: {self.pos}, next: {self.next})"

class Sequential:
    def __init__(self, table_format , name_key: str ,
                 name_index_file = 'Sequential_Struct/index_file.bin', 
                 name_data_file = 'Sequential_Struct/data_file.bin',
                 num_aux = 1,):
        
        self.index_file = name_index_file
        self.data_file = name_data_file
        self.RT = RegistroType(table_format, name_key)                           # Formato de los datos
        self.format_key = table_format[name_key]                                 # Formato de la clave (KEY)
        self._initialize_files()                                                 # Inicializa los archivos de índice y datos
        self.K = num_aux                                                   # Tamaño del archivo auxiliar


    def _initialize_files(self):
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'wb') as f:
                f.write(struct.pack('i', 0))
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'wb') as f:
                f.write(struct.pack('iii', -1, 0 ,0))                                # encabezado: pos_root(i), num_aux(i), tam_aux(i)
    
    ### MANEJO DE ENCABEZADOS ###
    def _read_header(self):
        with open(self.index_file, 'rb') as f:
            f.seek(0)
            header = f.read(TAM_ENCABEZADO)
            pos_root, num_dat, tam_aux = struct.unpack('iii', header)
        return pos_root, num_dat, tam_aux
    
    def _write_header(self, pos_root, num_dat, tam_aux):
        with open(self.index_file, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack('iii', pos_root, num_dat, tam_aux))

    ### MANEJO DE DATOS (CASE INDEPENT) ###
    def add_record(self, record : list):
        """
        Agrega un nuevo registro al final del archivo de datos y actualiza el encabezado.
        """
        with open(self.data_file, 'r+b') as f:
            # Leer el tamaño actual desde el encabezado
            f.seek(0)
            header = f.read(TAM_DATA)
            size = struct.unpack('i', header)[0]
            # Calcular el offset para el nuevo registro
            offset = TAM_DATA + size * self.RT.size
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
            offset = TAM_DATA + pos * self.RT.size
            f.seek(offset)
            data = f.read(self.RT.size)
            return self.RT.from_bytes(data)

    ### MANEJO DE INDEX_RECORDS ###

    def read_index(self, pos : int):
        """
        Lee un registro de índice desde el archivo de índice en la posición dada.
        """
        format_index = f'{self.format_key}ii'
        tam_index = struct.calcsize(format_index)
        with open(self.index_file, 'rb') as f:
            offset =  TAM_ENCABEZADO + pos * tam_index
            f.seek(offset)
            data = f.read(tam_index)
            return Index_Record.from_bytes(data, self.format_key)
    
    def write_index(self, index_record : Index_Record, pos : int):
        """
        Escribe un registro de índice en el archivo de índice en la posición dada.
        """
        format_index = f'{self.format_key}ii'
        tam_index = struct.calcsize(format_index)
        with open(self.index_file, 'r+b') as f:
            offset = TAM_ENCABEZADO + pos * tam_index
            f.seek(offset)
            f.write(index_record.to_bytes(self.format_key))

    def add_index(self, index_record : Index_Record):
        """
        Agrega un nuevo registro de índice al final del archivo de índice y actualiza el encabezado.
        """
        format_index = f'{self.format_key}ii'
        tam_index = struct.calcsize(format_index)
        with open(self.index_file, 'r+b') as f:
            # Leer el número actual de registros desde el encabezado
            header = f.read(TAM_ENCABEZADO)
            pos_root, num_dat, tam_aux = struct.unpack('iii', header)
            # Calcular el offset para el nuevo registro
            offset = TAM_ENCABEZADO + (num_dat + tam_aux) * tam_index
            f.seek(offset)
            f.write(index_record.to_bytes(self.format_key))
            # Actualizar el encabezado con el nuevo número de registros
            f.seek(0)
            f.write(struct.pack('iii', pos_root, num_dat, tam_aux+1))
            return num_dat + tam_aux
    
    def update_root(self, pos_root : int):
        """
        Actualiza la posición de la raíz en el encabezado del archivo de índice.
        """
        with open(self.index_file, 'r+b') as f:
            _ , num_dat,tam_aux = self._read_header()
            self._write_header(pos_root, num_dat, tam_aux)
    
    ### FUNCIONES DE MANEJO DE SEQUENTIAL ###

    ## INSERCION ##

    def binary_search_prev(self, key):
        """
        Realiza una búsqueda binaria en el archivo de índice para encontrar la posición anterior al resgistro buscado.
        """
        pos_root, num_dat, _ = self._read_header()
        if pos_root == -1:
            return pos_root
        left = 0
        right = num_dat - 1
        mid = pos_root
        index_record = self.read_index(pos_root)

        while left <= right:
            mid = (left + right) // 2
            index_record = self.read_index(mid)
            if index_record.key == key:
                # Si se encuentra la clave, se busca el registro anterior
                pos_prev = mid-1
                if pos_prev < 0:
                    return pos_root
                index_record = self.read_index(pos_prev)
                while index_record.next == -2 or index_record.key >= key:
                    pos_prev -= 1
                    if pos_prev < 0:
                        return pos_root
                    index_record = self.read_index(pos_prev)
                return pos_prev # retorna la posición del registro anterior
            elif index_record.key < key:
                left = mid + 1
            else:
                right = mid - 1

        pos_prev = mid  
        while index_record.next == -2 or index_record.key >= key:
            pos_prev -= 1
            if pos_prev < 0:
                return pos_root
            index_record = self.read_index(pos_prev)
        return pos_prev # retorna la posición del registro anterior
    
    def linear_search(self, key, pos : int = None):
        """
        Realiza una búsqueda lineal en el archivo de índice para encontrar la posición del prev y el registro buscado.
        retorna: prev_ptr, temp_ptr
        """
        # el pos retornado o es el pos_root o un pos positivo del registro anterior
        prev_ptr = pos
        temp_ptr = pos

        # Caso 1: Archivo vacío
        if temp_ptr == -1:
            return -1, -1
        pos_root, num_dat, tam_aux = self._read_header()
        root = self.read_index(pos_root)

        # Caso 2: La clave está en la raíz
        if root.key == key:
            return -1, pos_root
        # Caso 3: La clave es menor que la raíz
        if root.key > key:
            return -1, -1
        
        # Búsqueda lineal
        while temp_ptr != -1:
            # print("temp_ptr", temp_ptr)
            index_record = self.read_index(temp_ptr)
            # Caso 4: Encontramos la clave
            if index_record.key == key:
                # print ("encontramos la clave")
                return prev_ptr, temp_ptr
            # Caso 5: Pasamos el punto donde debería estar la clave
            if index_record.key > key:
                # print ("pasamos el punto")
                return prev_ptr, -1
            # Avanzamos al siguiente registro
            prev_ptr = temp_ptr
            temp_ptr = index_record.next

        
        # Caso 6: Llegamos al final sin encontrar la clave
        return prev_ptr, -1


    def add(self, record: list = None, pos_new_record :int = None):

        # Le el encabezado del archivo de índice
        if record is not None and pos_new_record is not None:
            return "Error: Debe ingresar solo uno de los dos argumentos (record o pos_new_record)"
        if record is None and pos_new_record is None:
            return "Error: Debe ingresar uno de los dos argumentos (record o pos_new_record)"
        if record is not None:
            pos_new_record = self.add_record(record)
            key = self.RT.get_key(record)

        if pos_new_record is not None:
            record = self._read_record(pos_new_record)
            key = self.RT.get_key(record)  # Obtiene la clave del registro 

        pos_root, num_dat, tam_aux  = self._read_header()

        ## CASO 1: Si el índice está vacío, se agrega el registro como raíz
        index_record = Index_Record(key = key, pos = pos_new_record)
        pos_new_index = self.add_index(index_record)

        if pos_root == -1:
            self.update_root(pos_new_index)
            if tam_aux +1 == self.K:
                self.reconstruction()
            # print(pos_new_index, index_record, "->", self._read_record(index_record.pos))
            # print( "Registro agregado como raíz")
            return
        
        ## CASO 2: indice con registros
        # busqueda binaria
        pos = self.binary_search_prev(key)
        # busqueda lineal
        prev_ptr, temp_ptr = self.linear_search(key, pos)
        
        # CASO 2.1: Si el registro es menor que la raíz, se convierte en la nueva raíz
        if prev_ptr == -1 :
            index_record.next = pos_root
            self.update_root(pos_new_index)
            self.write_index(index_record, pos_new_index)
            # print(pos_new_index, index_record, "->", self._read_record(index_record.pos))
            if tam_aux +1 == self.K:
                self.reconstruction()
            # print("Registro cambio a la raíz")
            return 
        else:
            index_record_prev = self.read_index(prev_ptr)
            pos_next = index_record_prev.next
            index_record_prev.next = pos_new_index # apunta al nuevo registro
            self.write_index(index_record_prev, prev_ptr)
            index_record.next = pos_next  # apunta al prev->next
            self.write_index(index_record, pos_new_index)
            # print(pos_new_index, index_record, "->", self._read_record(index_record.pos))
            if tam_aux +1 == self.K:
                self.reconstruction()
            # print( "Registro agregado en la posición correcta")
            return
    

    def reconstruction(self):
        """
        Reconstruye el sequential file cuando se alcanza el tamaño máximo.
        """
        # Crear un nuevo archivo de índice
        pos_root,_,_ = self._read_header()
        pos_index = pos_root
        total_dat = 0
        with open("temp.bin", "wb") as temp:
            temp.write(struct.pack('iii', -1, 0, 0))
            while pos_index != -1:
                index_record = self.read_index(pos_index)
                next_pos = index_record.next
                if next_pos == -1:
                    index_record.next = -1
                    temp.write(index_record.to_bytes(self.format_key))
                    total_dat += 1
                    break
                index_record.next = total_dat+1
                temp.write(index_record.to_bytes(self.format_key))
                pos_index = next_pos
                total_dat += 1
            # Actualizar el encabezado del nuevo archivo 
            temp.seek(0)
            temp.write(struct.pack('iii', 0, total_dat , 0))
        os.remove(self.index_file)
        os.rename("temp.bin", self.index_file)
        self.K = round(total_dat**0.5 +0.5)
    
    def delete(self, key):
        """
        Elimina un registro del archivo de índice y actualiza el encabezado.
        """
        pos_root, num_dat, tam_aux = self._read_header()
        if pos_root == -1:
            return "El árbol está vacío."
        
        # busqueda binaria
        pos = self.binary_search_prev(key)
        # busqueda lineal
        prev_ptr, temp_ptr = self.linear_search(key, pos)
        next_ptr = None
        if temp_ptr == -1:
            return "Registro no encontrado."
        else:
            while temp_ptr != -1:
                index_record = self.read_index(temp_ptr)
                if index_record.key == key:
                    next_ptr = index_record.next
                    delete_index = self.read_index(temp_ptr)
                    delete_index.next = -2
                    self.write_index(delete_index, temp_ptr)
                    temp_ptr = next_ptr

                else:
                    break
            if prev_ptr == -1:
                self.update_root(next_ptr)
            else:
                index_record_prev = self.read_index(prev_ptr)
                index_record_prev.next = next_ptr
                self.write_index(index_record_prev, prev_ptr)



    def search(self, key):
        """
        Busca todos los registros en el archivo de índice que tengan ese key.
        """
        pos_root, num_dat, _ = self._read_header()
        result = []
        if pos_root == -1:
            return result
        # busqueda binaria
        pos = self.binary_search_prev(key)
        # busqueda lineal
        prev_ptr, temp_ptr = self.linear_search(key, pos)
        while temp_ptr != -1:
            index_record = self.read_index(temp_ptr)
            if index_record.key == key:
                result.append(self._read_record(index_record.pos))
            else:
                break
            temp_ptr = index_record.next
        return result
        
    def search_range(self, key1, key2):
        """
        Busca todos los registros en el archivo de índice que estén dentro del rango [key1, key2].
        """
        pos_root, num_dat, _ = self._read_header()
        result = []
        if pos_root == -1:
            return result
        # busqueda binaria
        pos = self.binary_search_prev(key1)
        # busqueda lineal
        prev_ptr, temp_ptr = self.linear_search(key1, pos)
        if temp_ptr == -1:
            temp_ptr = prev_ptr
            if prev_ptr == -1:
                temp_ptr = pos_root
        while temp_ptr != -1:
            index_record = self.read_index(temp_ptr)
            if index_record.key >= key1 and index_record.key <= key2:
                result.append(self._read_record(index_record.pos))
            elif index_record.key > key2:
                break
            temp_ptr = index_record.next
        return result
        
    def mostrar(self):
        # mostrar el data ordenado
        pos_root, num_dat, max_aux = self._read_header()
        print("====================================")
        print("Posición raíz:", pos_root)
        print("Número de registros:", num_dat)
        print("Tamaño del archivo auxiliar:", max_aux)
        print("Data.bin:")
        for i in range(num_dat):
            index_record = self.read_index(i)
            print( i , index_record, "->", self._read_record(index_record.pos))
        print("Index.bin:")
        for i in range(max_aux):
            index_record = self.read_index(num_dat+i)
            print(num_dat+i, index_record, "->", self._read_record(index_record.pos))
        print("Fin de la lista")
        print("====================================")

    def inorder_aux(self , pos : int , l :list):
        """
        Realiza un recorrido inorden del árbol B+.
        """
        if pos == -1:
            return
        index_record = self.read_index(pos)
        self.inorder_aux(index_record.next, l)
        l.append(pos)
    
    def inorder(self):
        """
        Realiza un recorrido inorden .
        """
        list = []
        pos_root, num_dat, _ = self._read_header()
        if pos_root == -1:
            print("El árbol está vacío.")
            return
        print("====================================")
        print("Recorrido inorden:")
        self.inorder_aux(pos_root,list)
        for i in range(len(list) - 1, -1, -1):
            index_record = self.read_index(list[i])
            print( list[i] , index_record, "->", self._read_record(index_record.pos))
        print()
        print("Fin del recorrido inorden.")
        print("====================================")



        

                

            


                


        






                



        


        

        




        
    


