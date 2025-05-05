import struct
import os
import bisect
from collections import deque

# Constantes
TAM_ENCABEZADO = 4  # Tamaño del encabezado en bytes (número de páginas)
TAM_PAGINA = 4096    # Tamaño fijo de cada página (4KB)
TAM_REGISTRO = 25    # Tamaño de cada registro (3s codigo + 20s nombre + 2s ciclo)
REGISTROS_POR_PAGINA = TAM_PAGINA // TAM_REGISTRO  # Registros por página primaria

# Formatos
RECORD_FORMAT = '3s20s2s'  # codigo (3), nombre (20), ciclo (2)
INDEX_FORMAT = '3si'       # clave (3), puntero (4)

# =============================================
# Clases independientes
# =============================================

class Registro:
    def __init__(self, codigo, nombre, ciclo):
        self.codigo = codigo
        self.nombre = nombre
        self.ciclo = ciclo
    
    def to_bytes(self):
        return struct.pack(RECORD_FORMAT, 
                         self.codigo.encode('utf-8').ljust(3, b'\x00'),
                         self.nombre.encode('utf-8').ljust(20, b'\x00'),
                         self.ciclo.zfill(2).encode('utf-8'))
    
    @classmethod
    def from_bytes(cls, data):
        unpacked = struct.unpack(RECORD_FORMAT, data)
        return cls(
            unpacked[0].decode('utf-8').strip('\x00'),
            unpacked[1].decode('utf-8').strip('\x00'),
            unpacked[2].decode('utf-8').strip('\x00')
        )
    
    def __lt__(self, other):
        return self.codigo < other.codigo
    
    def __eq__(self, other):
        return self.codigo == other.codigo
    
    def __str__(self):
        return f"Código: {self.codigo}, Nombre: {self.nombre}, Ciclo: {self.ciclo}"

class PageFile:
    """Representa una página del archivo primario"""
    def __init__(self):
        self.records = [None] * REGISTROS_POR_PAGINA
        self.record_count = 0
        self.next_overflow = -1  # Puntero a página de overflow
    
    def add_record_sorted(self, record):
        """Añade un registro manteniendo el orden"""
        if self.record_count >= REGISTROS_POR_PAGINA:
            return False
            
        # Encontrar posición para mantener ordenado
        pos = bisect.bisect_left([r.codigo if r else '' for r in self.records[:self.record_count]], record.codigo)
        
        # Desplazar registros a la derecha
        for i in range(self.record_count, pos, -1):
            self.records[i] = self.records[i-1]
        
        # Insertar nuevo registro
        self.records[pos] = record
        self.record_count += 1
        return True
    
    def to_bytes(self):
        """Convierte la página a bytes"""
        data = bytearray()
        for record in self.records:
            if record:
                data.extend(record.to_bytes())
            else:
                data.extend(b'\x00' * TAM_REGISTRO)
        data.extend(struct.pack('i', self.next_overflow))
        return bytes(data)
    
    @classmethod
    def from_bytes(cls, data):
        """Reconstruye una página desde bytes"""
        page = cls()
        for i in range(REGISTROS_POR_PAGINA):
            start = i * TAM_REGISTRO
            record_data = data[start:start+TAM_REGISTRO]
            if record_data != b'\x00' * TAM_REGISTRO:
                page.records[i] = Registro.from_bytes(record_data)
                page.record_count += 1
        page.next_overflow = struct.unpack('i', data[-4:])[0]
        return page

class IndexPage:
    """Representa una página del índice (para ambos niveles)"""
    def __init__(self, is_leaf=False):
        self.keys = []       # Lista de claves (códigos)
        self.pointers = []   # Lista de punteros
        self.is_leaf = is_leaf
    
    def add_entry_sorted(self, key, pointer):
        """Añade una entrada manteniendo el orden"""
        # Encontrar posición para mantener ordenado
        pos = bisect.bisect_left(self.keys, key)
        
        # Insertar en las listas
        self.keys.insert(pos, key)
        self.pointers.insert(pos, pointer)
    
    def to_bytes(self):
        """Convierte la página de índice a bytes"""
        data = bytearray()
        data.append(self.is_leaf)
        for key, ptr in zip(self.keys, self.pointers):
            data.extend(struct.pack(INDEX_FORMAT, key.encode('utf-8'), ptr))
        # Rellenar con ceros el resto de la página
        remaining_space = TAM_PAGINA - (1 + len(self.keys) * struct.calcsize(INDEX_FORMAT))
        data.extend(b'\x00' * remaining_space)
        return bytes(data)
    
    @classmethod
    def from_bytes(cls, data):
        """Reconstruye una página de índice desde bytes"""
        page = cls()
        page.is_leaf = bool(data[0])
        offset = 1
        entry_size = struct.calcsize(INDEX_FORMAT)
        while offset + entry_size <= TAM_PAGINA:
            key, ptr = struct.unpack(INDEX_FORMAT, data[offset:offset+entry_size])
            if key == b'\x00' * 3:  # Fin de entradas válidas
                break
            page.keys.append(key.decode('utf-8').strip('\x00'))
            page.pointers.append(ptr)
            offset += entry_size
        return page

# =============================================
# Clase ISAM principal
# =============================================

class ISAM:
    def __init__(self, data_file='data_file.bin', index_file='index_file.bin', overflow_file='overflow_file.bin'):
        self.data_file = data_file
        self.index_file = index_file
        self.overflow_file = overflow_file
        self._initialize_files()

    # --------------------------
    # Métodos de inicialización
    # --------------------------
    
    def _initialize_files(self):
        """Inicializa los archivos necesarios con sus encabezados"""
        # Archivo de datos primario
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'wb') as f:
                f.write(struct.pack('i', 0))  # Número de páginas primarias
        
        # Archivo de índice (dos niveles)
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'wb') as f:
                # Encabezado: num_paginas_indice, ptr_nivel1, ptr_nivel2
                f.write(struct.pack('iii', 0, -1, -1))
        
        # Archivo de overflow
        if not os.path.exists(self.overflow_file):
            with open(self.overflow_file, 'wb') as f:
                f.write(struct.pack('i', 0))  # Contador de registros overflow

    # --------------------------
    # Operaciones principales
    # --------------------------
    
    def insert_record(self, registro):
        """Inserta un objeto Registro en la estructura ISAM"""
        if not isinstance(registro, Registro):
            raise ValueError("Debe proporcionar un objeto de tipo Registro")
        
        # 1. Insertar en archivo primario o overflow
        primary_pages = self._read_primary_header()
        inserted = False
        
        # Caso especial: primera página
        if primary_pages == 0:
            new_page = PageFile()
            new_page.add_record_sorted(registro)
            self._add_primary_page(new_page)
            self._update_index(registro.codigo)
            return
        
        # Buscar página primaria adecuada
        for page_num in range(primary_pages):
            page = self._read_primary_page(page_num)
            last_key = page.records[page.record_count-1].codigo if page.record_count > 0 else ''
            
            # Si el código es menor que el último de la página o es la última página
            if not last_key or registro.codigo <= last_key or page_num == primary_pages-1:
                if page.record_count < REGISTROS_POR_PAGINA:
                    # Insertar en página primaria manteniendo orden
                    if page.add_record_sorted(registro):
                        self._write_primary_page(page_num, page)
                        inserted = True
                        break
                else:
                    # Insertar en overflow
                    self._insert_overflow(page, page_num, registro)
                    inserted = True
                    break
        
        if not inserted:
            # Crear nueva página primaria
            new_page = PageFile()
            new_page.add_record_sorted(registro)
            self._add_primary_page(new_page)
        
        # 2. Actualizar índices si es necesario (sparse index)
        self._update_index(registro.codigo)
    
    def search_record(self, codigo):
        """Busca un registro por su código y devuelve objeto Registro"""
        # 1. Buscar en el índice de nivel 1
        l1_page, l2_page = self._read_index_headers()
        
        # Si no hay índices, búsqueda secuencial
        if l1_page == -1:
            return self._sequential_search(codigo)
        
        # Buscar en nivel 1
        l1 = self._read_index_page(l1_page)
        page_ptr = self._binary_search_index(l1, codigo)
        
        # Si tenemos nivel 2, buscar allí
        if l2_page != -1:
            l2 = self._read_index_page(l2_page)
            page_ptr = self._binary_search_index(l2, codigo)
        
        # Buscar en la página de datos
        if page_ptr != -1:
            page = self._read_primary_page(page_ptr)
            # Búsqueda binaria en la página
            idx = bisect.bisect_left([r.codigo if r else '' for r in page.records[:page.record_count]], codigo)
            if idx < page.record_count and page.records[idx] and page.records[idx].codigo == codigo:
                return page.records[idx]
            
            # Buscar en overflow si no se encontró
            return self._search_overflow(page, codigo)
        
        return None

    # --------------------------
    # Métodos auxiliares
    # --------------------------
    
    def _binary_search_index(self, index_page, key):
        """Búsqueda binaria en una página de índice"""
        idx = bisect.bisect_left(index_page.keys, key)
        
        if idx == 0:
            return index_page.pointers[0]
        elif idx < len(index_page.keys):
            return index_page.pointers[idx-1]
        else:
            return index_page.pointers[-1]
    
    def _update_index(self, new_key):
        """Actualiza los índices sparse cuando sea necesario"""
        l1_page, l2_page = self._read_index_headers()
        primary_pages = self._read_primary_header()
        
        # Regla: crear/actualizar índices cada √n páginas primarias
        sqrt_pages = int(primary_pages ** 0.5)
        
        if sqrt_pages > 0 and primary_pages % sqrt_pages == 0:
            if l1_page == -1:
                # Crear primer nivel de índice
                self._create_first_level_index()
            elif l2_page == -1 and primary_pages >= sqrt_pages * sqrt_pages:
                # Crear segundo nivel de índice
                self._create_second_level_index()
            else:
                # Actualizar índices existentes
                self._rebuild_indices()
    
    def _create_first_level_index(self):
        """Crea el primer nivel de índice sparse"""
        primary_pages = self._read_primary_header()
        index_page = IndexPage(is_leaf=True)
        
        # Tomar el primer registro de cada página √n
        step = max(1, int(primary_pages ** 0.5))
        for page_num in range(0, primary_pages, step):
            page = self._read_primary_page(page_num)
            if page.records[0]:
                index_page.add_entry_sorted(page.records[0].codigo, page_num)
        
        # Guardar el índice
        index_page_num = self._add_index_page(index_page)
        self._write_index_headers(index_page_num, -1)
    
    def _create_second_level_index(self):
        """Crea el segundo nivel de índice sparse"""
        count, l1_page, _ = self._read_index_header()
        l1 = self._read_index_page(l1_page)
        
        # Tomar cada √n claves del nivel 1
        step = max(1, int(len(l1.keys) ** 0.5))
        index_page = IndexPage(is_leaf=False)
        
        for i in range(0, len(l1.keys), step):
            index_page.add_entry_sorted(l1.keys[i], l1_page)
        
        # Guardar el índice de nivel 2
        index_page_num = self._add_index_page(index_page)
        self._write_index_headers(l1_page, index_page_num)
    
    def _rebuild_indices(self):
        """Reconstruye ambos niveles de índices"""
        primary_pages = self._read_primary_header()
        sqrt_pages = int(primary_pages ** 0.5)
        
        # Reconstruir nivel 1
        count, l1_page, l2_page = self._read_index_header()
        l1 = IndexPage(is_leaf=True)
        
        for page_num in range(0, primary_pages, sqrt_pages):
            page = self._read_primary_page(page_num)
            if page.records[0]:
                l1.add_entry_sorted(page.records[0].codigo, page_num)
        
        self._write_index_page(l1_page, l1)
        
        # Reconstruir nivel 2 si existe
        if l2_page != -1:
            l2 = IndexPage(is_leaf=False)
            step = max(1, int(len(l1.keys) ** 0.5))
            
            for i in range(0, len(l1.keys), step):
                l2.add_entry_sorted(l1.keys[i], l1_page)
            
            self._write_index_page(l2_page, l2)
    
    def _insert_overflow(self, page, page_num, record):
        """Inserta un registro en el área de overflow"""
        overflow_count = self._read_overflow_header()
        
        # Escribir el registro en overflow
        with open(self.overflow_file, 'ab') as f:
            f.seek(TAM_ENCABEZADO + overflow_count * TAM_REGISTRO)
            f.write(record.to_bytes())
        
        # Actualizar contador
        self._write_overflow_header(overflow_count + 1)
        
        # Actualizar puntero en página primaria si es el primer overflow
        if page.next_overflow == -1:
            page.next_overflow = overflow_count
            self._write_primary_page(page_num, page)
    
    def _search_overflow(self, page, codigo):
        """Busca un registro en el área de overflow"""
        if page.next_overflow == -1:
            return None
        
        overflow_count = self._read_overflow_header()
        
        with open(self.overflow_file, 'rb') as f:
            f.seek(TAM_ENCABEZADO)
            for _ in range(overflow_count):
                record_data = f.read(TAM_REGISTRO)
                record = Registro.from_bytes(record_data)
                if record.codigo == codigo:
                    return record
        
        return None
    
    def _sequential_search(self, codigo):
        """Búsqueda secuencial en archivo primario y overflow"""
        primary_pages = self._read_primary_header()
        
        for page_num in range(primary_pages):
            page = self._read_primary_page(page_num)
            for record in page.records[:page.record_count]:
                if record and record.codigo == codigo:
                    return record
            
            # Buscar en overflow
            result = self._search_overflow(page, codigo)
            if result:
                return result
        
        return None

    # --------------------------
    # Operaciones de archivo
    # --------------------------
    
    def _read_primary_header(self):
        """Lee el encabezado del archivo primario"""
        with open(self.data_file, 'rb') as f:
            return struct.unpack('i', f.read(TAM_ENCABEZADO))[0]
    
    def _write_primary_header(self, count):
        """Escribe el encabezado del archivo primario"""
        with open(self.data_file, 'r+b') as f:
            f.write(struct.pack('i', count))
    
    def _read_primary_page(self, page_num):
        """Lee una página del archivo primario"""
        with open(self.data_file, 'rb') as f:
            f.seek(TAM_ENCABEZADO + page_num * TAM_PAGINA)
            data = f.read(TAM_PAGINA)
            return PageFile.from_bytes(data)
    
    def _write_primary_page(self, page_num, page):
        """Escribe una página del archivo primario"""
        with open(self.data_file, 'r+b') as f:
            f.seek(TAM_ENCABEZADO + page_num * TAM_PAGINA)
            f.write(page.to_bytes())
    
    def _add_primary_page(self, page):
        """Añade una nueva página al archivo primario"""
        page_count = self._read_primary_header()
        with open(self.data_file, 'r+b') as f:
            f.seek(TAM_ENCABEZADO + page_count * TAM_PAGINA)
            f.write(page.to_bytes())
        self._write_primary_header(page_count + 1)
    
    def _read_index_header(self):
        """Lee el encabezado completo del archivo de índice"""
        with open(self.index_file, 'rb') as f:
            data = f.read(3 * TAM_ENCABEZADO)
            return struct.unpack('iii', data)  # (count, l1_ptr, l2_ptr)
    
    def _read_index_headers(self):
        """Lee los punteros a los niveles de índice"""
        header = self._read_index_header()
        return header[1], header[2]  # (l1_ptr, l2_ptr)
    
    def _write_index_headers(self, l1_ptr, l2_ptr):
        """Escribe los punteros a los niveles de índice"""
        count = self._read_index_header()[0]
        with open(self.index_file, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack('iii', count, l1_ptr, l2_ptr))
    
    def _read_index_page(self, page_num):
        """Lee una página de índice"""
        with open(self.index_file, 'rb') as f:
            f.seek(3 * TAM_ENCABEZADO + page_num * TAM_PAGINA)
            data = f.read(TAM_PAGINA)
            return IndexPage.from_bytes(data)
    
    def _write_index_page(self, page_num, page):
        """Escribe una página de índice"""
        with open(self.index_file, 'r+b') as f:
            f.seek(3 * TAM_ENCABEZADO + page_num * TAM_PAGINA)
            f.write(page.to_bytes())
    
    def _add_index_page(self, page):
        """Añade una nueva página de índice"""
        count = self._read_index_header()[0]
        with open(self.index_file, 'r+b') as f:
            f.seek(3 * TAM_ENCABEZADO + count * TAM_PAGINA)
            f.write(page.to_bytes())
        
        # Actualizar contador
        with open(self.index_file, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack('i', count + 1))
        
        return count
    
    def _read_overflow_header(self):
        """Lee el encabezado del archivo de overflow"""
        with open(self.overflow_file, 'rb') as f:
            return struct.unpack('i', f.read(TAM_ENCABEZADO))[0]
    
    def _write_overflow_header(self, count):
        """Escribe el encabezado del archivo de overflow"""
        with open(self.overflow_file, 'r+b') as f:
            f.write(struct.pack('i', count))
    
    # --------------------------
    # Métodos de visualización
    # --------------------------
    
    def print_structure(self):
        """Muestra la estructura completa del ISAM"""
        print("\n=== Estructura ISAM ===")
        
        # Mostrar índices
        l1_page, l2_page = self._read_index_headers()
        
        if l2_page != -1:
            print("\nNivel 2 (Índice Sparse):")
            l2 = self._read_index_page(l2_page)
            print(f"Claves: {l2.keys}")
            print(f"Punteros: {l2.pointers}")
        
        if l1_page != -1:
            print("\nNivel 1 (Índice Sparse):")
            l1 = self._read_index_page(l1_page)
            print(f"Claves: {l1.keys}")
            print(f"Punteros: {l1.pointers}")
        
        # Mostrar datos primarios
        primary_pages = self._read_primary_header()
        print(f"\nDatos Primarios ({primary_pages} páginas):")
        for i in range(primary_pages):
            page = self._read_primary_page(i)
            print(f"\nPágina {i}:")
            print(f"Registros: {[r.codigo for r in page.records[:page.record_count]]}")
            print(f"Overflow: {page.next_overflow}")
        
        # Mostrar overflow
        overflow_count = self._read_overflow_header()
        print(f"\nOverflow ({overflow_count} registros)")