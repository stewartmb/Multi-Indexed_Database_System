import random
import string
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

        def generar_string_aleatorio(n):
            caracteres = string.ascii_letters + string.digits  # Letras y números
            return ''.join(random.choices(caracteres, k=n))

        table_format = {"nombre": "12s", "edad": "i", "altura": "d"}
        hash = Hash(table_format, "nombre")

        for i in range(100):
            nombre = generar_string_aleatorio(random.randint(6, 12))
            edad = random.randint(0, 100)
            altura = random.uniform(1.50, 2.00)
            hash.insert([nombre, edad, altura])

        # Search for a range of records
        resultado = hash.range_search("ba", "se")
        print(resultado)



    def test_delete(self):
        for i in range(0, 100):
            self.hash.insert(["NOMBRE", i, 1.75])

        # Delete a record
        wasDeleted = self.hash.delete(50)
        print(wasDeleted)
        self.assertEqual(wasDeleted, True)
        wasDeleted = self.hash.delete(200)
        print(wasDeleted)
        self.assertEqual(wasDeleted, False)

        # Check if the record was deleted
        self.assertEqual(self.hash.search(50), None)

    def test_random_operations(self):
        data = []
        for i in range(0, 100):
            self.hash.insert(["NOMBRE", i, 1.7523])
            data.append(i)

        for _ in range(0, 1000):
            operation = random.choice(["i", "s", "rs", "d"])

            if operation == "i":
                i = random.randint(0, 1000)
                while i in data:
                    i = random.randint(0, 1000)
                print(f"Inserting: {i}")
                self.hash.insert(["NOMBRE", i, 1.7523])
                data.append(i)
                self.assertEqual(self.hash.search(i)[1], i)
            elif operation == "s":
                if len(data) > 0:
                    i = random.choice(data)
                    print(f"Searching: {i}")
                    self.assertEqual(self.hash.search(i)[1], i)
            elif operation == "rs":
                if len(data) > 0:
                    i = random.choice(data)
                    print(f"Range Searching: {i} to {i + 10}")
                    ans = self.hash.range_search(i, i + 10)
                    ans.sort(key=lambda x: x[1])
                    self.assertEqual(ans[0][1], i)
            elif operation == "d":
                if len(data) > 0:
                    i = random.choice(data)
                    print(f"Deleting: {i}")
                    self.hash.delete(i)
                    data.remove(i)
                    ans = self.hash.search(i)
                    print(ans)
                    self.assertEqual(ans, None)
