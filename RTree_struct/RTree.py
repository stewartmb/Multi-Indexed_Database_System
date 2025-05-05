import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import heapq

b = 4

INT_MAX = 2**31 - 1
INT_MIN = -(2**31)


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

    def inside(self, min_coords, max_coords):
        return all(
            min_coords[i] <= self.coords[i] <= max_coords[i]
            for i in range(len(self.coords))
        )

    def __lt__(self, other):
        return self.coords < other.coords

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
        return str(self.coords)


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


class Rectangle:
    def __init__(
        self, rectangles=None, points=None, parent=None, is_leaf=True, mbr=None
    ):
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


class RTree:
    def __init__(self, root=None):
        self.root = root
        self.b = b

    @staticmethod
    def choose_subtree(u, p):
        best_mbr = None
        min_per = INT_MAX
        subtree = None
        for rec in u.rectangles:
            mb = MBR(rec.mbr.min_coords[:], rec.mbr.max_coords[:])  # mbr de rec
            new_per = mb.update_coords_point(
                p
            )  # simulamos añadir el nuevo punto y devuelve la diferencia de perimetros

            if new_per < min_per:  # si el nuevo perimetro es menor al ya guardado
                min_per = new_per  # reemplazamos ese perimetro
                best_mbr = mb  # reemplazamos ese mbr
                subtree = rec  # elegimos ese rec
            elif new_per == min_per:  # si es igual, elegimos al mbr con menor perimetro
                if mb.perimeter() < best_mbr.perimeter():
                    best_mbr = mb
                    subtree = rec
        return subtree

    @staticmethod
    def split_leaf(u):
        m = len(u.points)
        min_per = INT_MAX
        best_split = None, None

        all_sorted = Point.sort_points_by_dimension(u.points)
        for dim in all_sorted:
            for i in range(math.ceil(0.4 * b), m - math.ceil(0.4 * b) + 1):
                s1 = dim[0:i]
                s2 = dim[i:]
                mbr1 = MBR.calc_mbr(s1)
                mbr2 = MBR.calc_mbr(s2)

                if mbr1.perimeter() + mbr2.perimeter() < min_per:
                    min_per = mbr1.perimeter() + mbr2.perimeter()
                    best_split = (
                        Rectangle(points=s1, mbr=mbr1, is_leaf=True),
                        Rectangle(points=s2, mbr=mbr2, is_leaf=True),
                    )

        return best_split

    @staticmethod
    def split_internal(u):
        m = len(u.rectangles)
        min_per = INT_MAX
        best_split = None, None

        all_sorted_min = Rectangle.sort_rectangles_by_dimension_min(u.rectangles)
        for dim in all_sorted_min:
            for i in range(math.ceil(0.4 * b), m - math.ceil(0.4 * b) + 1):
                s1 = dim[0:i]
                s2 = dim[i:]
                mbr1 = MBR.calc_mbr_rec(s1)
                mbr2 = MBR.calc_mbr_rec(s2)

                if mbr1.perimeter() + mbr2.perimeter() < min_per:
                    min_per = mbr1.perimeter() + mbr2.perimeter()
                    best_split = (
                        Rectangle(rectangles=s1, mbr=mbr1, is_leaf=False),
                        Rectangle(rectangles=s2, mbr=mbr2, is_leaf=False),
                    )

        all_sorted_max = Rectangle.sort_rectangles_by_dimension_max(u.rectangles)
        for dim in all_sorted_max:
            for i in range(math.ceil(0.4 * b), m - math.ceil(0.4 * b) + 1):
                s1 = dim[0:i]
                s2 = dim[i:]
                mbr1 = MBR.calc_mbr_rec(s1)
                mbr2 = MBR.calc_mbr_rec(s2)

                if mbr1.perimeter() + mbr2.perimeter() < min_per:
                    min_per = mbr1.perimeter() + mbr2.perimeter()
                    best_split = (
                        Rectangle(rectangles=s1, mbr=mbr1, is_leaf=False),
                        Rectangle(rectangles=s2, mbr=mbr2, is_leaf=False),
                    )

        return best_split

    @staticmethod
    def split(u):
        if u.is_leaf:
            return RTree.split_leaf(u)
        return RTree.split_internal(u)

    def handle_overflow(self, u):
        x, y = RTree.split(u)
        w = u.parent
        if w is None:  # se crea un nuevo root if root overflows
            new_root = Rectangle(is_leaf=False)
            x.parent = new_root
            y.parent = new_root
            new_root.add_rectangle(x)
            new_root.add_rectangle(y)
            self.root = new_root
            # self.print_tree(new_root)
        else:
            w.remove(u)
            # Add u and v to the parent
            w.add_rectangle(x)
            w.add_rectangle(y)
            # self.print_tree(w)
            x.parent = w
            y.parent = w
            if (
                len(w.rectangles) > b
            ):  # si w overflows, llamar a handle overflow again con w
                self.handle_overflow(w)
                # self.print_tree(w)

    def __insert__(self, u, p):
        # u is rectangle
        # p is point
        if u.is_leaf:
            u.add_point(p)
            if u.size() == b + 1:
                self.handle_overflow(u)
        else:
            u.add_point(p)
            v = RTree.choose_subtree(u, p)
            self.__insert__(v, p)

    def insert(self, point):
        if self.root is None:
            self.root = Rectangle(is_leaf=True)

        self.__insert__(self.root, point)
        self.visualize_tree(self.root)

    def __ksearch__(self, node, k, point, maxh):
        if node.is_leaf:
            for p in node.points:
                dist = Point.distance(p, point)
                if len(maxh) < k:
                    heapq.heappush(maxh, (-dist, p))
                elif dist < -maxh[0][0]:
                    heapq.heappushpop(maxh, (-dist, p))
        else:
            sorted_rec = sorted(
                node.rectangles, key=lambda rec: Point.mindist(point, rec.mbr)
            )
            for rec in sorted_rec:
                if len(maxh) < k or Point.mindist(point, rec.mbr) < -maxh[0][0]:
                    self.__ksearch__(rec, k, point, maxh)
        return

    def ksearch(self, k, point):
        maxh = []
        self.__ksearch__(self.root, k, point, maxh)
        return [pt for (d, pt) in sorted(maxh, key=lambda x: x[0], reverse=True)]

    def __range_search__(self, node, min_coords, max_coords, ans):
        if node.is_leaf:
            for p in node.points:
                if p.inside(min_coords, max_coords):
                    ans.append(p)
        else:
            for rec in node.rectangles:
                if rec.intersects(min_coords, max_coords):
                    self.__range_search__(rec, min_coords, max_coords, ans)

    def range_search(self, point_start, point_end):
        ans = []
        self.__range_search__(self.root, point_start.coords, point_end.coords, ans)
        return ans

    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        indent = "  " * level
        if node.is_leaf:
            print(f"{indent}Leaf Node (Level {level}) with {len(node.points)} points:")
            for p in node.points:
                print(f"{indent}  Point: {p.coords}")
        else:
            print(
                f"{indent}Internal Node (Level {level}) with {len(node.rectangles)} children:"
            )
            for child in node.rectangles:
                self.print_tree(child, level + 1)

    def visualize_tree(self, node, ax=None, level=0, color="black"):
        if ax is None:
            fig, ax = plt.subplots()
            ax.set_xlim(0, 15)
            ax.set_ylim(0, 15)
            ax.set_title("R-tree Split Visualization")
            ax.set_aspect("equal")

        if node.mbr:
            width = node.mbr.max_coords[0] - node.mbr.min_coords[0]
            height = node.mbr.max_coords[1] - node.mbr.min_coords[1]
            rect = patches.Rectangle(
                (node.mbr.min_coords[0], node.mbr.min_coords[1]),
                width,
                height,
                linewidth=1.5,
                edgecolor=color,
                facecolor="none",
            )
            ax.add_patch(rect)
            # Add label for level
            ax.text(
                node.mbr.min_coords[0] + width / 2,
                node.mbr.min_coords[1] + height / 2,
                f"L{level}",
                color=color,
                fontsize=8,
                ha="center",
                va="center",
            )

        if node.is_leaf:
            for p in node.points:
                ax.plot(p.coords[0], p.coords[1], "ko")
        else:
            colors = ["red", "blue", "green", "orange", "purple", "brown"]
            for child in node.rectangles:
                next_color = colors[(level + 1) % len(colors)]
                self.visualize_tree(child, ax=ax, level=level + 1, color=next_color)

        if level == 0:
            plt.show()


if __name__ == "__main__":
    rtree = RTree()

    # Insert enough points to cause internal node split
    points = [
        Point([1, 1]),
        Point([2, 2]),
        Point([3, 3]),
        Point([4, 4]),
        Point([5, 5]),
        Point([6, 6]),
        Point([7, 7]),
        Point([8, 8]),
        Point([9, 9]),
        Point([10, 10]),
        Point([11, 11]),
        Point([12, 12]),
        Point([13, 13]),
        Point([14, 14]),
        Point([15, 15]),
    ]

    for pt in points:
        rtree.insert(pt)

    # ans = rtree.ksearch(6, Point([6,3]))
    # a = list(map(print, ans))

    ans = rtree.range_search(Point([3, 2]), Point([7, 6]))
    a = list(map(print, ans))
