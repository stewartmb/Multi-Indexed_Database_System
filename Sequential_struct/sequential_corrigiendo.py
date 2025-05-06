import struct
import os
import math

class Record:
    def __init__(self, id=-1, name="", codigo=-1, date="", deleted=False, next=-1, aux=False):
        self.id = id
        self.name = name
        self.codigo = codigo
        self.date = date
        self.next = next
        self.deleted = deleted
        self.aux = aux

    def __str__(self):
        return f'{self.id} | {self.name} | {self.codigo} | {self.date} | next: {self.next}{"a" if self.aux else "d"} | {"[DELETED]" if self.deleted else ""}'

    def key(self):
        return self.id

    def is_deleted(self):
        return self.deleted

    def is_smaller(self, val):
        return self.key() <= val

    def to_binary(self):
        format_str = 'i30si10si??'  # id (4), name (30), codigo (4), date (10), next (4), deleted (1), aux (1)
        packed = struct.pack(format_str, self.id, self.name.encode().ljust(30, b'\x00'),
                           self.codigo, self.date.encode().ljust(10, b'\x00'), self.next, 
                           self.deleted, self.aux)
        return packed

    @staticmethod
    def from_binary(data):
        id, name, codigo, date, next, deleted, aux = struct.unpack('i30si10si??', data)
        return Record(id, name.decode().strip(), codigo, date.decode().strip(), deleted, next, aux)

class Sequential:
    def __init__(self, filename, k=5, maxi=10):
        self.filename = filename
        self.aux_filename = "aux.bin"
        self.HEADER_SIZE = struct.calcsize("i?ii")  # start_pos (4), aux (1), k_count (4), aux_count (4)
        self.k = k  # limite de eliminaciones para reconstruir
        self.maxi = maxi  # max registros en aux para reconstruir
        self.k_count = 0  # contador para k
        self.aux_count = 0  # contador para maxi de aux

        if not os.path.exists(self.filename):
            with open(self.filename, 'wb') as f:
                f.write(struct.pack("i?ii", -1, False, 0, 0))  #header  start_pos aux k_count aux_count

        self.RECORD_SIZE = struct.calcsize('i30si10si??')

    def write_start(self, start_pos, aux):
        with open(self.filename, 'r+b') as f:
            f.write(struct.pack("i?ii", start_pos, aux, self.k_count, self.aux_count))  # Usar self.k_count y self.aux_count

    def write_header(self, start_pos, aux, k_count, aux_count):
        with open(self.filename, 'r+b') as f:
            f.write(struct.pack("i?ii", start_pos, aux, k_count, aux_count))
            self.k_count = k_count
            self.aux_count = aux_count
    
    def get_start(self):
        with open(self.filename, 'rb') as f:
            data = f.read(self.HEADER_SIZE)
            if len(data) < self.HEADER_SIZE:
                return -1, False, 0 , 0
            return struct.unpack("i?ii", data)

    def get_header(self):
        with open(self.filename, 'rb') as f:
            data = f.read(self.HEADER_SIZE)
            if len(data) < self.HEADER_SIZE:
                return -1, False, 0, 0
            start_pos, aux, k_count, aux_count = struct.unpack("i?ii", data)
            self.k_count = k_count
            self.aux_count = aux_count
            return start_pos, aux, k_count, aux_count

    def get_record_at(self, aux, pos):
        filename = self.aux_filename if aux else self.filename
        try:
            with open(filename, "rb") as f:
                offset = self.HEADER_SIZE + pos * self.RECORD_SIZE if not aux else pos * self.RECORD_SIZE
                f.seek(offset)
                data = f.read(self.RECORD_SIZE)
                if len(data) < self.RECORD_SIZE:
                    return None
                return Record.from_binary(data)
        except FileNotFoundError:
            return None

    def get_end(self, aux):
        if aux:
            with open(self.aux_filename, "ab+") as f:
                f.seek(0, 2)  # Move the pointer to the end of the file
                end = (f.tell()-self.HEADER_SIZE) // self.RECORD_SIZE  # Calculate the number of records in the file
            return end
        else:
            with open(self.filename, "ab+") as f:
                f.seek(0, 2)  # Move the pointer to the end of the file
                end = (f.tell()-self.HEADER_SIZE) // self.RECORD_SIZE  # Calculate the number of records in the file
            return end
    
    def write_record_end(self, aux, record):
        filename = self.aux_filename if aux else self.filename
        with open(filename, "ab") as f:
            pos = (f.tell() - (self.HEADER_SIZE if not aux else 0)) // self.RECORD_SIZE
            f.write(record.to_binary())
            return pos

    def write_record_at(self, record, pos, aux):
        filename = self.aux_filename if aux else self.filename
        with open(filename, "r+b") as f:
            offset = self.HEADER_SIZE + pos * self.RECORD_SIZE if not aux else pos * self.RECORD_SIZE
            f.seek(offset)
            f.write(record.to_binary())
           
    def binary_search(self, key):
        with open(self.filename, "rb") as f:
            f.seek(0, 2)
            file_size = f.tell()
            if file_size <= self.HEADER_SIZE:
                return -1
            num_records = (file_size - self.HEADER_SIZE) // self.RECORD_SIZE

        left, right = 0, num_records - 1
        result = -1

        while left <= right:
            mid = (left + right) // 2
            record = self.get_record_at(False, mid)
            if record is None:
                break

            if record.key() < key:
                result = mid
                left = mid + 1
            else:
                right = mid - 1

        return result

    def print_all(self):
        print("\nContenido del archivo principal:")
        start_pos, start_aux, k_count, aux_count = self.get_header()
        print(f"Header - Start: {start_pos}{'a' if start_aux else 'd'}, K Count: {k_count}, Aux Count: {aux_count}")

        with open(self.filename, "rb") as f:
            f.seek(self.HEADER_SIZE)
            pos = 0
            while True:
                data = f.read(self.RECORD_SIZE)
                if not data or len(data) < self.RECORD_SIZE:
                    break
                record = Record.from_binary(data)
                if record:
                    print(f"Pos {pos}d: {record}")
                pos += 1

        print("\nContenido del archivo auxiliar:")
        try:
            with open(self.aux_filename, "rb") as f:
                pos = 0
                while True:
                    data = f.read(self.RECORD_SIZE)
                    if not data or len(data) < self.RECORD_SIZE:
                        break
                    record = Record.from_binary(data)
                    if record:
                        print(f"Pos {pos}a: {record}")
                    pos += 1
        except FileNotFoundError:
            print("No existe archivo auxiliar")

    def insert(self, record):
    # Check if main file is empty (only has header)
        with open(self.filename, "rb") as f:
            f.seek(0, 2)
            file_size = f.tell()

        if file_size <= self.HEADER_SIZE:  # Only has header
            self.write_start(0, False)  # First record at position 0 in main file
            self.write_record_at(record, 0, False)
            return

        # Find insertion position using binary search
        pos = self.binary_search(record.key())
        start_pos, start_aux, _, _ = self.get_start()

        # Case 1: Insert at beginning (new smallest key)
        if pos == -1:
            prev = self.get_record_at(start_aux, start_pos)
            if prev.next == -1:
                new_pos = self.write_record_end(True, record)
                self.aux_count += 1
                record.next = start_pos
                record.aux = start_aux
                self.write_record_at(record, new_pos, True)
                self.write_start(new_pos, True)
            else:
                temp = self.get_record_at(prev.aux, prev.next)
                prev_pos, prev_aux = start_pos, start_aux

                first = True
                if start_aux != False:
                    while temp.next != -1 or temp.is_smaller(record.id):
                        prev_pos, prev_aux = prev.next, prev.aux
                        first = False
                        prev = self.get_record_at(prev.aux, prev.next)
                        temp = self.get_record_at(temp.aux, temp.next)

                if first:
                    new_pos = self.write_record_end(True, record)
                    self.aux_count += 1
                    record.next = start_pos
                    record.aux = start_aux
                    self.write_record_at(record, new_pos, True)
                    self.write_start(new_pos, True)
                else:
                    record.next, record.aux = prev.next, prev.aux
                    new_pos = self.write_record_end(True, record)
                    self.aux_count += 1 
                    prev.next, prev.aux = new_pos, True

                self.write_record_at(prev, prev_pos, prev_aux)
            return

        current = self.get_record_at(False, pos)
        if current is None:
            return

        # Case 2: Insert at end of list
        if current.next == -1:
            new_pos = self.write_record_end(False, record)
            current.next = new_pos
            current.aux = False
            self.write_record_at(current, pos, False)
            return

        # Case 3: Insert in middle of list
        next_record = self.get_record_at(current.aux, current.next)
        if next_record and record.key() > current.key() and record.key() < next_record.key():
            record.next = current.next
            record.aux = current.aux
            new_pos = self.write_record_end(True, record)
            self.aux_count += 1 
            current.next = new_pos
            current.aux = True
            self.write_record_at(current, pos, False)
        else:
            prev_record = current
            prev_pos = pos
            prev_aux = False
            next_pos = current.next
            next_aux = current.aux

            while next_pos != -1:
                next_record = self.get_record_at(next_aux, next_pos)
                if not next_record or record.key() < next_record.key():
                    break
                prev_record = next_record
                prev_pos = next_pos
                prev_aux = next_aux
                next_pos = next_record.next
                next_aux = next_record.aux

            record.next = prev_record.next
            record.aux = prev_record.aux
            new_pos = self.write_record_end(True, record)
            self.aux_count += 1
            prev_record.next = new_pos
            prev_record.aux = True
            self.write_record_at(prev_record, prev_pos, prev_aux)

        self.write_header(*self.get_start()[:2], self.k_count, self.aux_count)

        if self.aux_count >= self.maxi:
            self.rebuild()

    def rebuild(self):
        print("\nIniciando proceso de reconstrucción...")
        ordered_records = []
        start_pos, start_aux, _, _ = self.get_header()
        pos, aux = start_pos, start_aux

        while pos != -1:
            record = self.get_record_at(aux, pos)
            if record is None:
                break
            if not record.deleted:
                ordered_records.append(record)
            pos = record.next
            aux = record.aux

        temp_main = "test.bin"
        temp_aux = "aux.bin"

        with open(temp_main, 'wb') as f_main:
            f_main.write(struct.pack("i?ii", 0, False, 0, 0))

            for i, record in enumerate(ordered_records):
                record.next = i+1 if i+1 < len(ordered_records) else -1
                record.aux = False
                record.deleted = False
                f_main.write(record.to_binary())

        open(temp_aux, 'wb').close()
        
        os.replace(temp_main, self.filename)
        os.replace(temp_aux, self.aux_filename)
        
        self.k_count = 0
        self.aux_count = 0

    def search(self, key):
        pos = self.binary_search(key)
        if pos == -1:
            start_pos, start_aux, _, _ = self.get_header()
            if start_pos == -1:
                return None
            record = self.get_record_at(start_aux, start_pos)
        else:
            record = self.get_record_at(False, pos)

        while record:
            if not record.deleted and record.id == key:
                return record
            if record.next == -1:
                break
            record = self.get_record_at(record.aux, record.next)

        return None

    def search_range(self, mini, maxi):
        results = []
        pos = self.binary_search(mini)
        
        if pos == -1:
            start_pos, start_aux, _, _ = self.get_header()
            pos, aux = start_pos, start_aux
        else:
            aux = False

        current = self.get_record_at(aux, pos)
        
        while current and current.key() <= maxi:
            if not current.deleted and current.key() >= mini:
                results.append(current)
            if current.next == -1:
                break
            current = self.get_record_at(current.aux, current.next)

        return results

    def delete(self, key):
        start_pos, start_aux, _, _ = self.get_header()
        if start_pos == -1:
            return False

        prev_pos = -1
        prev_aux = False
        current_pos = start_pos
        current_aux = start_aux

        while current_pos != -1:
            record = self.get_record_at(current_aux, current_pos)
            if not record:
                break

            if record.id == key and not record.deleted:
                record.deleted = True
                self.write_record_at(record, current_pos, current_aux)
                self.k_count += 1

                if prev_pos == -1: 
                    self.write_header(record.next, record.aux, self.k_count, self.aux_count)
                else:
                    prev_record = self.get_record_at(prev_aux, prev_pos)
                    if prev_record:
                        prev_record.next = record.next
                        prev_record.aux = record.aux
                        self.write_record_at(prev_record, prev_pos, prev_aux)
                        self.write_header(start_pos, start_aux, self.k_count, self.aux_count)

                if self.k_count >= self.k:
                    self.rebuild()
                    
                return True

            prev_pos = current_pos
            prev_aux = current_aux
            current_pos = record.next
            current_aux = record.aux

        return False