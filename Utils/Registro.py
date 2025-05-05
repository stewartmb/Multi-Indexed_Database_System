import struct

class RegistroType:
    """
    Clase para manejar registros binarios.

    Attributes:
        dict_format (dict): Un diccionario que define el formato del registro.
        FORMAT (str): Una cadena que representa el formato struct de los datos
        size (int): El tamaño del registro en bytes.
        key (str): El nombre de la clave que se utilizará como índice.
    """

    def __init__(self, dict_format: dict, key_index: int = None, key_name: str = None):
        """
        Inicializa la clase RegistroType. Necesita un diccionario donde las claves
        son los nombres de los atributos del registro y los valores son los tipos de datos
        en formato struct. Además necesita un índice o un nombre de clave para identificar el registro.
        (En caso de que se brinden ambos se da preferencia al nombre de clave).
        Parameters:
            dict_format: Un diccionario que define el formato del registro.
            key_index: Índice del campo clave en el registro.
            key_name: Nombre del campo clave en el registro.
        """
        self.dict_format = dict_format
        self.FORMAT = ''.join(dict_format.values())
        self.size = struct.calcsize(self.FORMAT)

        if key_name is not None:
            if key_name not in dict_format:
                raise ValueError(f"Key name '{key_name}' not found in dict_format.")
            self.key = key_name
            self.key_index = list(dict_format.keys()).index(key_name)
        elif key_index is not None:
            keys = list(dict_format.keys())
            if not (0 <= key_index < len(keys)):
                raise IndexError(f"key_index {key_index} out of range.")
            self.key_index = key_index
            self.key = keys[key_index]
        else:
            raise ValueError("You must provide either key_name or key_index.")

    def to_bytes(self, args: list) -> bytes:
        """
        Convierte el registro (como lista de python) a bytes.
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
        Convierte bytes a un registro (como lista de python).
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
        return lista[self.key_index]