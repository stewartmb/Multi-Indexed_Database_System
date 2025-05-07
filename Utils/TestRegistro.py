import unittest
from Registro import RegistroType

class TestRegistroType(unittest.TestCase):

    def setUp(self):
        self.dict_format = {'id': 'Q', 'name': '20s', 'age': 'i'}

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

        self.registro_string = RegistroType({'STRING': '5s'}, key_index=0)  # Cadena de 20 caracteres
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
        self.assertEqual(restored_data3[0], "texto")
        self.assertEqual(restored_data4[0], "12345")

        self.registro_string = RegistroType({'STRING': '200s'}, key_index=0)  # Cadena de 20 caracteres
        byte_data = self.registro_string.to_bytes(["Texto"])
        restored_data1 = self.registro_string.from_bytes(byte_data)
        byte_data = self.registro_string.to_bytes([""])
        restored_data2 = self.registro_string.from_bytes(byte_data)
        byte_data = self.registro_string.to_bytes(["lorem ipsum. \\habia una vez \n wa"])
        restored_data3 = self.registro_string.from_bytes(byte_data)
        byte_data = self.registro_string.to_bytes(["1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"])
        restored_data4 = self.registro_string.from_bytes(byte_data)

        self.assertEqual(restored_data1[0], "Texto")
        self.assertEqual(restored_data2[0], "")
        self.assertEqual(restored_data3[0], "lorem ipsum. \\habia una vez \n wa")
        self.assertEqual(restored_data4[0], "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890")

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

    def test_init_with_key_name(self):
        reg = RegistroType(self.dict_format, key_name='name')
        self.assertEqual(reg.key, 'name')
        self.assertEqual(reg.key_index, 1)

    def test_init_with_key_index(self):
        reg = RegistroType(self.dict_format, key_index=2)
        self.assertEqual(reg.key, 'age')
        self.assertEqual(reg.key_index, 2)

    def test_key_name_priority_over_index(self):
        reg = RegistroType(self.dict_format, key_index=0, key_name='age')
        self.assertEqual(reg.key, 'age')
        self.assertEqual(reg.key_index, 2)

    def test_invalid_key_name_raises(self):
        with self.assertRaises(ValueError):
            RegistroType(self.dict_format, key_name='not_found')

    def test_invalid_key_index_raises(self):
        with self.assertRaises(IndexError):
            RegistroType(self.dict_format, key_index=5)

    def test_no_key_name_or_index_raises(self):
        with self.assertRaises(ValueError):
            RegistroType(self.dict_format)