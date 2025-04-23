D = 3
MAX_RECORDS = 3

def posbucket (x):
    b = bin(x % 2**D)[2:]
    return b.zfill(D)

class Bucket:
    def __init__(self, splitable=True):
        self.records = []
        self.full = 0
        self.overflow = None
        self.splitable = splitable

    def insert(self, record):
        if self.full < MAX_RECORDS:
            self.records.append(record)
            self.full += 1
            return True
        else:
            if self.splitable:
                return False
            else:
                if self.overflow is None:
                    self.overflow = Bucket(splitable=False)
                self.overflow.insert(record)
                return True

    def search(self, record):
        if record in self.records:
            return True
        elif self.overflow is not None:
            return self.overflow.search(record)
        else:
            return False

    def delete(self, record):
        if record in self.records:
            self.records.remove(record)
            self.full -= 1
            return True
        elif self.overflow is not None:
            return self.overflow.delete(record)
        else:
            return False

class Node:
    def __init__(self, bucket, level):
        self.bucket = bucket
        self.zero = None
        self.one = None
        self.level = level

    def split(self):
        self.bucket = None
        if self.level == 1:
            print("Splitting bucket")
            self.zero = Node(Bucket(splitable=False), self.level - 1)
            self.one = Node(Bucket(splitable=False), self.level - 1)
        else:
            self.zero = Node(Bucket(), self.level - 1)
            self.one = Node(Bucket(), self.level - 1)

    def insert(self, record, hash):
        if self.bucket is None:
            if hash[D - self.level] == "0":
                return self.zero.insert(record, hash)
            else:
                return self.one.insert(record, hash)
        else:
            if self.bucket.insert(record):
                return True
            else:
                records = self.bucket.records
                records.append(record)
                self.split()
                for r in records:
                    hash = posbucket(r)
                    if hash[D - self.level] == "0":
                        self.zero.insert(r, hash)
                    else:
                        self.one.insert(r, hash)


    def print(self, prefix=""):
        if self.bucket is not None:
            print(f"Bucket ({prefix}):", self.bucket.records)
            current = self.bucket
            while current.overflow is not None:
                current = current.overflow
                print(f"  Overflow ({prefix}):", current.records)
        else:
            self.zero.print(prefix + "0")
            self.one.print(prefix + "1")

    def search(self, record, hash):
        if self.bucket is not None:
            return self.bucket.search(record)
        else:
            if hash[D - self.level] == "0":
                return self.zero.search(record, hash)
            else:
                return self.one.search(record, hash)

    def delete(self, record, hash):
        if self.bucket is not None:
            if self.bucket.records.remove(record):
                self.bucket.full -= 1
                if self.bucket.full == 0:
                    self.bucket = None
                return True

        else:
            if hash[D - self.level] == "0":
                return self.zero.delete(record, hash)
            else:
                return self.one.delete(record, hash)

class ExtensibleHash:
    def __init__(self):
        self.head = Node(Bucket(), D)
        self.head.split()

    def insert(self, record):
        hash = posbucket(record)
        if self.head.insert(record, hash):
            return True

    def search(self, record):
        hash = posbucket(record)
        return self.head.search(record, hash)

    def delete(self, record):
        hash = posbucket(record)
        return self.head.delete(record, hash)

    def print(self):
        print("Printing buckets")
        self.head.print()

eh = ExtensibleHash()

while True:
    op = input("{insertar o search} + num:")
    if op[0] == "i":
        record = int(op[1:])
        eh.insert(record)
    if op[0] == "s":
        record = int(op[1:])
        if eh.search(record):
            print(f"{record} encontrado")
        else:
            print(f"{record} no encontrado")
    eh.print()