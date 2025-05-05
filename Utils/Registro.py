import struct

class RegistroType:
    """
    Estructura que maneja el control de los registros.
    size = espacio en bytes
    FORMAT = formato de los registros (struct)
    dict_format = formato de los registros (diccionario)
    to_bytes = convierte el registro a bytes
    from_bytes = convierte bytes a un registro
    get_key = obtiene el valor del indice de ordenamiento del registro
    """
    def __init__(self, dict_format, key_index: int):
        self.dict_format = dict_format
        self.keyIndex = key_index
        self.key = list(dict_format.keys())[key_index]
        self.FORMAT = ''.join(dict_format.values())
        self.size = struct.calcsize(self.FORMAT)

    def to_bytes(self, args: list) -> bytes:
        """
        Convierte el registro a bytes.
        """
        types = list(self.dict_format.values())
        for i in range(len(args)):
            if types[i] == 'i':
                args[i] = int(args[i])
            elif types[i] == 'q':
                args[i] = int(args[i])
            elif types[i] == 'Q':
                args[i] = int(args[i])
            elif types[i] == 'f':
                args[i] = float(args[i])
            elif types[i] == 'd':
                args[i] = float(args[i])
            elif types[i] == '?':
                args[i] = bool(args[i])
            else:
                args[i] = args[i].encode('utf-8').ljust(20, b'\x00')

        return struct.pack(self.FORMAT, *args)

    def from_bytes(self, data: bytes) -> list:
        """
        Convierte bytes a un registro.
        """
        unpacked = list(struct.unpack(self.FORMAT, data))
        types = list(self.dict_format.values())
        for i in range(len(unpacked)):
            if types[i] == 'i':
                unpacked[i] = int(unpacked[i])
            elif types[i] == 'q':
                unpacked[i] = int(unpacked[i])
            elif types[i] == 'Q':
                unpacked[i] = int(unpacked[i])
            elif types[i] == 'f':
                unpacked[i] = float(unpacked[i])
            elif types[i] == 'd':
                unpacked[i] = float(unpacked[i])
            elif types[i] == '?':
                unpacked[i] = bool(unpacked[i])
            else:
                unpacked[i] = unpacked[i].decode('utf-8').strip('\x00')
        return unpacked

    def get_key(self, lista: list) -> any:
        return lista[self.keyIndex]