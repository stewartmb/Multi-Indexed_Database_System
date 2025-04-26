import pickle
import struct
import os

indexFile = []
dataFile = []


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


class RegistroType:
    def __init__(self, estructura: dict, index_key: int):
        self.estructura = estructura
        self.index_key = index_key
        self.FORMAT = ''.join(str(valor) for valor in self.estructura.values())
        self.size = struct.calcsize(self.FORMAT)
        self.cantidad_atributos = len(estructura)

    def to_bytes(self, registro):
        """
        Convierte un registro a bytes.
        :param registro: registro a convertir
        """
        return struct.pack(self.FORMAT, *registro)

    def from_bytes(cls, data, estructura):
        """
        Convierte bytes a un registro.
        :param data: datos en bytes
        :param estructura: estructura del registro
        """
        print(struct.unpack(cls.FORMAT, data))
        return



table_format = {"nombre":"10s", "apellido":"20s", "edad": "i", "ciudad": "25s"}
index_key = 2



# Crear una instancia de RegistroType
reg = RegistroType(table_format, index_key)


b = reg.to_bytes(['Juan', 'Perez', 25, 'Madrid'])

