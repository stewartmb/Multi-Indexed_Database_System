import pickle
import struct

def getbits(dato, nbits):
    """
    toma los ultimos n bits de un dato en binario.
    :param dato: dato a convertir
    :param nbits: cantidad de bits a tomar
    """
    if isinstance(dato, int): # int
        bits = bin(dato & (2 ** (nbits * 8) - 1))[2:]
    elif isinstance(dato, float): # float
        dato_bytes = struct.pack('>f', dato)
        bits = ''.join(f'{byte:08b}' for byte in dato_bytes)
    else:
        if isinstance(dato, str): # texto
            dato_bytes = dato.encode('utf-8')
        else: # otros
            dato_bytes = pickle.dumps(dato)

        bits = ''.join(f'{byte:08b}' for byte in dato_bytes)
    return bits[-nbits:] if nbits <= len(bits) else bits.zfill(nbits)



print(getbits('Hola', 64))
print(getbits(13, 64))
print(getbits(0.25, 64))