class BTreeNode:
    def __init__(self, t, is_leaf):
        self.t = t            # Grado mínimo (t >= 2)
        self.is_leaf = is_leaf
        self.keys = []        # Entre t-1 y 2t-1 claves
        self.children = []    # Entre t y 2t hijos

class BTree:
    def __init__(self, t):
        self.root = BTreeNode(t, True)
        self.t = t
    
    def insert(self, key):
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_root = BTreeNode(self.t, False)
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_non_full(new_root, key)
        else:
            self._insert_non_full(root, key)
    
    def _insert_non_full(self, node, key):
        i = len(node.keys) - 1
        if node.is_leaf:
            node.keys.append(key)
            node.keys.sort()
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == 2 * self.t - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key)
    
    def _split_child(self, parent, child_idx):
        child = parent.children[child_idx]
        new_node = BTreeNode(self.t, child.is_leaf)
        
        split_pos = self.t - 1  # Posición correcta de división
        middle_key = child.keys[split_pos]
        
        new_node.keys = child.keys[split_pos + 1:]
        child.keys = child.keys[:split_pos]
        
        if not child.is_leaf:
            new_node.children = child.children[split_pos + 1:]
            child.children = child.children[:split_pos + 1]
        
        parent.keys.insert(child_idx, middle_key)
        parent.children.insert(child_idx + 1, new_node)
    
    def print_level_order(self):
        if not self.root.keys:
            print("Árbol vacío")
            return
        
        queue = [self.root]
        while queue:
            current_level = []
            next_level = []
            
            for node in queue:
                current_level.append(str(node.keys))
                if not node.is_leaf:
                    next_level.extend(node.children)
            
            print("Nivel:", " | ".join(current_level))
            queue = next_level

# Ejemplo con grado mínimo t=2 (B-Tree 2-3-4)
btree = BTree(2)
keys = [5, 7, 9, 6, 12, 13, 15, 18]

print("Inserción correcta en B-Tree (t=2):")
for key in keys:
    print(f"\nInsertando {key}:")
    btree.insert(key)
    btree.print_level_order()