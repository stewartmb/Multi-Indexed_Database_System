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

class Index_Page():
    def __init__(self, leaf=True, M=None):
        self.leaf = leaf
        self.keys = [None] * (M)
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
        instance.next = unpacked[-2]
        instance.key_count = unpacked[-1]

        return instance
    

def get_index_format(M, format_key): # Se hizo con la finalidad que al variar M, el formato del índice cambie automáticamente
    """
    Genera el formato del índice dinámicamente basado en M.
    """
    format = f'b{(M-1) * format_key}{M * "i"}ii'
    return format
