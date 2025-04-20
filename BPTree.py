class BPTreeNode:
    def __init__(self, leaf, M):
        self.leaf = leaf
        self.M = M
        self.keys = []
        self.children = []
        self.father = None  # Enlace al padre
        self.next = None  # Enlace a la siguiente hoja

class BPTree:
    def __init__(self, M):
        self.M = M
        self.root = BPTreeNode(leaf=True, M=M)

    def insert(self, key):
        root = self.root
        if len(root.keys) == self.M - 1:
            new_root = BPTreeNode(leaf=False, M=self.M)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, key)

    def _insert_non_full(self, node, key):
        if node.leaf:
            index = self._find_index(node.keys, key)
            node.keys.insert(index, key)
        else:
            index = self._find_index(node.keys, key)
            child = node.children[index]
            if len(child.keys) == self.M - 1:
                self._split_child(node, index)
                if key > node.keys[index]:
                    index += 1
            self._insert_non_full(node.children[index], key)

    def _split_child(self, parent, index):
        child    = parent.children[index]
        new_child = BPTreeNode(leaf=child.leaf, M=self.M)

        if child.leaf:
            # --- división de hoja ---
            mid = self.M // 2  # ej. 4//2 = 2 → 2 claves en left, 1 en right
            new_child.keys = child.keys[mid:]
            child.keys     = child.keys[:mid]
            # ajustar enlaces
            new_child.next = child.next
            child.next     = new_child
            # insertar separador en el padre
            parent.keys.insert(index, new_child.keys[0])

        else:
            # --- división de nodo interno ---
            mid = (self.M - 1) // 2   # ej. (4-1)//2 = 1 → promociona child.keys[1]
            promoted = child.keys[mid]

            # repartir claves
            new_child.keys     = child.keys[mid+1:]
            child.keys         = child.keys[:mid]

            # repartir punteros
            new_child.children = child.children[mid+1:]
            child.children     = child.children[:mid+1]

            # insertar la clave promocionada en el padre
            parent.keys.insert(index, promoted)

        # finalmente, conectar el nuevo hijo
        parent.children.insert(index+1, new_child)


    def _find_index(self, keys, key):
        for i, item in enumerate(keys):
            if key < item:
                return i
        return len(keys)

    def print_tree(self):
        def _print(node, level):
            print("Nivel", level, ":", node.keys)
            if not node.leaf:
                for child in node.children:
                    _print(child, level + 1)
        _print(self.root, 0)

    def search(self, key):
        node = self.root
        while not node.leaf:
            index = self._find_index(node.keys, key)
            node = node.children[index]
        return key in node.keys


tree = BPTree(M=3)

for k in [10, 20, 5, 6, 12, 30, 7, 17]:
    tree.insert(k)

print("Árbol B+ después de las inserciones:")

# find the key 12 
found = tree.search(1)

tree.insert(13)
tree.insert(14)
tree.print_tree()

