import random
import unittest
from Hash_struct.Hash import Hash

class TestHash(unittest.TestCase):
    def setUp(self):
        self.table_format = {"nombre":"12s", "edad": "i", "altura": "d"}
        self.hash_table = Hash(self.table_format, "edad")
        self.K = 200
        nums = random.sample(range(100, 1000), self.K)
        self.placed = nums[0:self.K // 2]
        self.not_placed = nums[self.K // 2:self.K]

    def test_insert(self):


        for i in range(self.K//2):
            self.hash_table.insert(["NOMBRE", self.placed[i], 1.75])

        # Search for the inserted records
        for i in range(self.K//2):
            if self.hash_table.search(self.placed[i]) is not None:
                self.assertEqual(self.hash_table.search(self.placed[i])[1], self.placed[i])

        # Search for records that were not inserted
        for i in range(self.K//2):
            self.assertFalse(self.hash_table.search(self.not_placed[i]))

    def test_search(self):
        # Insert a record
        self.hash_table.insert(["NOMBRE", 25, 1.75])

        for i in range(self.K//2):
            self.hash_table.insert(["NOMBRE", self.placed[i], 1.75])
        self.hash_table.search(25)
