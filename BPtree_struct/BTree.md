# Documentación - B+ tree 

El árbol B+ es una variación de la estructura de datos del árbol B+. En un árbol B+, los punteros a datos se almacenan únicamente en los nodos hoja. En este árbol , la estructura de un nodo hoja difiere de la de los nodos internos. Los nodos hoja contienen una entrada para cada valor del campo de búsqueda, junto con un puntero al registro (o al bloque que contiene dicho registro). Los nodos hoja del árbol B+ están enlazados para proporcionar acceso ordenado al campo de búsqueda de los registros. Los nodos internos de un árbol B+ se utilizan para guiar la búsqueda. Algunos valores de los campos de búsqueda de los nodos hoja se repiten en los nodos internos del árbol B+.

![B](/images/BpTree.png)

## Características de los árboles B+
- **Equilibrado**: Los árboles B+ se autoequilibran, lo que significa que, al añadir o eliminar datos, este se ajusta automáticamente para mantener una estructura equilibrada. Esto garantiza que el tiempo de búsqueda se mantenga relativamente constante, independientemente del tamaño del árbol.
- **Multinivel**: Los árboles B+ son estructuras de datos multinivel, con un nodo raíz en la parte superior y uno o más niveles de nodos internos debajo. Los nodos hoja en el nivel inferior contienen los datos.
- **Ordenado**: los árboles B+ mantienen el orden de las claves en el árbol, lo que facilita la realización de consultas de rango y otras operaciones que requieren datos ordenados.
- **Abanico de salida**: Los árboles B+ tienen un abanico de salida alto, lo que significa que cada nodo puede tener varios nodos secundarios. Esto reduce la altura del árbol y aumenta la eficiencia de las operaciones de búsqueda e indexación.
- **Compatible con caché**: los árboles B+ están diseñados para ser compatibles con caché, lo que significa que pueden aprovechar los mecanismos de almacenamiento en caché en las arquitecturas informáticas modernas para mejorar el rendimiento.
- **Orientado a disco**: los árboles B+ se utilizan a menudo para sistemas de almacenamiento basados ​​en disco porque son eficientes para almacenar y recuperar datos del disco.

## Estructura del índice

El índice está estructurado de la siguiente manera:

- Archivo de datos (data_file.bin): Almacena los registros en un heap (implementado en Heap).

- Archivo de índice (index_file.bin): Contiene la estructura del árbol B+ con páginas/nodos.

```python
class IndexPage():
    def __init__(self, leaf=True, M=None):
        self.leaf = leaf      # True si es nodo hoja
        self.keys = [None] * (M-1)  # Claves de búsqueda
        self.childrens = [-1] * M   # Punteros (a registros o nodos hijos)
        self.father = -1      # Puntero al padre
        self.key_count = 0    # Número de claves actuales
        self.M = M           # Orden del árbol (máx. hijos por nodo)
```
### Tipos de Nodos:
#### Nodos Internos (no hoja):

- keys: Valores separadores para el enrutamiento

- childrens: Punteros a nodos hijos

No contienen datos reales

#### Nodos Hoja:

- keys: Claves de búsqueda

- childrens: Punteros a registros en el archivo de datos

Enlazados secuencialmente (último childrens apunta al siguiente nodo hoja)

## Algorimtmos
A continuación, se presenta los algoritmos de las operaciones:

### Inserción
Algorimto de inserción:

```

```


Funciones Auxiliares:

### Búsqueda
Algorimto de búsqueda:


Funciones Auxiliares:

### Búsqueda por rango
Algorimto de búsqueda por rango:


Funciones Auxiliares:

### Eliminación

Lamentablemente, la eliminación en la estructura demostró ser de mucha complejidad para implementarse. Entonces, se decidió obviar esta operación.

Igualmente, al momento de probar la eliminación en el frontend usando el índice se puede hacer, pero no se maneja correctamente.
