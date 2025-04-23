class Node(object):
    def __init__(self, order):
        # Inicializa un nodo vacío. Puede ser hoja o interno.
        self.order = order           # Máximo número de claves por nodo
        self.keys = []               # Lista de claves
        self.values = []             # En hojas: listas de valores. En nodos internos: hijos
        self.leaf = True             # Indica si es una hoja

    def add(self, key, value):
        # Agrega un par clave-valor a un nodo hoja (manteniendo orden)
        if not self.keys:
            # Si está vacío, simplemente lo agrega
            self.keys.append(key)
            self.values.append([value])
            return None

        for i, item in enumerate(self.keys):
            if key == item:
                # Si la clave ya existe, agrega el valor a la lista de valores
                self.values[i].append(value)
                break
            elif key < item:
                # Inserta en la posición correcta para mantener orden
                self.keys = self.keys[:i] + [key] + self.keys[i:]
                self.values = self.values[:i] + [[value]] + self.values[i:]
                break
            elif i + 1 == len(self.keys):
                # Si es mayor que todas, lo agrega al final
                self.keys.append(key)
                self.values.append([value])

    def split(self):
        # Divide un nodo en dos cuando se llena
        left = Node(self.order)   # Nodo izquierdo
        right = Node(self.order)  # Nodo derecho
        mid = self.order // 2     # Punto medio

        # Divide claves y valores entre los dos nodos
        left.keys = self.keys[:mid]
        left.values = self.values[:mid]
        right.keys = self.keys[mid:]
        right.values = self.values[mid:]

        # El nodo actual se convierte en nodo interno con dos hijos
        self.keys = [right.keys[0]]  # Promueve la primera clave del derecho
        self.values = [left, right]  # Hijos izquierdo y derecho
        self.leaf = False

    def is_full(self):
        # Retorna True si el nodo alcanzó su capacidad máxima
        return len(self.keys) == self.order

    def show(self, counter=0):
        # Imprime el árbol en formato jerárquico (por nivel)
        print(counter, str(self.keys))
        if not self.leaf:
            for item in self.values:
                item.show(counter + 1)


class BPlusTree(object):
    def __init__(self, order=4):
        # Inicializa el árbol con una raíz que es hoja vacía
        self.root = Node(order)

    def _find(self, node, key):
        # Encuentra el hijo por el cual continuar la búsqueda
        for i, item in enumerate(node.keys):
            if key < item:
                return node.values[i], i  # Devuelve hijo izquierdo
        return node.values[i + 1], i + 1  # Devuelve hijo derecho al final

    def _merge(self, parent, child, index):
        # Cuando un nodo hoja se divide, se reestructura el árbol
        parent.values.pop(index)     # Elimina hijo antiguo (ahora dividido)
        pivot = child.keys[0]        # Clave a promover

        for i, item in enumerate(parent.keys):
            if pivot < item:
                # Inserta la clave y los dos nuevos hijos en el padre
                parent.keys = parent.keys[:i] + [pivot] + parent.keys[i:]
                parent.values = parent.values[:i] + child.values + parent.values[i:]
                break
            elif i + 1 == len(parent.keys):
                # Si es mayor que todas, lo agrega al final
                parent.keys += [pivot]
                parent.values += child.values
                break

    def insert(self, key, value):
        # Inserta un nuevo par clave-valor
        parent = None
        child = self.root

        # Baja hasta una hoja
        while not child.leaf:
            parent = child
            child, index = self._find(child, key)

        # Agrega el dato en la hoja
        child.add(key, value)

        # Si se llenó, hay que dividirla
        if child.is_full():
            child.split()
            # Si hay padre, se hace el merge (reorganización)
            if parent and not parent.is_full():
                self._merge(parent, child, index)

    def retrieve(self, key):
        # Busca y retorna los valores asociados a una clave
        child = self.root
        while not child.leaf:
            child, index = self._find(child, key)

        for i, item in enumerate(child.keys):
            if key == item:
                return child.values[i]
        return None  # No se encontró

    def show(self):
        # Muestra visualmente el contenido del árbol
        self.root.show()


# DEMOSTRACIONES

def demo_node():
    print('Inicializando nodo...')
    node = Node(order=4)

    print('\nInsertando clave a...')
    node.add('a', 'alpha')
    print('¿Nodo lleno?', node.is_full())
    node.show()

    print('\nInsertando claves b, c, d...')
    node.add('b', 'bravo')
    node.add('c', 'charlie')
    node.add('d', 'delta')
    print('¿Nodo lleno?', node.is_full())
    node.show()

    print('\nDividiendo nodo...')
    node.split()
    node.show()

def demo_bplustree():
    print('Inicializando árbol B+...')
    bplustree = BPlusTree(order=4)

    print('\nÁrbol con 1 elemento...')
    bplustree.insert('a', 'alpha')
    bplustree.show()

    print('\nÁrbol con 2 elementos...')
    bplustree.insert('b', 'bravo')
    bplustree.show()

    print('\nÁrbol con 3 elementos...')
    bplustree.insert('c', 'charlie')
    bplustree.show()

    print('\nÁrbol con 4 elementos...')
    bplustree.insert('d', 'delta')
    bplustree.show()

    print('\nÁrbol con 5 elementos...')
    bplustree.insert('e', 'echo')
    bplustree.show()

    print('\nÁrbol con 6 elementos...')
    bplustree.insert('f', 'foxtrot')
    bplustree.show()

    print('\nBuscando valores con clave e...')
    print(bplustree.retrieve('e'))

if __name__ == '__main__':
    demo_node()
    print('\n')
    demo_bplustree()

    bplus = BPlusTree(order=4)
    bplus.insert('1', '1')
    bplus.insert('2', '2')
    bplus.insert('3', '3')
    bplus.insert('4', '4')
    bplus.insert('5', '5')
    bplus.insert('6', '6')
    bplus.insert('7', '7')
    bplus.insert('8', '8')
    bplus.insert('9', '9')
    bplus.insert('97', '97')
    bplus.insert('99', '99')
    bplus.insert('98', '98')


    bplus.show()


