import pickle
import struct
import os


def getbits(dato, nbits):
    if isinstance(dato, int): # numeros
        bits = bin(dato & (2 ** (nbits * 8) - 1))[2:]
    else:
        if isinstance(dato, str): # texto
            dato_bytes = dato.encode('utf-8')
        else: # otros
            dato_bytes = pickle.dumps(dato)

        bits = ''.join(f'{byte:08b}' for byte in dato_bytes)
    return bits[-nbits:] if nbits <= len(bits) else bits.zfill(nbits)


class Bucket:
    def __init__(self, local_depth, fullness):
        self.local_depth = local_depth



class ExtensibleHash:
    def __init__(self, name_index_file='index_file.bin', name_data_file='data_file.bin',
                 global_depth = 3, max_records = 3):
        self.index_file = name_index_file
        self.data_file = name_data_file
        self.global_depth = global_depth
        self.max_records = max_records
        self.header = 4
        self.hashindex = 4 * 2**global_depth
        self.BUCKET_FORMAT = 'i' * max_records + 'iii'
        self.bucket_size = struct.calcsize(self.BUCKET_FORMAT)
        self._initialize_files(global_depth, force=True)


    def _initialize_files(self, global_depth, force=False):
        if force or not os.path.exists(self.index_file):
            with open(self.index_file, 'wb') as f:
                f.write(struct.pack('i', global_depth))
                for i in range(2 ** global_depth):
                    if i % 2 == 0:
                        f.write(struct.pack('i', 0))
                    else:
                        f.write(struct.pack('i', 1))

                # [0,0,0...0,0,0] + [localdepth, fullness, overflowPosition]
                f.write(struct.pack(self.BUCKET_FORMAT, *([0] * self.max_records + [1,0,-1])))
                f.write(struct.pack(self.BUCKET_FORMAT, *([0] * self.max_records + [1,0,-1])))











# def posbucket (x):
#     b = bin(x % 2 ** MAX_D)[2:]
#     return b.zfill(MAX_D)
#
# class Bucket:
#     def __init__(self, splitable=True):
#         self.records = []
#         self.full = 0
#         self.overflow = None
#         self.splitable = splitable
#
#     def insert(self, record):
#         if self.full < MAX_RECORDS:
#             self.records.append(record)
#             self.full += 1
#             return True
#         else:
#             if self.splitable:
#                 return False
#             else:
#                 if self.overflow is None:
#                     self.overflow = Bucket(splitable=False)
#                 self.overflow.insert(record)
#                 return True
#
#     def search(self, record):
#         if record in self.records:
#             return True
#         elif self.overflow is not None:
#             return self.overflow.search(record)
#         else:
#             return False
#
#     def delete(self, record):
#         if record in self.records:
#             self.records.remove(record)
#             self.full -= 1
#             return True
#         elif self.overflow is not None:
#             return self.overflow.delete(record)
#         else:
#             return False
#
# class Node:
#     def __init__(self, bucket, level):
#         self.bucket = bucket
#         self.zero = None
#         self.one = None
#         self.level = level
#
#     def split(self):
#         self.bucket = None
#         if self.level == 1:
#             print("Splitting bucket")
#             self.zero = Node(Bucket(splitable=False), self.level - 1)
#             self.one = Node(Bucket(splitable=False), self.level - 1)
#         else:
#             self.zero = Node(Bucket(), self.level - 1)
#             self.one = Node(Bucket(), self.level - 1)
#
#     def insert(self, record, hash):
#         if self.bucket is None:
#             if hash[MAX_D - self.level] == "0":
#                 return self.zero.insert(record, hash)
#             else:
#                 return self.one.insert(record, hash)
#         else:
#             if self.bucket.insert(record):
#                 return True
#             else:
#                 records = self.bucket.records
#                 records.append(record)
#                 self.split()
#                 for r in records:
#                     hash = posbucket(r)
#                     if hash[MAX_D - self.level] == "0":
#                         self.zero.insert(r, hash)
#                     else:
#                         self.one.insert(r, hash)
#
#
#     def print(self, prefix=""):
#         if self.bucket is not None:
#             print(f"Bucket ({prefix}):", self.bucket.records)
#             current = self.bucket
#             while current.overflow is not None:
#                 current = current.overflow
#                 print(f"  Overflow ({prefix}):", current.records)
#         else:
#             self.zero.print(prefix + "0")
#             self.one.print(prefix + "1")
#
#     def search(self, record, hash):
#         if self.bucket is not None:
#             return self.bucket.search(record)
#         else:
#             if hash[MAX_D - self.level] == "0":
#                 return self.zero.search(record, hash)
#             else:
#                 return self.one.search(record, hash)
#
#     def delete(self, record, hash):
#         if self.bucket is not None:
#             if self.bucket.records.remove(record):
#                 self.bucket.full -= 1
#                 if self.bucket.full == 0:
#                     self.bucket = None
#                 return True
#
#         else:
#             if hash[MAX_D - self.level] == "0":
#                 return self.zero.delete(record, hash)
#             else:
#                 return self.one.delete(record, hash)
#
# class ExtensibleHash:
#     def __init__(self):
#         self.head = Node(Bucket(), MAX_D)
#         self.head.split()
#
#     def insert(self, record):
#         hash = posbucket(record)
#         if self.head.insert(record, hash):
#             return True
#
#     def search(self, record):
#         hash = posbucket(record)
#         return self.head.search(record, hash)
#
#     def delete(self, record):
#         hash = posbucket(record)
#         return self.head.delete(record, hash)
#
#     def print(self):
#         print("Printing buckets")
#         self.head.print()

eh = ExtensibleHash()