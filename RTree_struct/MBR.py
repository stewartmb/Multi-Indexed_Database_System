from Point import Point

INT_MAX = 2**31 - 1
INT_MIN = -(2**31)


class MBR:
    def __init__(self, min_coords, max_coords):
        self.min_coords = min_coords
        self.max_coords = max_coords

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
