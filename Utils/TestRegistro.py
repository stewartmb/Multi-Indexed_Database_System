import unittest
from Utils.Registro import RegistroType

class TestRegistroType(unittest.TestCase):

    def setUp(self):

        self.registro_int = RegistroType({'INT': 'i'}, key_index=0)  # Entero (4 bytes)
        self.registro_uint = RegistroType({'UINT': 'I'}, key_index=0)  # Entero sin signo (4 bytes)
        self.registro_short = RegistroType({'SHORT': 'h'}, key_index=0)  # Entero corto (2 bytes)
        self.registro_ushort = RegistroType({'USHORT': 'H'}, key_index=0)  # Entero corto sin signo
        self.registro_long = RegistroType({'LONG': 'l'}, key_index=0)  # Entero largo
        self.registro_ulong = RegistroType({'ULONG': 'L'}, key_index=0)  # Entero largo sin signo
        self.registro_float = RegistroType({'FLOAT': 'f'}, key_index=0)  # Flotante (4 bytes)
        self.registro_double = RegistroType({'DOUBLE': 'd'}, key_index=0)  # Doble precisión (8 bytes)
        self.registro_bool = RegistroType({'BOOL': '?'}, key_index=0)  # Booleano (1 byte)
        self.registro_char = RegistroType({'CHAR': 'c'}, key_index=0)  # Caracter (1 byte)


    def test_strings(self):
        self.registro_string = RegistroType({'STRING': '20s'}, key_index=0)  # Cadena de 20 caracteres
        byte_data = self.registro_string.to_bytes(["Texto"])
        restored_data1 = self.registro_string.from_bytes(byte_data)
        byte_data = self.registro_string.to_bytes([""])
        restored_data2 = self.registro_string.from_bytes(byte_data)
        byte_data = self.registro_string.to_bytes(["texto con espacios"])
        restored_data3 = self.registro_string.from_bytes(byte_data)
        byte_data = self.registro_string.to_bytes(["12345678901234567890123"])
        restored_data4 = self.registro_string.from_bytes(byte_data)

        self.assertEqual(restored_data1[0], "Texto")
        self.assertEqual(restored_data2[0], "")
        self.assertEqual(restored_data3[0], "texto con espacios")
        self.assertEqual(restored_data4[0], "12345678901234567890")

    def test_integers(self):
        self.registro_int = RegistroType({'INT': 'i'}, key_index=0)
        valores = [0, 1, -1, 2147483647, -2147483648]
        for v in valores:
            byte_data = self.registro_int.to_bytes([v])
            restored = self.registro_int.from_bytes(byte_data)
            self.assertEqual(restored[0], v)

    def test_floats(self):
        self.registro_float = RegistroType({'FLOAT': 'f'}, key_index=0)
        valores = [0.0, 1.5, -3.14, 1e10]
        for v in valores:
            byte_data = self.registro_float.to_bytes([v])
            restored = self.registro_float.from_bytes(byte_data)
            self.assertAlmostEqual(restored[0], v, places=5)

    def test_doubles(self):
        self.registro_double = RegistroType({'DOUBLE': 'd'}, key_index=0)
        valores = [0.0, 1.5, -3.1415926535, 1e300]
        for v in valores:
            byte_data = self.registro_double.to_bytes([v])
            restored = self.registro_double.from_bytes(byte_data)
            self.assertAlmostEqual(restored[0], v, places=10)

    def test_bools(self):
        self.registro_bool = RegistroType({'BOOL': '?'}, key_index=0)
        for v in [True, False]:
            byte_data = self.registro_bool.to_bytes([v])
            restored = self.registro_bool.from_bytes(byte_data)
            self.assertEqual(restored[0], v)

    def test_long_longs(self):
        self.registro_longlong = RegistroType({'LONGLONG': 'q'}, key_index=0)
        valores = [0, 1, -1, 9223372036854775807, -9223372036854775808]
        for v in valores:
            byte_data = self.registro_longlong.to_bytes([v])
            restored = self.registro_longlong.from_bytes(byte_data)
            self.assertEqual(restored[0], v)

    def test_unsigned_long_longs(self):
        self.registro_ulonglong = RegistroType({'ULONGLONG': 'Q'}, key_index=0)
        valores = [0, 1, 18446744073709551615]
        for v in valores:
            byte_data = self.registro_ulonglong.to_bytes([v])
            restored = self.registro_ulonglong.from_bytes(byte_data)
            self.assertEqual(restored[0], v)