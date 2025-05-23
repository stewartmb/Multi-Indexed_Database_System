import math
import heapq
import struct
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *
from Heap_struct.Heap import *

point_format = ""
mbr_format = ""
rect_format = ""
header_format = "iiiii255s255s255s"
header_size = struct.calcsize(header_format)
b=32
m = 2
dim=2
tipo="i"

class RTreeFile: 
    """
    Clase que maneja el archivo del índice del RTree

    Atributos
    ---------------
        data_filename: str
            path al archivo con la data
        index_filename: str
            path al archivo de índices
        RT: RegistroType
            objeto de RegistroType
    """
    class Point:
        """
        Clase para manejar cada punto del RTree
        
        Atributos
        ---------------
            coords: list
                mantiene las coordenadas del punto
            placeholder: bool
                0 si el valor del punto sirve, 1 si solo es para tener la estructura
            index: int
                posicion del registro que tiene ese punto como key en el data file

        """
        def __init__(self, coords: list = None, placeholder: bool = False, index: int = -1):
            """
            Inicializa un punto

            Parametros
            ---------------
            coords: list
                mantiene las coordenadas del punto
            placeholder: bool
                0 si el valor del punto sirve, 
                1 si solo es para tener la estructura
            index: int
                posicion del registro que tiene 
                ese punto como key en el data file
            """
            if coords is None:
                coords = []
                for i in range(dim):
                    coords.append(i)
            self.coords = coords
            self.placeholder = placeholder
            self.index = index

        def to_binary(self) -> bytes:
            """
            Convierte un punto a binario
            """
            global point_format
            return struct.pack(point_format, *self.coords, self.placeholder, self.index)

        def __hash__(self):
            return hash(tuple(self.coords))
    
        @staticmethod
        def from_binary(binary: bytes):
            """
            Lee bytes y lo convierte en un punto

            Parametros
            ---------------
                binary: str
                    texto en binario
            
            Retorna
            ---------------
                Point()
            """
            global point_format
            data = struct.unpack(point_format, binary)
            coords = list(data[:dim])
            placeholder = data[dim]
            index = data[dim + 1]
            return RTreeFile.Point(coords=coords, placeholder=placeholder, index=index)

        @staticmethod
        def sort_points_by_dimension(points: list) -> list:
            """
            Ordena los puntos por cada dimension

            Parametros
            ---------------
                points: list
                    lista de puntos a ordenar
            
            Retorna
            ---------------
                list
                    lista de puntos ordenados
            """
            num_dims = len(points[0].coords)
            sorted_by_dim = []
            for i in range(num_dims):
                sorted_dim = sorted(points, key=lambda p: p.coords[i])
                sorted_by_dim.append(sorted_dim)
            return sorted_by_dim

        def inside(self, min_coords, max_coords):
            """
            Verifica si el punto se encuentra dentro del rango dado
            """
            return all(
                min_coords[i] <= self.coords[i] <= max_coords[i]
                for i in range(len(self.coords))
            )

        def __lt__(self, other):
            return self.coords < other.coords
        
        def __eq__(self, other):
            if len(self.coords) != len(other.coords):
                return False
            return all(math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-6) for a, b in zip(self.coords, other.coords))

        @staticmethod
        def distance(p1, p2):
            """
            Calcula la distancia entre dos puntos
            """
            return math.sqrt(
                sum((p1.coords[i] - p2.coords[i]) ** 2 for i in range(len(p1.coords)))
            )

        @staticmethod
        def mindist(q, mbr):
            """
            Calcula la distancia mínima entre un punto y un mbr
            """
            sum_sq = 0
            for i in range(len(q.coords)):
                qi = q.coords[i]
                li = mbr.min_coords[i]
                ui = mbr.max_coords[i]

                if qi < li:
                    ri = li
                elif qi > ui:
                    ri = ui
                else:
                    ri = qi

                sum_sq += (qi - ri) ** 2
            return math.sqrt(sum_sq)

        def __str__(self):
            ret_str = f"{self.index}: {self.coords}"
            return ret_str

    class MBR:
        """
        Clase que maneja los MBRs de cada rectangulo

        Atributos
        ---------------
            min_coords: list
                coordenadas mínimas del MBR
            max_coords: list
                coordenadas máximas del MBR
        """
        def __init__(self, min_coords, max_coords):
            self.min_coords = min_coords
            self.max_coords = max_coords

        def to_binary(self) -> bytes:
            """
            Convierte el MBR a bytes
            """
            global mbr_format
            return struct.pack(mbr_format, *self.min_coords, *self.max_coords)

        @staticmethod
        def from_binary(binary):
            """
            Lee bytes y retorna un MBR con ese contenido
            """
            global mbr_format
            coords = struct.unpack(mbr_format, binary)
            assert len(coords) % 2 == 0, "Invalid MBR binary format"
            min_coords = list(coords[: len(coords) // 2])
            max_coords = list(coords[len(coords) // 2 :])
            return RTreeFile.MBR(min_coords, max_coords)

        def __str__(self):
            return f"MBR: {self.min_coords}, {self.max_coords}"

        def perimeter(self):
            """
            Calcula el perimetro de un MBR
            """
            return 2 * sum(
                self.max_coords[i] - self.min_coords[i] for i in range(len(self.min_coords))
            )

        def update_coords_point(self, point):
            """
            Se actualiza el MBR para incluir el punto dado.
            Se retorna la diferencia de perímetros entre el MBR original y el MBR nuevo.
            """
            prev_perimeter = self.perimeter()
            for i in range(len(point.coords)):
                self.min_coords[i] = min(self.min_coords[i], point.coords[i])
                self.max_coords[i] = max(self.max_coords[i], point.coords[i])
            new_perimeter = self.perimeter()
            return new_perimeter - prev_perimeter

        def update_coords_rec(self, rec):
            """
            Se actualiza el MBR para incluir el rectangulo dado.
            Se retorna la diferencia de perímetros entre el MBR original y el MBR nuevo.
            """
            prev_perimeter = self.perimeter()
            for i in range(len(rec.mbr.min_coords)):
                self.min_coords[i] = min(self.min_coords[i], rec.mbr.min_coords[i])
                self.max_coords[i] = max(self.max_coords[i], rec.mbr.max_coords[i])
            new_perimeter = self.perimeter()
            return new_perimeter - prev_perimeter

        @staticmethod
        def calc_mbr(points):
            """
            Dado una lista de puntos, calcula el MBR que los contiene.
            """
            num_dims = len(points[0].coords)
            min_coords = points[0].coords[:]
            max_coords = points[0].coords[:]

            for p in points[1:]:
                for i in range(num_dims):
                    min_coords[i] = min(min_coords[i], p.coords[i])
                    max_coords[i] = max(max_coords[i], p.coords[i])

            return RTreeFile.MBR(min_coords, max_coords)

        @staticmethod
        def calc_mbr_rec(file, rectangles_pos):
            """
            Dado una lista de posiciones de rectángulos, calcula el MBR que los contiene.
            """
            rectangles = [file.get_rec_at(x) for x in rectangles_pos]
            num_dims = len(rectangles[0].mbr.min_coords)
            min_coords = rectangles[0].mbr.min_coords[:]
            max_coords = rectangles[0].mbr.max_coords[:]

            for rec in rectangles[1:]:
                for i in range(num_dims):
                    min_coords[i] = min(min_coords[i], rec.mbr.min_coords[i])
                    max_coords[i] = max(max_coords[i], rec.mbr.max_coords[i])

            return RTreeFile.MBR(min_coords, max_coords)

    class Rectangle:
        """
        Clase que maneja cada rectángulo que compone el RTree
        
        Atributos
        ---------------
            pos: int
                posicion del rectangulo en el archivo de índices
            rectangles: list
                lista con las posiciones de los rectangulos dentro del objeto
            points: list
                lista con los puntos dentro del objeto
            parent: int
                posicion del rectangulo padre del objeto
            is_leaf: bool
                indica si el rectangulo es hoja o no
            mbr: MBR
                el MBR del objeto
            deleted:
                indica si el objeto está eliminado o no
        """
        def __init__(
            self,
            file,
            pos=None,
            rectangles=None,
            points=None,
            parent=-1,
            is_leaf=True,
            mbr=None,
            deleted=False
        ):
            self.pos = pos  # int
            if points is None:
                points = []  # puntos de tamaño maximo b+1
            if rectangles is None:
                rectangles = []  # i de tamaño maximo b+1
            self.rectangles = rectangles
            self.points = points
            self.is_leaf = is_leaf  # bool
            self.parent = parent  # int
            self.mbr = mbr  # mbr
            self.deleted = deleted # bool

        def __str__(self):
            ret_str = f"pos: {self.pos}\n"
            ret_str += f"points: "
            for p in self.points:
                ret_str += f"[{p}] "
            ret_str += f"\n"
            ret_str += "rectangles: "
            for rec in self.rectangles:
                ret_str += f"{rec} "
            ret_str += f"\n"
            ret_str += f"is_leaf: {self.is_leaf}\n"
            ret_str += f"deleted: {self.deleted}\n"
            ret_str += f"parent: {self.parent}\n"
            ret_str += f"mbr: {self.mbr}\n"
            return ret_str

        def to_binary(self) -> bytes:
            """
            Convierte el rectangulo a bytes
            """
            global rect_format, point_format, b, tipo
            if self.mbr is None:
                raise ValueError(f"Rectangle at position {self.pos} has no MBR during serialization.")
            points = [
                p.to_binary() for p in self.points
            ]  # pos puntos rectangles is_leaf parent mbr

            temp = RTreeFile.Point(placeholder=True)
            while (len(points) < b+1):
                points.append(temp.to_binary())

            rects = self.rectangles[:]
            while(len(rects) < b+1):
                rects.append(-1)
            
            rect = struct.pack(rect_format, self.pos, self.is_leaf, self.parent, self.deleted, *rects)

            mbr = self.mbr.to_binary()
            return rect + b''.join(p for p in points) + mbr

        @staticmethod
        def from_binary(file, binary):
            """
            Convierte bytes a un objeto Rectangle
            """
            global rect_format, point_format, mbr_format, b, tipo

            offset = 0
            header_size = struct.calcsize(rect_format)
            rect_data = struct.unpack_from(rect_format, binary, offset)
            pos = rect_data[0]
            is_leaf = rect_data[1]
            parent = rect_data[2]
            deleted = rect_data[3]
            rectangles = list(rect_data[4:])
            offset += header_size

            rectangles = [val for val in rectangles if val != -1]

            point_size = struct.calcsize(point_format)
            points = []
            for _ in range(b + 1):
                point_bin = binary[offset:offset + point_size]
                point = RTreeFile.Point.from_binary(point_bin)
                if not point.placeholder:
                    points.append(point)
                offset += point_size

            mbr_size = struct.calcsize(mbr_format)
            mbr_bin = binary[offset:offset + mbr_size]
            mbr = RTreeFile.MBR.from_binary(mbr_bin)

            return RTreeFile.Rectangle(file, pos, rectangles, points, parent, is_leaf, mbr, deleted)

        def add_point(self, point):
            """
            Añade un punto al rectángulo
            """
            if self.mbr is None:
                self.mbr = RTreeFile.MBR(point.coords[:], point.coords[:])
            else:
                self.mbr.update_coords_point(point)

            if self.is_leaf:
                self.points.append(point)

        def add_rectangle(self, file, rec):
            """
            Añade un rectangulo al rectangulo 
            """
            if self.mbr is None:
                self.mbr = RTreeFile.MBR(rec.mbr.min_coords[:], rec.mbr.max_coords[:])
            else:
                self.mbr.update_coords_rec(rec)
            rec.parent = self.pos
            # file.write_rec_at(rec.pos, rec)
            self.rectangles.append(rec.pos)

        def size(self):
            return len(self.points)

        def remove(self, file, obj):
            """
            Elimina obj del objeto Rectangle
            obj puede ser un punto o la posición de un rectangulo
            """
            if self.is_leaf:
                for p in self.points:
                    if p.coords == obj.coords:
                        self.points.remove(p)
            elif not self.is_leaf and obj.pos in self.rectangles:
                self.rectangles.remove(obj.pos)
                rec = file.get_rec_at(obj.pos)
                rec.deleted = True
                file.write_rec_at(obj.pos, rec)

            if self.is_leaf and self.points:
                self.mbr = RTreeFile.MBR.calc_mbr(self.points)
            elif not self.is_leaf and self.rectangles:
                self.mbr = RTreeFile.MBR.calc_mbr_rec(file, self.rectangles)
            else:
                self.mbr = RTreeFile.MBR(RTreeFile.Point().coords, RTreeFile.Point().coords)

        def intersects(self, min_coords, max_coords):
            """
            Verifica si un rectangulo intersecta con un rango dado
            """
            for i in range(len(self.mbr.min_coords)):
                if (
                    self.mbr.max_coords[i] < min_coords[i]
                    or self.mbr.min_coords[i] > max_coords[i]
                ):
                    return False
            return True
        
    # MAIN CLASS 
    def __init__(self, table_format, p_key: str, keys: list = [], 
                 data_filename: str = "info/data.bin", 
                 index_filename: str = "info/index.bin",
                 force_create: bool = False
                 ):
        global point_format, mbr_format, rect_format, b, m, dim

        self.data_filename = data_filename
        self.index_filename = index_filename

        self.RT = RegistroType(table_format, keys)
        self.HEAP = Heap(table_format, p_key, data_filename, force_create=force_create)

        os.makedirs(os.path.dirname(self.index_filename), exist_ok=True)
        if not os.path.exists(self.index_filename): # crear archivo si no existe
            open(self.index_filename, 'w').close() 

        os.makedirs(os.path.dirname(self.data_filename), exist_ok=True)
        if not os.path.exists(self.data_filename): # crear archivo si no existe
            open(self.data_filename, 'w').close() 

        with open(self.index_filename, "ab+") as f:
            if f.tell() == 0:
                root = -1  # int
                b = 32
                dim = len(keys)
                m = int(b * 0.3)
                size = 0
                typef = table_format[keys[0]]  # can be changed to add support for different type indexes
                point_format = dim * typef + "?i"
                mbr_format = 2 * (dim * typef)
                rect_format = "i?i?" + ((b + 1) * "i")
                self.write_header(
                    root, size, b, m, dim, point_format, mbr_format, rect_format
                )
            else:
                root, size, b, m, dim, point_format, mbr_format, rect_format = (
                    self.get_header()
                )

    def get_root(self):
        """
        Retorna la posición de la raiz del arbol
        """
        return self.get_header()[0]

    def get_size(self):
        """
        Retorna la cantidad de rectangulos en el archivo
        """
        return self.get_header()[1]

    def write_root(self, root):
        """
        Escribe la raiz en el archivo de índices
        """
        global point_format, mbr_format, rect_format, b, m, dim, tipo
        self.write_header(root, self.get_size(), b, m, dim, point_format, mbr_format, rect_format)

    def write_size(self, size):
        """
        Escribe la cantidad de rectangulos en el archivo
        """
        global point_format, mbr_format, rect_format, b, m, dim, tipo
        self.write_header(self.get_root(), size, b, m, dim, point_format, mbr_format, rect_format)
    
    def __append_record(self, record):
        """
        Añade un registro al final del archivo de data
        """
        with open(self.data_filename, "ab") as f:
            pos = f.tell()
            f.write(self.RT.to_bytes(record))
            return int(pos/self.RT.size)

    def write_header(self, root, size, bf, mf, dimf, point_f, mbr_f, rect_f):
        """
        Escribe el header de los índices
        """
        with open(self.index_filename, "r+b") as f:
            f.seek(0)
            f.write(
                struct.pack(
                    header_format,
                    root,
                    size,
                    bf,
                    mf, 
                    dimf,
                    point_f.encode(),
                    mbr_f.encode(),
                    rect_f.encode(),
                )
            )

    def get_header(self):
        """
        Retorna el header del archivo de índices
        """
        with open(self.index_filename, "r+b") as f:
            global header_format, header_size
            f.seek(0)
            root, size, bf, mf, df, point_f, mbr_f, rect_f = struct.unpack(
                header_format, f.read(header_size)
            )
            return (
                root,
                size,
                bf,
                mf,
                df,
                point_f.decode().strip("\x00"),
                mbr_f.decode().strip("\x00"),
                rect_f.decode().strip("\x00"),
            )

    def write_rec_at(self, pos, rec):
        """
        Escribe el rectangulo rec en la posición pos en el archivo de índices
        """
        with open(self.index_filename, "r+b") as f:
            global rect_format, point_format, mbr_format, b
            point_size = struct.calcsize(point_format)
            mbr_size = struct.calcsize(mbr_format)
            total_size = struct.calcsize(rect_format) + (b + 1) * point_size + mbr_size
            f.seek(header_size + pos * total_size)
            f.write(rec.to_binary())

    def get_rec_at(self, pos):
        """
        Obtiene el rectángulo en la posición pos en el archivo de índices
        """
        with open(self.index_filename, "r+b") as f:
            global rect_format, point_format, mbr_format, b
            rect_format_size = struct.calcsize(rect_format)
            point_size = struct.calcsize(point_format)
            mbr_size = struct.calcsize(mbr_format)
            total_size = rect_format_size + (b + 1) * point_size + mbr_size
            f.seek(header_size + pos * total_size)
            return self.Rectangle.from_binary(self, f.read(total_size))
    
    def get_record_at(self, pos):
        """
        Obtiene el registro en la posicion pos en el archivo de data
        """
        with open(self.data_filename, "r+b") as f:
            f.seek(pos * self.RT.size + 4)
            return self.RT.from_bytes(f.read(self.RT.size))

    def choose_subtree(self, u, p):
        """
        Elige el subtree de los hijos de u donde sería mejor insertar p.
        Se elige el subtree en el cual se tendría que aumentar el menor perímetro.
        
        Retorna
        ---------------
            Posición del subarbol (rectangulo) donde insertar el punto 
        """
        best_mbr = None
        min_per = math.inf
        subtree = None

        for rec_pos in u.rectangles:
            rec = self.get_rec_at(rec_pos)
            mb = self.MBR(rec.mbr.min_coords[:], rec.mbr.max_coords[:])  # mbr de rec
            new_per = mb.update_coords_point(
                p
            )  # simulamos añadir el nuevo punto y devuelve la diferencia de perimetros

            if new_per < min_per:  # si el nuevo perimetro es menor al ya guardado
                min_per = new_per  # reemplazamos ese perimetro
                best_mbr = mb  # reemplazamos ese mbr
                subtree = rec_pos  # elegimos ese rec
            elif new_per == min_per:  # si es igual, elegimos al mbr con menor perimetro
                if mb.perimeter() < best_mbr.perimeter():
                    best_mbr = mb
                    subtree = rec_pos
        return subtree

    @staticmethod
    def split(file, u): # cuadratico
        """
        Dado un rectángulo u, aplica el split cuadrático para obtener el mejor split del rectángulo

        Retorna
        ---------------
            Dos rectángulos, u dividido en dos
        """
        global m
        if u.is_leaf:
            entries = u.points[:]
        else:
            entries = u.rectangles[:]

        # step 1: pick seeds
        max_waste = -math.inf
        seed1 = seed2 = None
        for i in range(len(entries)):
            for j in range(i+1, len(entries)):
                if u.is_leaf:
                    mbr_i = RTreeFile.MBR(entries[i].coords[:], entries[i].coords[:])
                    mbr_j = RTreeFile.MBR(entries[j].coords[:], entries[j].coords[:])
                else:
                    i_rec = file.get_rec_at(entries[i])
                    j_rec = file.get_rec_at(entries[j])
                    mbr_i = i_rec.mbr
                    mbr_j = j_rec.mbr

                combined = RTreeFile.MBR(mbr_i.min_coords[:], mbr_i.max_coords[:])

                if not u.is_leaf:
                    combined.update_coords_rec(RTreeFile.Rectangle(file=file, mbr=mbr_j))
                else:
                    mbr_j = RTreeFile.MBR(entries[j].coords[:], entries[j].coords[:])
                    combined.update_coords_rec(RTreeFile.Rectangle(file=file, points=[entries[j]], mbr=mbr_j))
                
                waste = combined.perimeter() - mbr_i.perimeter() - mbr_j.perimeter()

                if waste > max_waste:
                    max_waste = waste
                    seed1, seed2 = entries[i], entries[j]
        
        entries.remove(seed1)
        entries.remove(seed2)

        group1 = RTreeFile.Rectangle(file=file, is_leaf = u.is_leaf)
        group2 = RTreeFile.Rectangle(file=file, is_leaf = u.is_leaf)

        if u.is_leaf:
            group1.add_point(seed1)
            group2.add_point(seed2)
        else:
            seed1_rec = file.get_rec_at(seed1)
            seed2_rec = file.get_rec_at(seed2)
            
            group1.add_rectangle(file=file, rec=seed1_rec)
            group2.add_rectangle(file=file, rec=seed2_rec)
        
        # step 2: distribuir el resto de puntos/rectángulos

        while entries:
            # si grupo 1 necesita el resto de structs para tener el minimo
            if (len(group1.points if u.is_leaf else group1.rectangles) + len(entries)) == m:
                for e in entries:
                    if u.is_leaf:
                        group1.add_point(e)
                    else:
                        rec = file.get_rec_at(e)
                        group1.add_rectangle(file=file, rec=rec)
                break

            # si grupo 2 necesita el resto de structs para tener el minimo
            if (len(group2.points if u.is_leaf else group2.rectangles) + len(entries)) == m:
                for e in entries:
                    if u.is_leaf:
                        group2.add_point(e)
                    else:
                        rec = file.get_rec_at(e)
                        group2.add_rectangle(file=file, rec=rec)
                break

            # por cada punto/rec en entries
            # simular añadirlo a ambos grupos
            # elegimos el punto que maximice la diferencia de perimetros (cause el mayor desbalance de crecimiento)
            # se añade al grupo correspondiente
            
            max_diff = -math.inf
            chosen = None
            ch_d1 = ch_d2 = None

            for e in entries:
                if u.is_leaf:
                    mbr = RTreeFile.MBR(e.coords[:], e.coords[:])
                else:
                    rec = file.get_rec_at(e)
                    mbr = rec.mbr # can cause problems
                
                d1 = RTreeFile.MBR(group1.mbr.min_coords[:], group1.mbr.max_coords[:]) if group1.mbr else RTreeFile.MBR(mbr.min_coords[:], mbr.max_coords[:])
                d2 = RTreeFile.MBR(group2.mbr.min_coords[:], group2.mbr.max_coords[:]) if group2.mbr else RTreeFile.MBR(mbr.min_coords[:], mbr.max_coords[:])

                if u.is_leaf:
                    d1_inc = d1.update_coords_point(e)
                    d2_inc = d2.update_coords_point(e)
                else:
                    rec = file.get_rec_at(e)
                    d1_inc = d1.update_coords_rec(rec)
                    d2_inc = d2.update_coords_rec(rec)
                
                diff = abs(d1_inc - d2_inc)
                if diff > max_diff:
                    max_diff = diff
                    chosen = e
                    ch_d1 = d1_inc
                    ch_d2 = d2_inc
            
            entries.remove(chosen)

            
            if not u.is_leaf:
                rec = file.get_rec_at(chosen)

            if ch_d1 < ch_d2:
                group1.add_point(chosen) if u.is_leaf else group1.add_rectangle(file=file, rec=rec)
            elif ch_d2 < ch_d1:
                group2.add_point(chosen) if u.is_leaf else group2.add_rectangle(file=file, rec=rec)
            else:
                if group1.mbr.perimeter() < group2.mbr.perimeter():
                    group1.add_point(chosen) if u.is_leaf else group1.add_rectangle(file=file, rec=rec)
                else:
                    group2.add_point(chosen) if u.is_leaf else group2.add_rectangle(file=file, rec=rec)
            
        return group1, group2
    
    def handle_overflow(self, u_pos):
        """
        Maneja el caso en que el rectángulo en u_pos tenga más objetos (rectangulos/puntos) que el permitido (b)
        """
        global b
        u = self.get_rec_at(u_pos)
        x, y = RTreeFile.split(file=self, u=u)
        w_pos = u.parent
        if w_pos == -1:  # se crea un nuevo root if root overflows
            u.deleted = True
            self.write_rec_at(u_pos, u)

            end = self.get_size()

            new_root_pos = end
            end += 1

            new_root = RTreeFile.Rectangle(file=self, pos=new_root_pos, is_leaf=False)
            x.parent = new_root_pos
            y.parent = new_root_pos

            x_pos = end
            end += 1

            y_pos = end
            end += 1
            
            x.pos = x_pos
            y.pos = y_pos

            for rec_pos in x.rectangles:
                rec = self.get_rec_at(rec_pos)
                rec.parent = x_pos
                self.write_rec_at(rec_pos, rec)
            
            for rec_pos in y.rectangles:
                rec = self.get_rec_at(rec_pos)
                rec.parent = y_pos
                self.write_rec_at(rec_pos, rec)

            new_root.add_rectangle(self, x)
            new_root.add_rectangle(self, y)

            self.write_rec_at(new_root_pos, new_root)
            self.write_rec_at(x_pos, x)
            self.write_rec_at(y_pos, y)

            self.write_size(end)
            self.write_root(new_root_pos)
            # self.print_tree(new_root)
        else:
            w = self.get_rec_at(w_pos)
            w.remove(self, u)
            self.write_rec_at(w_pos, w)

            end = self.get_size()
            
            x_pos = end
            end += 1
            y_pos = end
            end += 1

            x.pos = x_pos
            y.pos = y_pos

            # Add x and y to the parent
            w.add_rectangle(self, x)
            w.add_rectangle(self, y)
            # self.print_tree(w)
            x.parent = w_pos
            y.parent = w_pos

            for rec_pos in x.rectangles:
                rec = self.get_rec_at(rec_pos)
                rec.parent = x_pos
                self.write_rec_at(rec_pos, rec)
            
            for rec_pos in y.rectangles:
                rec = self.get_rec_at(rec_pos)
                rec.parent = y_pos
                self.write_rec_at(rec_pos, rec)

            u.deleted = True
            self.write_rec_at(u_pos, u)

            self.write_rec_at(w_pos, w)
            self.write_rec_at(x_pos, x)
            self.write_rec_at(y_pos, y)

            self.write_size(end)

            if (
                len(w.rectangles) > b
            ):  # si w overflows, llamar a handle overflow again con w
                self.handle_overflow(w.pos)
                # self.print_tree(w)

    def __insert__(self, u_pos, p):
        """
        Función recursiva que inserta el punto p en el rectangulo en u_pos
        """
        # u is rectangle
        # p is point
        u = self.get_rec_at(u_pos)
        if u.is_leaf:
            u.add_point(p)
            self.write_rec_at(u_pos, u)
            if u.size() == b + 1:
                self.handle_overflow(u_pos)
        else:
            u.add_point(p)
            v_pos = self.choose_subtree(u, p)
            self.__insert__(v_pos, p)

    def aux_insert(self, point):
        """
        Inserta el punto point al árbol
        """
        root = self.get_root()
        if self.get_root() == -1:
            pos = self.get_size()
            self.write_root(pos)
            self.write_size(pos+1)
            new_root = self.Rectangle(file = self, pos=pos,is_leaf=True, mbr=self.MBR(point.coords, point.coords))
            self.write_rec_at(pos, new_root)
            root = pos

        self.__insert__(root, point)

    def insert(self, record, record_pos = None):
        """
        Inserta el registro en el índice
        
        Parametros
        ---------------
            record
                registro a insertar
            record_pos: int
                posición de registro en el data file
        """
        if record_pos is None:
            record_pos = self.HEAP.insert(record)
        coords = self.RT.get_key(record)
        point = RTreeFile.Point(coords=coords, index=record_pos)
        self.aux_insert(point)
    
    def sort_by_mindist(self, rectangles, point):
        """
        Ordena los rectangulos de acuerdo a su distancia minima con el punto

        Parametros
        ---------------
            rectangles
                lista de posiciones de rectangulos
            point
                punto
        """
        sorted_rec = []
        for rec_pos in rectangles:
            sorted_rec.append(self.get_rec_at(rec_pos))
        sorted(
            sorted_rec, key=lambda rec:RTreeFile.Point.mindist(point, rec.mbr)
        )
        ans = [rec.pos for rec in sorted_rec]
        return ans          

    def __ksearch__(self, node_pos, k, point, maxh):
        """
        Función recursiva para hacer la busqueda de knn

        Parametros
        ---------------
            node_pos
                el nodo donde se va a buscar
            k
                numero de vecinos a buscar
            point
                el punto de búsqueda
            maxh
                max heap de ayuda para mantener los k puntos más cercanos

        """
        node = self.get_rec_at(node_pos)
        if node.is_leaf:
            for p in node.points:
                dist = RTreeFile.Point.distance(p, point)
                if len(maxh) < k:
                    heapq.heappush(maxh, (-dist, p))
                elif dist < -maxh[0][0]:
                    heapq.heappushpop(maxh, (-dist, p))
        else:
            sorted_rec = self.sort_by_mindist(node.rectangles, point)
            for rec_pos in sorted_rec:
                rec = self.get_rec_at(rec_pos)
                if len(maxh) < k or RTreeFile.Point.mindist(point, rec.mbr) < -maxh[0][0]:
                    self.__ksearch__(rec_pos, k, point, maxh)
        return

    def aux_ksearch(self, k, point):
        """
        Función de ayuda que hace la búsqueda de knn

        Retorna
        ---------------
            lista de posiciones de los resultados de la busqueda
        """
        maxh = []
        self.__ksearch__(self.get_root(), k, point, maxh)
        return [pt.index for (d, pt) in sorted(maxh, key=lambda x: x[0], reverse=True)]
    
    def ksearch(self, k, query):
        """
        Función para hacer la busqueda de k vecinos cercanos en el arbol

        Parametros
        ---------------
            k
                numero de vecinos a buscar
            query: list
                lista de las coordenadas del punto de busqueda
        
        Retorna
        ---------------
            lista con las registros resultados de la busqueda
        """
        positions = self.aux_ksearch(k, RTreeFile.Point(query))
        records = []
        for pos in positions:
            record = self.HEAP.read(pos)
            records.append(record)
        return records

    def __range_search__(self, node_pos, min_coords, max_coords, ans):
        """
        Funcion recursiva que mantiene los resultados de la busqueda por rango en el rectangulo en node_pos
        """
        node = self.get_rec_at(node_pos)
        if node.is_leaf:
            for p in node.points:
                if p.inside(min_coords, max_coords):
                    ans.append(p.index)
        else:
            for rec_pos in node.rectangles:
                rec = self.get_rec_at(rec_pos)
                if rec.intersects(min_coords, max_coords):
                    self.__range_search__(rec_pos, min_coords, max_coords, ans)

    def aux_range_search(self, point_start, point_end):
        """
        Funcion auxiliar que toma dos puntos, los límites de la búsqueda, 
        y realiza la búsqueda por rango en el árbol de esos atributos.
        """
        ans = []
        self.__range_search__(self.get_root(), point_start.coords, point_end.coords, ans)
        return ans
    
    def range_search(self, coords_start, coords_end):
        """
        Función para hacer la busqueda por rango en el árbol

        Parametros
        ---------------
            coords_start: list
                lista con las coordenadas minimas de la busqueda
            coords_end: list
                lista con las coordenadas maximas de la busqueda
        Retorna
        ---------------
            lista con las registros resultados de la busqueda
        """
        positions = self.aux_range_search(RTreeFile.Point(coords_start), RTreeFile.Point(coords_end))
        records = []
        for pos in positions:
            record = self.HEAP.read(pos)
            records.append(record)
        return records

    def __search__(self, node_pos, point, ans):
        """
        Funcion recursiva que realiza la busqueda de point en el rectangulo en node_pos y los almacena en ans.
        """
        node = self.get_rec_at(node_pos)
        if node.is_leaf:
            for p in node.points:
                if p == point:
                    ans.append(p.index)
        else:
            for rec_pos in node.rectangles:
                rec = self.get_rec_at(rec_pos)
                if point.inside(rec.mbr.min_coords, rec.mbr.max_coords):
                    self.__search__(rec_pos, point, ans)

    def aux_search(self, point):
        """
        Devuelve las posiciones de los resultados de la busqueda
        """
        ans = []
        self.__search__(self.get_root(), point, ans)
        return ans
    
    def search(self, query: list):
        """
        Función para hacer la busqueda exacta en el arbol

        Parametros
        ---------------
            query: list
                lista con las coordenadas de la busqueda

        Retorna
        ---------------
            lista con las registros resultados de la busqueda
        """
        positions = self.aux_search(RTreeFile.Point(coords=query))
        records = []
        for pos in positions:
            record = self.HEAP.read(pos)
            records.append(record)
        return records

    def print_tree(self, node_pos=None, level=0):
        """
        Imprime el arbol con su estructura
        """
        if node_pos is None:
            node_pos = self.get_root()
        
        indent = "  " * level
        node = self.get_rec_at(node_pos)
        if node.is_leaf:
            print(f"{indent}Leaf Node at pos {node.pos} (Level {level}) with {len(node.points)} points:")
            for p in node.points:
                print(f"{indent}  Point: {p.coords}")
        else:
            print(
                f"{indent}Internal Node at pos {node.pos} (Level {level}) with {len(node.rectangles)} children:"
            )
            for child in node.rectangles:
                self.print_tree(child, level + 1)

    def print_file(self):
        """
        Imprime el contenido del archivo de indices
        """
        print(self.get_root())
        total_rects = self.get_size()
        print(total_rects)

        for i in range(total_rects):
            rec = self.get_rec_at(i)
            if not rec.deleted:
                print(f"Rectangle at position {i}: \n{rec}\n")

    def find_rec(self, node_pos, point):
        """
        Devuelve la posición del rectángulo que contiene a point
        """
        node = self.get_rec_at(node_pos)
        if node.is_leaf:
            for p in node.points:
                if p.coords == point.coords:
                    return node_pos
            return -1
        else:
            found = -1
            for rec_pos in node.rectangles:
                rec = self.get_rec_at(rec_pos)
                if point.inside(rec.mbr.min_coords, rec.mbr.max_coords):
                    found = self.find_rec(rec_pos, point)
                    if found != -1:
                        return found
            return found
        
    def get_leaves(self, node_pos):
        """
        Retorna una lista con las hojas dentre del rectangulo en node_pos
        """
        leaves = []

        def traverse(n_pos):
            n = self.get_rec_at(n_pos)
            if n.is_leaf:
                leaves.append(n_pos)
            else:
                for child in n.rectangles:
                    traverse(child)

        traverse(node_pos)
        return leaves

    def condense_tree(self, node_pos):
        """
        Funcion que elimina el rectangulo en node_pos si tiene menos de m puntos/rectangulos.
        Se reinsertan los puntos en el rectangulo a eliminar.
        """
        global m
        temp_pos = node_pos
        eliminated = []

        while True:
            if temp_pos == -1:
                break
            temp = self.get_rec_at(temp_pos)
            parent_pos = temp.parent

            if (temp.is_leaf and len(temp.points) < m) or (not temp.is_leaf and len(temp.rectangles) < m):
                parent = self.get_rec_at(parent_pos)
                parent.remove(self, temp)
                temp.deleted = True
                self.write_rec_at(temp.pos, temp)
                self.write_rec_at(parent_pos, parent)

                if temp_pos == self.get_root():
                    self.write_root(-1)

                leaf_rec = self.get_leaves(temp_pos)
                for r in leaf_rec:
                    eliminated.append(r)
            
            temp_pos = parent_pos
    
        unique_points = set()
        for rec_pos in eliminated:
            rec = self.get_rec_at(rec_pos)
            unique_points.update(rec.points)

        #self.print_file()
        for p in unique_points:
            self.aux_insert(p)
        #self.print_file()

        return
    
    def aux_delete(self, point):
        """
        Funcion auxiliar que elimina un punto en el archivo de índices
        """
        while True:
            rec_pos = self.find_rec(self.get_root(), point)
            if rec_pos == -1:
                break
            rec = self.get_rec_at(rec_pos)
            rec.remove(self, point)
            self.write_rec_at(rec_pos, rec)
            self.condense_tree(rec_pos)

        root = self.get_rec_at(self.get_root())
        if not root.is_leaf and len(root.rectangles) == 1:
            self.write_root(root.rectangles[0])
    
    def delete(self, query):
        """
        Funcion para eliminar los puntos que sean iguales a query

        Parametros
        ---------------
            query: list
                lista con las coordenadas de los puntos a eliminar
        """
        self.aux_delete(RTreeFile.Point(coords=query))