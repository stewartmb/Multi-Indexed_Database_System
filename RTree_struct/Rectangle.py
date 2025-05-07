from MBR import MBR

INT_MAX = 2**31 - 1
INT_MIN = -(2**31)


class Rectangle:
    def __init__(
        self,
        pos=None,
        rectangles=None,
        points=None,
        parent=None,
        is_leaf=True,
        mbr=None,
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

    def add_point(self, point):
        if self.mbr is None:  # si no hay mbr, crearlo
            self.mbr = MBR(point.coords[:], point.coords[:])
        else:
            self.mbr.update_coords_point(point)
        self.points.append(point)

    def add_rectangle(self, rec):
        if self.mbr is None:
            self.mbr = MBR(rec.mbr.min_coords[:], rec.mbr.max_coords[:])
        else:
            self.mbr.update_coords_rec(rec)
        rec.parent = self
        self.rectangles.append(rec)

    def size(self):
        return len(self.points)

    def __str__(self):
        return f"{self.mbr.min_coords} {self.mbr.max_coords}"

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

    def remove(self, obj):
        if self.is_leaf and obj in self.points:
            self.points.remove(obj)
        elif not self.is_leaf and obj in self.rectangles:
            self.rectangles.remove(obj)

        if self.is_leaf and self.points:
            self.mbr = MBR.calc_mbr(self.points)
        elif not self.is_leaf and self.rectangles:
            self.mbr = MBR.calc_mbr_rec(self.rectangles)
        else:
            self.mbr = None

    def intersects(self, min_coords, max_coords):
        for i in range(len(self.mbr.min_coords)):
            if (
                self.mbr.max_coords[i] < min_coords[i]
                or self.mbr.min_coords[i] > max_coords[i]
            ):
                return False
        return True
