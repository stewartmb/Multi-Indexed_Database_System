import unittest
from Hash_struct.Hash import Hash

class TestHash(unittest.TestCase):
    def setUp(self):
        self.table_format = {"nombre":"10s", "edad": "i", "altura": "d"}