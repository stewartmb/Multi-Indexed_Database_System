import math
import heapq
import struct

INT_MAX = 2**31 - 1
INT_MIN = -(2**31)

point_format = ""
mbr_format = ""
rect_format = ""
header_format = "iiiii255s255s255s"
header_size = struct.calcsize(header_format)
b=16
m=2
dim=2
tipo="i"

def logg(s):
    print(f"LOG: {s}")

class RTreeFile:
    class Point:
        def __init__(self, coords=None, placeholder=False, index=-1):
            if coords is None:
                coords = []
                for i in range(dim):
                    coords.append(i)
            self.coords = coords
            self.placeholder = placeholder
            self.index = index

        def to_binary(self):
            global point_format
            return struct.pack(point_format, *self.coords, self.placeholder, self.index)

        def __hash__(self):
            return hash(tuple(self.coords))
    
        @staticmethod
        def from_binary(binary):
            global point_format
            data = struct.unpack(point_format, binary)
            coords = list(data[:dim])
            placeholder = data[dim]
            index = data[dim + 1]
            return RTreeFile.Point(coords=coords, placeholder=placeholder, index=index)

        @staticmethod
        def sort_points_by_dimension(points):
            num_dims = len(points[0].coords)
            sorted_by_dim = []
            for i in range(num_dims):
                sorted_dim = sorted(points, key=lambda p: p.coords[i])
                sorted_by_dim.append(sorted_dim)
            return sorted_by_dim

        def inside(self, min_coords, max_coords):
            return all(
                min_coords[i] <= self.coords[i] <= max_coords[i]
                for i in range(len(self.coords))
            )

        def __lt__(self, other):
            return self.coords < other.coords
        
        def __eq__(self, other):
            return self.coords == other.coords

        @staticmethod
        def distance(p1, p2):
            return math.sqrt(
                sum((p1.coords[i] - p2.coords[i]) ** 2 for i in range(len(p1.coords)))
            )

        @staticmethod
        def mindist(q, mbr):
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
        def __init__(self, min_coords, max_coords):
            self.min_coords = min_coords
            self.max_coords = max_coords

        def to_binary(self):
            global mbr_format
            return struct.pack(mbr_format, *self.min_coords, *self.max_coords)

        @staticmethod
        def from_binary(binary):
            global mbr_format
            coords = struct.unpack(mbr_format, binary)
            assert len(coords) % 2 == 0, "Invalid MBR binary format"
            min_coords = list(coords[: len(coords) // 2])
            max_coords = list(coords[len(coords) // 2 :])
            return RTreeFile.MBR(min_coords, max_coords)

        def __str__(self):
            return f"MBR: {self.min_coords}, {self.max_coords}"

        def perimeter(self):
            return 2 * sum(
                self.max_coords[i] - self.min_coords[i] for i in range(len(self.min_coords))
            )

        def update_coords_point(self, point):
            prev_perimeter = self.perimeter()
            for i in range(len(point.coords)):
                self.min_coords[i] = min(self.min_coords[i], point.coords[i])
                self.max_coords[i] = max(self.max_coords[i], point.coords[i])
            new_perimeter = self.perimeter()
            return new_perimeter - prev_perimeter

        def update_coords_rec(self, rec):
            prev_perimeter = self.perimeter()
            for i in range(len(rec.mbr.min_coords)):
                self.min_coords[i] = min(self.min_coords[i], rec.mbr.min_coords[i])
                self.max_coords[i] = max(self.max_coords[i], rec.mbr.max_coords[i])
            new_perimeter = self.perimeter()
            return new_perimeter - prev_perimeter

        @staticmethod
        def smaller_mbr(mbr1, mbr2):
            if mbr1.perimeter() < mbr2.perimeter():
                return mbr1
            else:
                return mbr2

        @staticmethod
        def calc_mbr(points):
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

        def to_binary(self):
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
            if self.mbr is None:
                self.mbr = RTreeFile.MBR(point.coords[:], point.coords[:])
            else:
                self.mbr.update_coords_point(point)

            if self.is_leaf:
                self.points.append(point)

        def add_rectangle(self, file, rec):
            if self.mbr is None:
                self.mbr = RTreeFile.MBR(rec.mbr.min_coords[:], rec.mbr.max_coords[:])
            else:
                self.mbr.update_coords_rec(rec)
            rec.parent = self.pos
            # file.write_rec_at(rec.pos, rec)
            self.rectangles.append(rec.pos)

        def size(self):
            return len(self.points)

        @staticmethod
        def sort_rectangles_by_dimension_min(file, rectangles_pos):
            rectangles = [file.get_rec_at(x) for x in rectangles_pos]
            num_dims = len(rectangles[0].mbr.min_coords)
            sorted_by_dim = []
            for i in range(num_dims):
                sorted_dim = sorted(rectangles, key=lambda r: r.mbr.min_coords[i])
                sorted_by_dim.append(sorted_dim)
            return sorted_by_dim

        @staticmethod
        def sort_rectangles_by_dimension_max(file, rectangles_pos):
            rectangles = [file.get_rec_at(x) for x in rectangles_pos]
            num_dims = len(rectangles[0].mbr.max_coords)
            sorted_by_dim = []
            for i in range(num_dims):
                sorted_dim = sorted(rectangles, key=lambda r: r.mbr.max_coords[i])
                sorted_by_dim.append(sorted_dim)
            return sorted_by_dim

        def remove(self, file, obj):
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
            for i in range(len(self.mbr.min_coords)):
                if (
                    self.mbr.max_coords[i] < min_coords[i]
                    or self.mbr.min_coords[i] > max_coords[i]
                ):
                    return False
            return True
    def __init__(self, filename="index.bin", bf=16, dimf=2, typef="i", mf=2):
        self.filename = filename
        global point_format, mbr_format, rect_format, b, m, dim, tipo
        with open(self.filename, "ab+") as f:
            if f.tell() == 0:
                root = -1  # int
                b = bf
                dim = dimf
                tipo = typef
                m = mf
                size = 0
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
                # Print formats for debugging
        print(f"rect_format: {rect_format}")
        print(f"point_format: {point_format}")
        print(f"mbr_format: {mbr_format}")

    def get_root(self):
        return self.get_header()[0]

    def get_size(self):
        return self.get_header()[1]

    def write_root(self, root):
        global point_format, mbr_format, rect_format, b, m, dim, tipo
        self.write_header(root, self.get_size(), b, m, dim, point_format, mbr_format, rect_format)

    def write_size(self, size):
        global point_format, mbr_format, rect_format, b, m, dim, tipo
        self.write_header(self.get_root(), size, b, m, dim, point_format, mbr_format, rect_format)

    def write_header(self, root, size, bf, mf, dimf, point_f, mbr_f, rect_f):
        with open(self.filename, "r+b") as f:
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
        with open(self.filename, "r+b") as f:
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
        with open(self.filename, "r+b") as f:
            global rect_format, point_format, mbr_format, b
            point_size = struct.calcsize(point_format)
            mbr_size = struct.calcsize(mbr_format)
            total_size = struct.calcsize(rect_format) + (b + 1) * point_size + mbr_size
            f.seek(header_size + pos * total_size)
            f.write(rec.to_binary())

    def get_rec_at(self, pos):
        with open(self.filename, "r+b") as f:
            global rect_format, point_format, mbr_format, b
            rect_format_size = struct.calcsize(rect_format)
            point_size = struct.calcsize(point_format)
            mbr_size = struct.calcsize(mbr_format)
            total_size = rect_format_size + (b + 1) * point_size + mbr_size
            f.seek(header_size + pos * total_size)
            return self.Rectangle.from_binary(self, f.read(total_size))

    def choose_subtree(self, u, p):
        best_mbr = None
        min_per = INT_MAX
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

    def insert(self, point):
        root = self.get_root()
        if self.get_root() == -1:
            pos = self.get_size()
            self.write_root(pos)
            self.write_size(pos+1)
            new_root = self.Rectangle(file = self, pos=pos,is_leaf=True, mbr=self.MBR(point.coords, point.coords))
            self.write_rec_at(pos, new_root)

        self.__insert__(root, point)
        # self.visualize_tree(self.root)
    
    def sort_by_mindist(self, rectangles, point):
        sorted_rec = []
        for rec_pos in rectangles:
            sorted_rec.append(self.get_rec_at(rec_pos))
        sorted(
            sorted_rec, key=lambda rec:RTreeFile.Point.mindist(point, rec.mbr)
        )
        ans = [rec.pos for rec in sorted_rec]
        return ans          

    def __ksearch__(self, node_pos, k, point, maxh):
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

    def ksearch(self, k, point):
        maxh = []
        self.__ksearch__(self.get_root(), k, point, maxh)
        return [pt for (d, pt) in sorted(maxh, key=lambda x: x[0], reverse=True)]

    def __range_search__(self, node_pos, min_coords, max_coords, ans):
        node = self.get_rec_at(node_pos)
        if node.is_leaf:
            for p in node.points:
                if p.inside(min_coords, max_coords):
                    ans.append(p)
        else:
            for rec_pos in node.rectangles:
                rec = self.get_rec_at(rec_pos)
                if rec.intersects(min_coords, max_coords):
                    self.__range_search__(rec_pos, min_coords, max_coords, ans)

    def range_search(self, point_start, point_end):
        ans = []
        self.__range_search__(self.get_root(), point_start.coords, point_end.coords, ans)
        return ans

    def __search__(self, node_pos, point, ans):
        node = self.get_rec_at(node_pos)
        if node.is_leaf:
            for p in node.points:
                if p == point:
                    ans.append(p)
        else:
            for rec_pos in node.rectangles:
                rec = self.get_rec_at(rec_pos)
                if point.inside(rec.mbr.min_coords, rec.mbr.max_coords):
                    self.__search__(rec_pos, point, ans)

    def search(self, point):
        ans = []
        self.__search__(self.get_root(), point, ans)
        return ans
    
    def print_tree(self, node_pos=None, level=0):
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
        print(self.get_root())
        total_rects = self.get_size()
        print(total_rects)

        for i in range(total_rects):
            rec = self.get_rec_at(i)
            if not rec.deleted:
                print(f"Rectangle at position {i}: \n{rec}\n")

    def find_rec(self, node_pos, point):
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
            self.insert(p)
        #self.print_file()

        return
    
    def delete(self, point):
        rec_pos = self.find_rec(self.get_root(), point)
        rec = self.get_rec_at(rec_pos)
        rec.remove(self, point)
        self.write_rec_at(rec_pos, rec)
        self.condense_tree(rec_pos)

        raiz = self.get_rec_at(self.get_root())
        if len(raiz.rectangles) == 1:
            raiz_pos = raiz.rec[0]
            self.write_root(raiz_pos)
            

if __name__ == "__main__":
    rtree = RTreeFile(bf = 4)

    points = [
        # RTreeFile.Point(coords=[1, 1]),
        # RTreeFile.Point(coords=[2, 2]),
        # RTreeFile.Point(coords=[3, 3]),
        # RTreeFile.Point(coords=[4, 4]),
        # RTreeFile.Point(coords=[5, 5]),
        # RTreeFile.Point(coords=[6, 6]),
        # RTreeFile.Point(coords=[7, 7]),
        # RTreeFile.Point(coords=[8, 8]),
        # RTreeFile.Point(coords=[9, 9]),
        # RTreeFile.Point(coords=[10, 10]),
        # RTreeFile.Point(coords=[11, 11]),
        # RTreeFile.Point(coords=[12, 12]),
        # RTreeFile.Point(coords=[13, 13]),
        # RTreeFile.Point(coords=[14, 14]),
        # RTreeFile.Point(coords=[15, 15]),
        # RTreeFile.Point(coords=[3, 2]),
        # RTreeFile.Point(coords=[1, 12]),
        # RTreeFile.Point(coords=[18, 12]),
        # RTreeFile.Point(coords=[1, 3]),
        # RTreeFile.Point(coords=[2, 3]),
        # RTreeFile.Point(coords=[1, 2])
        RTreeFile.Point(index=0, coords=[1, 2]),
        RTreeFile.Point(index=3, coords=[1, 2]),
        RTreeFile.Point(index=2, coords=[1, 2]),

    ]

    # for pt in points:
    #     rtree.insert(pt)
    #     print(f"inserted point {pt}")
        # print("----------------FILE----------------")
        # rtree.print_file()
        # print("----------------FILE-END----------------")

    # print(50*"-")

    # print(len(points))

    # points = rtree.ksearch(3, RTreeFile.Point(coords=[4,2]))

    # print("K SEARCH")
    # for pt in points:
    #     print(pt)

    # print("RANGE SEARCH")

    # points = rtree.range_search(RTreeFile.Point(coords=[0,0]), RTreeFile.Point(coords=[5, 6]))
    # for pt in points:
    #     print(pt)

    # rtree.delete(RTreeFile.Point(coords=[4, 4]))

    rtree.print_tree()

    print("-------------------------------------------")

    # rtree.print_file()
    
    points = rtree.search(RTreeFile.Point(coords=[1, 2]))
    for pt in points:
        print(pt)