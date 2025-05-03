import pickle
import random
import struct
import os

LEVEL = 2 # Número de niveles del árbol ISAM
MAX_REGISTERS_INDEX_PAGE = 5
MAX_REGISTERS_PAGE = 20
MAX_REGISTERS_PAGE_OVERFLOW = 5


### RECORD FORMAT ###
RECORD_FORMAT = '3s20s2s'  # Formato de los datos: 3s (codigo), 20s (nombre), 2s (ciclo)
TAM_REGISTRO = struct.calcsize(RECORD_FORMAT)  # Tamaño del registro en bytes

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
    
    def __str__(self):
        """
        Representación en cadena del registro.
        """
        list = [self.codigo, self.nombre, self.ciclo]
        return str(list)  # Devuelve una lista con los atributos del registro


    def __repr__(self):
        """
        Representación en cadena del registro.
        """
        return f"Registro(codigo={self.codigo}, nombre={self.nombre}, ciclo={self.ciclo})"
    

    def __eq__(self, other):
        """
        Compara dos registros por su código.
        """
        if isinstance(other, Registro):
            return self.codigo == other.codigo
        return False
    
import struct
from typing import List, Union

class IndexPage:
    # Formato para serialización/deserialización:
    # - 1 byte para el nivel (0=hoja, >0=nodo interno)
    # - 1 byte para el número de registros actual
    # - MAX_REGISTERS_INDEX_PAGE valores (enteros)
    # - MAX_REGISTERS_INDEX_PAGE + 1 punteros (enteros)
    STRUCT_FORMAT = f'BB{MAX_REGISTERS_INDEX_PAGE}i{MAX_REGISTERS_INDEX_PAGE + 1}i'
    
    def __init__(self, level: int = 0):
        self.level = level  # 0 para hojas, >0 para nodos internos
        self.keys: List[int] = []
        self.pointers: List[int] = []  # Pueden ser páginas de datos u otros index pages
        
    def is_leaf(self) -> bool:
        return self.level == 0
    
    def is_full(self) -> bool:
        return len(self.keys) >= MAX_REGISTERS_INDEX_PAGE
    
    def insert_key_pointer(self, key: int, pointer: int) -> bool:
        """Inserta una clave y su puntero asociado (manteniendo el orden)"""
        if self.is_full():
            return False
            
        # Encontrar posición para insertar
        pos = 0
        while pos < len(self.keys) and self.keys[pos] < key:
            pos += 1
            
        self.keys.insert(pos, key)
        
        # Para punteros: el puntero en posición i apunta a páginas con claves <= keys[i]
        # El puntero en posición i+1 apunta a páginas con claves > keys[i]
        if len(self.pointers) == 0:
            self.pointers.append(pointer)
        self.pointers.insert(pos + 1, pointer)
        
        return True
    
    def to_bytes(self) -> bytes:
        """Convierte el IndexPage a bytes para almacenamiento"""
        # Rellenar keys y pointers con ceros hasta alcanzar el tamaño máximo
        keys_padded = self.keys + [0] * (MAX_REGISTERS_INDEX_PAGE - len(self.keys))
        pointers_padded = self.pointers + [0] * (MAX_REGISTERS_INDEX_PAGE + 1 - len(self.pointers))
        
        return struct.pack(
            self.STRUCT_FORMAT,
            self.level,
            len(self.keys),
            *keys_padded,
            *pointers_padded
        )
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'IndexPage':
        """Crea un IndexPage a partir de bytes"""
        unpacked = struct.unpack(cls.STRUCT_FORMAT, data)
        
        level = unpacked[0]
        num_keys = unpacked[1]
        
        index_page = cls(level)
        
        # Extraer keys (solo las reales, no el padding)
        index_page.keys = list(unpacked[2:2 + num_keys])
        
        # Extraer pointers (hay num_keys + 1 punteros válidos)
        index_page.pointers = list(unpacked[2 + MAX_REGISTERS_INDEX_PAGE:2 + MAX_REGISTERS_INDEX_PAGE + num_keys + 1])
        
        return index_page
    
    def search(self, key: int) -> int:
        """Busca una clave y devuelve el puntero correspondiente"""
        if not self.keys:
            return self.pointers[0] if self.pointers else -1
            
        # Búsqueda binaria
        left, right = 0, len(self.keys) - 1
        while left <= right:
            mid = (left + right) // 2
            if self.keys[mid] == key:
                return self.pointers[mid + 1]
            elif self.keys[mid] < key:
                left = mid + 1
            else:
                right = mid - 1
                
        # Si no se encuentra exactamente, devolver el puntero adecuado
        return self.pointers[left]
    
    def __str__(self):
        return f"IndexPage(level={self.level}, keys={self.keys}, pointers={self.pointers})"


    
        
