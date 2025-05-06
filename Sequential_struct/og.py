import struct
import os
import pandas as pd
import csv
import time
import matplotlib.pyplot as plt
import math

class Record:
    def __init__(self, id=-1, name="", cant=-1, price=-1, date="", deleted=False, next=-1, aux=False):
        self.id = id
        self.name = name
        self.cant = cant
        self.price = price
        self.date = date
        self.next = next
        self.deleted = deleted
        self.aux = aux

    def __str__(self):
        return f'{self.id} | {self.name} | {self.cant} | {self.price} | {self.date} | next: {self.next} | aux: {self.aux}'

    def key(self):
        return self.id

    def is_deleted(self):
        return self.deleted

    def is_smaller(self, val):
        return self.key() <= val

    def to_binary(self):
        format_str = 'i30sif10si??'
        packed = struct.pack(format_str, 
                            self.id,
                            self.name.encode().ljust(30, b'\x00'),
                            self.cant, 
                            self.price,
                            self.date.encode().ljust(10, b'\x00'),
                            self.next, 
                            self.deleted,
                            self.aux)
        return packed

    @staticmethod
    def from_binary(data):
        #try:
        id, name, cant, price, date, next, deleted, aux = struct.unpack('i30sif10si??', data)
        return Record(id, name.decode().strip(), cant, price, date.decode().strip(), deleted, next, aux)
        # except struct.error as e:
        #     print(f"Error al desempaquetar: {e}")
        #     print(f"Datos recibidos: {data}, longitud: {len(data)}")
        #     return None

class Sequential:
    def __init__(self, filename):
        self.filename = filename
        self.aux_filename = "aux.bin"
        self.HEADER_SIZE = 5  

        if not os.path.exists(self.filename):
            with open(self.filename, 'wb') as f:
                f.write(struct.pack("i?", -1, False)) 

        self.RECORD_SIZE = struct.calcsize('i30sif10si??')
        print(f"Tamaño de registro calculado: {self.RECORD_SIZE} bytes")

    def write_start(self, start_pos, aux):
        with open(self.filename, 'r+b') as f:
            f.write(struct.pack("i?", start_pos, aux))

    def get_start(self):
        with open(self.filename, 'rb') as f:
            data = f.read(5)
            if len(data) < 5:
                return -1, False
            return struct.unpack("i?", data)

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

    def write_record_end(self, aux, record):
        filename = self.aux_filename if aux else self.filename
        with open(filename, "ab") as f:
            pos = (f.tell() - (5 if not aux else 0)) // self.RECORD_SIZE
            f.write(record.to_binary())
            return pos

    def write_record_at(self, record, pos, aux):
        filename = self.aux_filename if aux else self.filename
        with open(filename, "r+b") as f:
            offset = 5 + pos * self.RECORD_SIZE if not aux else pos * self.RECORD_SIZE
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
        start_pos, start_aux = self.get_start()
        print(f"Encabezado (start position): {start_pos}{'a' if start_aux else 'd'}")

        with open(self.filename, "rb") as f:
            f.seek(5) 
            pos = 0
            while True:
                data = f.read(self.RECORD_SIZE)
                if not data or len(data) < self.RECORD_SIZE:
                    break
                record = Record.from_binary(data)
                if record:
                    next_ptr = f"{record.next}{'a' if record.aux else 'd'}" if record.next != -1 else "-1"
                    deleted_flag = "[DELETED] " if record.deleted else ""
                    print(f"Pos {pos}d: {deleted_flag}{record.id} | {record.name} | {record.cant} | {record.price} | {record.date} | next: {next_ptr}")
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
                        next_ptr = f"{record.next}{'a' if record.aux else 'd'}" if record.next != -1 else "-1"
                        deleted_flag = "[DELETED] " if record.deleted else ""
                        print(f"Pos {pos}a: {deleted_flag}{record.id} | {record.name} | {record.cant} | {record.price} | {record.date} | next: {next_ptr}")
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
        start_pos, start_aux = self.get_start()

        # Case 1: Insert at beginning (new smallest key)
        if pos == -1:
            prev = self.get_record_at(start_aux, start_pos)
            if prev.next == -1:
                new_pos = self.write_record_end(True, record)
                record.next = start_pos
                record.aux = start_aux
                # Update the record in AUX file with proper links
                self.write_record_at(record, new_pos, True)
                # Update header to point to new record in AUX file
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
                    record.next = start_pos
                    record.aux = start_aux
                    # Update the record in AUX file with proper links
                    self.write_record_at(record, new_pos, True)
                    # Update header to point to new record in AUX file
                    self.write_start(new_pos, True)
                else:
                    record.next, record.aux = prev.next, prev.aux
                    new_pos = self.write_record_end(True, record)
                    prev.next, prev.aux = new_pos, True

                self.write_record_at(prev, prev_pos, prev_aux)
            return

        # Get the record at found position
        current = self.get_record_at(False, pos)
        if current is None:
            return

        # Case 2: Insert at end of list
        if current.next == -1:
            if record.key() > current.key():
                new_pos = self.write_record_end(False, record)
                current.next = new_pos
                current.aux = False
                self.write_record_at(current, pos, False)
            return

        # Case 3: Insert in middle of list
        next_record = self.get_record_at(current.aux, current.next)
        if next_record and record.key() > current.key() and record.key() < next_record.key():
            # Insert between current and next (in AUX file)
            record.next = current.next
            record.aux = current.aux
            new_pos = self.write_record_end(True, record)
            current.next = new_pos
            current.aux = True
            self.write_record_at(current, pos, False)
        else:
            # Need to find correct position in chain
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

            # Insert between prev_record and next_record (in AUX file)
            record.next = prev_record.next
            record.aux = prev_record.aux
            new_pos = self.write_record_end(True, record)
            prev_record.next = new_pos
            prev_record.aux = True
            self.write_record_at(prev_record, prev_pos, prev_aux)

        n = self.get_end(False)
        if new_pos > math.log(n):
            self.rebuild()

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
            
    def rebuild(self):
        print("\nIniciando proceso de reconstrucción...")

        ordered_records = []
        pos, aux = self.get_start()

        while pos != -1:
            record = self.get_record_at(aux, pos)
            if record is None:
                break
            if not record.deleted:
                ordered_records.append(record)
            pos = record.next
            aux = record.aux

        temp_main = "temp_main.bin"
        temp_aux = "temp_aux.bin"

        # Write records to new main file
        with open(temp_main, 'wb') as f_main:
            # Write header (will be updated later)
            f_main.write(struct.pack("i?", 0, False))

            # Write records sequentially
            for i, record in enumerate(ordered_records):
                record.next = i+1
                if record.next == len(ordered_records):
                    record.next = -1
                record.aux = False
                f_main.write(record.to_binary())

        # Clear auxiliary file
        open(temp_aux, 'wb').close()
        os.replace(temp_main, self.filename)
        os.replace(temp_aux, self.aux_filename)

    def search(self, key):
        pos = self.binary_search(key)
        if pos == -1:
            pos = self.get_start()
            if pos == -1:
                return None
            record = self.get_record_at(pos[1], pos[0])
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

        left_pos = self.binary_search(mini)
        left = self.get_record_at(False, left_pos)

        while left.is_smaller(maxi):
            if left.id >= mini:
                results.append(left)
            left = self.get_record_at(left.aux, left.next)

        return results

    def delete(self, key):
        start_pos, start_aux = self.get_start()
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

                if prev_pos == -1: 
                    self.write_start(record.next, record.aux)
                else:
                    prev_record = self.get_record_at(prev_aux, prev_pos)
                    if prev_record:
                        prev_record.next = record.next
                        prev_record.aux = record.aux
                        self.write_record_at(prev_record, prev_pos, prev_aux)
                return True

            prev_pos = current_pos
            prev_aux = current_aux
            current_pos = record.next
            current_aux = record.aux

        return False

def medir_tiempos_por_cantidad(se, rows, cantidades):
    tiempos_insert = []
    tiempos_busqueda = []
    tiempos_rango = []
    tiempos_delete = []

    for n in cantidades:
        sample = rows[:n]

        if os.path.exists("sequential.dat"):
            os.remove("sequential.dat")
        se = Sequential("sequential.dat")

        t1 = time.time()
        for row in sample:
            id = int(row[0])
            nombre = row[1]
            cantidad = int(row[2])
            precio = float(row[3])
            fecha = row[4]
            se.insert(Record(id, nombre, cantidad, precio, fecha))
        t2 = time.time()
        tiempos_insert.append(t2 - t1)

        t1 = time.time()
        for i in range(1, n + 1, max(1, n // 10)):
            se.search(i)
        t2 = time.time()
        tiempos_busqueda.append(t2 - t1)

        t1 = time.time()
        se.search_range(1, n)
        t2 = time.time()
        tiempos_rango.append(t2 - t1)

        t1 = time.time()
        for i in range(1, n + 1, max(1, n // 10)):
            se.delete(i)
        t2 = time.time()
        tiempos_delete.append(t2 - t1)

    return tiempos_insert, tiempos_busqueda, tiempos_rango, tiempos_delete

def graficar_lineal(cantidades, tiempos, titulo, nombre_archivo):
    plt.figure(figsize=(10, 6))
    plt.plot(cantidades, tiempos, marker='o', linestyle='-', linewidth=2.5, color='#5F9EA0', label=titulo)
    for i, tiempo in enumerate(tiempos):
        plt.text(cantidades[i], tiempo, f"{tiempo:.4f}s", ha='center', va='bottom', fontsize=9)
    plt.title(f"{titulo} vs Cantidad de registros", fontsize=14)
    plt.xlabel("Cantidad de registros")
    plt.ylabel("Tiempo (segundos)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig(nombre_archivo)
    plt.show()

"""def main():
    cantidades = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    with open("sales_dataset_random.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        rows = list(reader)

    se = Sequential("sequential.dat")
    tiempos_insert, tiempos_busqueda, tiempos_rango, tiempos_delete = medir_tiempos_por_cantidad(se, rows, cantidades)

    graficar_lineal(cantidades, tiempos_insert, "Tiempo de Inserción", "sequential_insercion.png")
    graficar_lineal(cantidades, tiempos_busqueda, "Tiempo de Búsqueda", "sequential_busqueda.png")
    graficar_lineal(cantidades, tiempos_rango, "Tiempo de Búsqueda por Rango", "sequential_rango.png")
    graficar_lineal(cantidades, tiempos_delete, "Tiempo de Eliminación", "sequential_eliminacion.png")
"""


def main():
    for fname in ["data.dat", "aux.bin"]:
        if os.path.exists(fname):
            os.remove(fname)

    file = Sequential("data.dat")

    with open("sales_dataset_random.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            id = int(row[0])
            nombre = row[1]
            cantidad = int(row[2])
            precio = float(row[3])
            fecha = row[4]
            file.insert(Record(id, nombre, cantidad, precio, fecha))

    print("\nResultado final:")
    file.print_all()

    print("\nSEARCH:")
    print(file.search(8))
    print(file.search(2))

    print("\nsearch rango:")
    res = file.search_range(5,10)
    for rec in res:
        print(rec)

    print("\neliminar:")
    file.delete(1)
    file.delete(20)
    file.delete(6)
    file.print_all()

if __name__ == "__main__":
    main()