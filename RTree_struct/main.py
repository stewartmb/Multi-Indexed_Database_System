import math

b = 100
INT_MAX = 2**31-1
INT_MIN = -2**31

class Point:
    def __init__(self, coords):
        self.coords = coords

    @staticmethod
    def sort_points_by_dimension(points):
        num_dims = len(points[0].coords)
        sorted_by_dim = []
        for i in range(num_dims):
            sorted_dim = sorted(points, key=lambda p: p.coords[i])
            sorted_by_dim.append(sorted_dim)
        return sorted_by_dim

class MBR:
    def __init__(self, min_coords, max_coords):
        self.min_coords = min_coords
        self.max_coords = max_coords

    def perimeter(self):
        return 2 * sum(self.max_coords[i] - self.min_coords[i] for i in range(len(self.min_coords)))

    def update_coords_point(self, point):
        prev_perimeter = self.perimeter()
        for i in len(point.coords):
            self.min_coords[i] = min(self.min_coords[i], point[i])
            self.max_coords[i] = max(self.max_coords[i], point[i])
        new_perimeter = self.perimeter()
        return new_perimeter - prev_perimeter

    def update_coords_rec(self, rec):
        prev_perimeter = self.perimeter()
        for i in range(len(rec.min_coords)):
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

        return MBR(min_coords, max_coords)

    @staticmethod
    def calc_mbr_rec(rectangles):
        num_dims = len(rectangles[0].mbr.min_coords)
        min_coords = rectangles[0].mbr.min_coords[:]
        max_coords = rectangles[0].mbr.max_coords[:]

        for rec in rectangles[1:]:
            for i in range(num_dims):
                min_coords[i] = min(min_coords[i], rec.mbr.min_coords[i])
                max_coords[i] = max(max_coords[i], rec.mbr.max_coords[i])

        return MBR(min_coords, max_coords)


class Rectangle:
    def __init__(self, rectangles=None, points=None, parent=None, is_leaf=True, mbr=None):
        if points is None:
            points = []
        if rectangles is None:
            rectangles = []
        self.rectangles = rectangles
        self.points = points
        self.is_leaf = is_leaf
        self.parent = parent
        self.mbr = mbr

    def add_point(self, point):
        self.mbr.update_coords_point(point)
        self.points.append(point)

    def add_rectangle(self, rec):
        self.mbr.update_coords_rec(rec)
        rec.parent = self
        self.rectangles.append(rec)

    def size(self):
        return len(self.points)

    @staticmethod
    def sort_rectangles_by_dimension_min(rectangles):
        num_dims = len(rectangles[0].mbr.min_coords)
        sorted_by_dim = []
        for i in range(num_dims):
            sorted_dim = sorted(rectangles, key=lambda r: r.mbr.min_coords[i])
            sorted_by_dim.append(sorted_dim)
        return sorted_by_dim

    @staticmethod
    def sort_rectangles_by_dimension_max(rectangles):
        num_dims = len(rectangles[0].mbr.max_coords)
        sorted_by_dim = []
        for i in range(num_dims):
            sorted_dim = sorted(rectangles, key=lambda r: r.mbr.max_coords[i])
            sorted_by_dim.append(sorted_dim)
        return sorted_by_dim


class RTree:
    def __init__(self, root=None, b=6):
        self.root = root

    @staticmethod
    def choose_subtree(u, p):
        best_mbr = None
        min_per = INT_MAX
        subtree = None

        for rec in u.rectangles:
            mb = MBR(rec.min_coords, rec.max_coords) # mbr de rec
            new_per = mb.update_coords_point(p) # simulamos añadir el nuevo punto y devuelve la diferencia de perimetros
            if new_per < min_per: # si el nuevo perimetro es menor al ya guardado
                min_per = new_per # reemplazamos ese perimetro
                best_mbr = mb # reemplazamos ese mbr
                subtree = rec # elegimos ese rec
            elif new_per == min_per: # si es igual, elegimos al mbr con menor perimetro
                if mb.perimeter() < best_mbr.perimeter():
                    best_mbr = mb
                    subtree = rec
        subtree.mbr = best_mbr
        return subtree

    @staticmethod
    def split_leaf(u):
        m = len(u.points)
        min_per = INT_MAX
        best_split = None, None

        all_sorted = Point.sort_points_by_dimension(u.points)
        for dim in all_sorted:
            for i in range(math.ceil(0.4*b), m - math.ceil(0.4*b)):
                s1 = dim[0:i]
                s2 = dim[i:]
                mbr1 = MBR.calc_mbr(s1)
                mbr2 = MBR.calc_mbr(s2)

                if mbr1.perimeter() + mbr2.perimeter() < min_per:
                    min_per = mbr1.perimeter() + mbr2.perimeter()
                    best_split = Rectangle(points=s1, mbr=mbr1), Rectangle(points=s2, mbr=mbr2)

        return best_split

    @staticmethod
    def split_internal(u):
        m = len(u.rectangles)
        min_per = INT_MAX
        best_split = None, None

        all_sorted_min = Rectangle.sort_rectangles_by_dimension_min(u.rectangles)
        for dim in all_sorted_min:
            for i in range(math.ceil(0.4*b), m - math.ceil(0.4*b)):
                s1 = dim[0:i]
                s2 = dim[i:]
                mbr1 = MBR.calc_mbr_rec(s1)
                mbr2 = MBR.calc_mbr_rec(s2)

                if mbr1.perimeter() + mbr2.perimeter() < min_per:
                    min_per = mbr1.perimeter() + mbr2.perimeter()
                    best_split = Rectangle(points=s1, mbr=mbr1), Rectangle(points=s2, mbr=mbr2)

        all_sorted_max = Rectangle.sort_rectangles_by_dimension_max(u.rectangles)
        for dim in all_sorted_max:
            for i in range(math.ceil(0.4 * b), m - math.ceil(0.4 * b)):
                s1 = dim[0:i]
                s2 = dim[i:]
                mbr1 = MBR.calc_mbr_rec(s1)
                mbr2 = MBR.calc_mbr_rec(s2)

                if mbr1.perimeter() + mbr2.perimeter() < min_per:
                    min_per = mbr1.perimeter() + mbr2.perimeter()
                    best_split = Rectangle(points=s1, mbr=mbr1), Rectangle(points=s2, mbr=mbr2)

        return best_split

    @staticmethod
    def split(u):
        if u.is_leaf:
            return RTree.split_leaf(u)
        return RTree.split_internal(u)

    def handle_overflow(self, u):
        u, v = RTree.split(u)
        if self.root == u:
            new_root = Rectangle(is_leaf=False)
            new_root.add_rectangle(u)
            new_root.add_rectangle(v)
        else:
            w = u.parent
            # update mbr de u
            w.add_rectangle(u) # add v as child of w
            if w == b+1: # si w overflows, llamar a handle overflow again con w
                self.handle_overflow(w)


    def __insert__(self, u, p):
        # u is rectangle
        # p is point
        if u.is_leaf:
            u.add_point(p)
            if u.size() == b+1:
                self.handle_overflow(u)
        else:
            v = RTree.choose_subtree(u, p)
            self.__insert__(v, p)

    def insert(self, point):
        if self.root is None:
            self.root = Rectangle(is_leaf = True)

        self.__insert__(self.root, point);
