import random
import unittest
from Hash_struct.Hash import Hash

class TestHash(unittest.TestCase):
    def setUp(self):
        self.table_format = {"nombre":"12s", "edad": "i", "altura": "d"}
        self.hash = Hash(self.table_format, "edad")
        self.K = 100
        nums = random.sample(range(100, 1000), self.K)
        self.placed = nums[0:self.K // 2]
        self.not_placed = nums[self.K // 2:self.K]

    def test_insert_search(self):
        for i in range(self.K//2):
            self.hash.insert(["NOMBRE", self.placed[i], 1.75])

        # Search for the inserted records
        for i in range(self.K//2):
            if self.hash.search(self.placed[i]) is not None:
                self.assertEqual(self.hash.search(self.placed[i])[1], self.placed[i])

        # Search for records that were not inserted
        for i in range(self.K//2):
            self.assertEqual(self.hash.search(self.not_placed[i]), None)

    def test_range_search(self):
        for i in range(80, 215):
            self.hash.insert(["NOMBRE", i, 1.75])

        # Search for a range of records
        print(self.hash.range_search(100, 200))