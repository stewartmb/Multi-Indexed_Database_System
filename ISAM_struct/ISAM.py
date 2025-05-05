import bisect
import os
import pickle
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class Record:
    key: int
    data: Any

class PageFile:
    def __init__(self, page_size=4):
        self.pages: List[List[Record]] = []
        self.page_size = page_size
    
    def add_page(self, records: List[Record]):
        """Añade una página de registros al PageFile"""
        self.pages.append(records.copy())
    
    def find_in_page(self, page_num: int, key: int) -> Optional[Record]:
        """Busca un registro en una página específica"""
        if page_num >= len(self.pages):
            return None
            
        page = self.pages[page_num]
        # Búsqueda binaria en la página ordenada
        idx = bisect.bisect_left([r.key for r in page], key)
        if idx < len(page) and page[idx].key == key:
            return page[idx]
        return None
    
    def get_page(self, page_num: int) -> List[Record]:
        """Obtiene todos los registros de una página"""
        if page_num < len(self.pages):
            return self.pages[page_num]
        return []

class OverflowFile:
    def __init__(self):
        self.overflow_records: Dict[int, Record] = {}  # key: Record
    
    def insert(self, record: Record):
        """Añade un registro al overflow"""
        self.overflow_records[record.key] = record
    
    def search(self, key: int) -> Optional[Record]:
        """Busca un registro en el overflow"""
        return self.overflow_records.get(key, None)
    
    def remove(self, key: int) -> bool:
        """Elimina un registro del overflow"""
        if key in self.overflow_records:
            del self.overflow_records[key]
            return True
        return False

class SecondLevelIndex:
    def __init__(self):
        self.keys: List[int] = []  # Claves ordenadas
        self.page_numbers: List[int] = []  # Números de página correspondientes
    
    def add_entry(self, key: int, page_num: int):
        """Añade una entrada al índice de segundo nivel"""
        # Mantener las claves ordenadas
        idx = bisect.bisect_left(self.keys, key)
        self.keys.insert(idx, key)
        self.page_numbers.insert(idx, page_num)
    
    def find_page(self, key: int) -> int:
        """Encuentra el número de página para una clave dada"""
        idx = bisect.bisect_right(self.keys, key) - 1
        if idx >= 0:
            return self.page_numbers[idx]
        return 0  # Si la clave es menor que todas, va a la primera página

class IndexPage:
    def __init__(self):
        self.keys: List[int] = []  # Claves ordenadas
        self.second_level_indices: List[SecondLevelIndex] = []  # Índices de segundo nivel
    
    def initialize(self, page_file: PageFile, sparse_factor: int = 2):
        """Inicializa el índice estático de dos niveles basado en el PageFile"""
        # Nivel 1: Sparse index para las páginas del segundo nivel
        for page_num, page in enumerate(page_file.pages):
            if page_num % sparse_factor == 0 and page:
                # Añadir clave al primer nivel
                first_key = page[0].key
                idx = bisect.bisect_left(self.keys, first_key)
                self.keys.insert(idx, first_key)
                
                # Crear nuevo índice de segundo nivel
                sl_index = SecondLevelIndex()
                self.second_level_indices.insert(idx, sl_index)
            
            # Añadir entradas al índice de segundo nivel correspondiente
            if page:
                current_sl_index = self.second_level_indices[-1]
                current_sl_index.add_entry(page[0].key, page_num)
    
    def find_second_level_index(self, key: int) -> SecondLevelIndex:
        """Encuentra el índice de segundo nivel apropiado para una clave"""
        idx = bisect.bisect_right(self.keys, key) - 1
        if idx >= 0:
            return self.second_level_indices[idx]
        return self.second_level_indices[0]  # Si la clave es menor que todas

class ISAM:
    def __init__(self, page_size=4, sparse_factor=2):
        self.index_page = IndexPage()
        self.page_file = PageFile(page_size)
        self.overflow_file = OverflowFile()
        self.sparse_factor = sparse_factor
    
    def initialize_index(self):
        """Inicializa el índice estático de dos niveles"""
        self.index_page.initialize(self.page_file, self.sparse_factor)
    
    def insert(self, record: Record, initial_load=False):
        """Inserta un registro en la estructura ISAM"""
        if initial_load:
            # Durante la carga inicial, simplemente añadimos a las páginas
            if not self.page_file.pages or len(self.page_file.pages[-1]) >= self.page_file.page_size:
                self.page_file.add_page([])
            self.page_file.pages[-1].append(record)
            self.page_file.pages[-1].sort(key=lambda x: x.key)
        else:
            # Después de la inicialización, usar el índice para encontrar la página correcta
            sl_index = self.index_page.find_second_level_index(record.key)
            page_num = sl_index.find_page(record.key)
            
            # Intentar insertar en la página correspondiente
            page = self.page_file.get_page(page_num)
            if len(page) < self.page_file.page_size:
                # Hay espacio en la página
                bisect.insort(page, record, key=lambda x: x.key)
                self.page_file.pages[page_num] = page
            else:
                # No hay espacio, ir al overflow
                self.overflow_file.insert(record)
    
    def search(self, key: int) -> Optional[Record]:
        """Busca un registro por su clave"""
        # Primero buscar en el índice
        sl_index = self.index_page.find_second_level_index(key)
        page_num = sl_index.find_page(key)
        
        # Buscar en la página correspondiente
        record = self.page_file.find_in_page(page_num, key)
        if record:
            return record
        
        # Si no se encuentra en la página principal, buscar en overflow
        return self.overflow_file.search(key)
    
    def save_to_disk(self, filename: str):
        """Guarda la estructura ISAM en disco"""
        data = {
            'index_page': self.index_page,
            'page_file': self.page_file,
            'overflow_file': self.overflow_file,
            'sparse_factor': self.sparse_factor
        }
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
    
    @classmethod
    def load_from_disk(cls, filename: str) -> 'ISAM':
        """Carga la estructura ISAM desde disco"""
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        
        isam = cls(page_size=data['page_file'].page_size, 
                  sparse_factor=data['sparse_factor'])
        isam.index_page = data['index_page']
        isam.page_file = data['page_file']
        isam.overflow_file = data['overflow_file']
        return isam
    
    def print_structure(self):
        """Muestra la estructura actual de ISAM"""
        print("=== ISAM Structure ===")
        print("\nIndex Page (Level 1):")
        for i, key in enumerate(self.index_page.keys):
            print(f"Key: {key} -> SL Index {i}")
        
        print("\nSecond Level Indices:")
        for i, sl_index in enumerate(self.index_page.second_level_indices):
            print(f"SL Index {i}:")
            for j in range(len(sl_index.keys)):
                print(f"  Key: {sl_index.keys[j]} -> Page {sl_index.page_numbers[j]}")
        
        print("\nPage File:")
        for i, page in enumerate(self.page_file.pages):
            print(f"Page {i}: {[r.key for r in page]}")
        
        print("\nOverflow File:")
        print([key for key in self.overflow_file.overflow_records.keys()])

    

    # Crear e inicializar ISAM
isam = ISAM(page_size=3, sparse_factor=2)

# Carga inicial de datos (antes de inicializar el índice)
records = [
    Record(5, "Data5"), Record(10, "Data10"), Record(15, "Data15"),
    Record(20, "Data20"), Record(25, "Data25"), Record(30, "Data30"),
    Record(35, "Data35"), Record(40, "Data40"), Record(45, "Data45")
]

for record in records:
    isam.insert(record, initial_load=True)

# Inicializar el índice estático
isam.initialize_index()

# Operaciones después de la inicialización
isam.insert(Record(12, "Data12"))  # Irá al overflow si no cabe
isam.insert(Record(22, "Data22"))  # Irá al overflow si no cabe

# Buscar registros
print(isam.search(10))  # Debería estar en PageFile
print(isam.search(12))  # Debería estar en OverflowFile

# Mostrar estructura
isam.print_structure()

# Guardar y cargar desde disco
isam.save_to_disk("isam_data.bin")
loaded_isam = ISAM.load_from_disk("isam_data.bin")