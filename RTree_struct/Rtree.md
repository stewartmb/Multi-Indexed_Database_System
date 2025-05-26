# Documentación - R Tree
## Índices espaciales
Un índice espacial es una estructura de datos que permite realizar consultas eficientes sobre datos espaciales (geográficos).
Permite búsquedas como:
- Puntos dentro de un área
- Objetos que se intersectan
- Encontrar los vecinos más cercanos (K-NN).

## ¿Qué es un índice R-Tree?
El R-Tree es un índice espacial jerárquico que organiza objetos geométricos (puntos, líneas, polígonos) mediante rectángulos mínimos (MBR) para facilitar búsquedas espaciales eficientes.
- Cada rectángulo representa un nodo o entrada en el árbol.
- Los nodos internos agrupan elementos espacialmente cercanos para mejorar la eficiencia de búsqueda.

El R-Tree tiene más características:
- Es un árbol balanceado similar a un B-Tree.
- Garantiza que puntos cercanos se almacenen en lo posible en la misma página de datos o subárbol.
- Regiones de páginas jerárquicamente organizadas siempre deben estar contenidas completamente en la región de su padre.
- Estructura dinámica: operaciones de inserción y borrado eficientes O(log n)
- Permite buscar objetos espaciales en una área determinada.

![rtree_imagen1](/images/rtree.png)

## MBR
Un MBR (Minimum Bounding Rectangle) es el rectángulo de menor área que encierra completamente un objeto geométrico en un espacio multidimensional (2D, 3D, etc.). Es una aproximación simplificada que permite operaciones espaciales eficientes. EL MBR esta definido por las coordenadas de dos puntos en esquinas opuestas: (x_min, y_min) (inferior izquierdo) y (x_max, y_max) (superior derecho).

Entonces, en los nodos internos del R-Tree, se almacenan MBRs que agrupan los MBRs de sus hijos. Para los nodos hoja,  se contienen referencias a objetos espaciales junto con su MBR.

## ¿Que hacer cuando un nodo se llena?
Para un MBR, tiene una cantidad máxima de puntos que puede soportar. Una vez se pase ese umbral, el MBR se debe partir en dos; y a partir de dos puntos del MBR original se crean los nuevos MBRs. A esta técnica se le conoce como split y tiene 3 tipos:
- Split cuadrático
- Split lineal
- Split optimizado
Para la implementación del proyecto, se ha optado por usar el split cuadrático.

## Estructura del índice
La estructura del índice R-tree es la siguiente:
### Archivo de índice:
El archivo de índices tiene la siguiente estructura:
- **Header**: Metadatos globales. Contiene:
   - Posición del nodo raíz
   - Cantidad total de rectángulos
   - Capacidad máxima por nodo
   - Mínimo de entradas por nodo
   - Dimensión del espacio
   - Formato binario de los puntos
   - Formato binario de los MBRs
   - Formato binario de los rectángulos
    
- **Nodos**: Rectángulos (hojas o internos) almacenados como estructuras binarias. Contiene:
   - Posición en el archivo
   - Booleano: True si es nodo hoja, false c.c.
   - Posición del padre (-1 si es raíz)
   - Marca de eliminación lógica (1 si está eliminado)
   - Posiciones de hijos (nodos internos)
   - Puntos (nodos hoja)
   - MBR que cubre todos sus hijos/puntos
### Archivo de datos:

Heap File que almacena los registros completos (no ordenados).

### Estrcuturas clave:

- **Point**: Representa un punto multidimensional con coordenadas y referencia al registro en el Heap File.

- **MBR (Minimum Bounding Rectangle)**: Rectángulo que envuelve puntos u otros MBRs.

- **Rectangle**: Nodos del R-Tree (hojas o internos), que contienen puntos u otros rectángulos.


## Algoritmo de las operaciones

### Inserción

### Búsqueda

### Búsqueda por Rango

### K-NN

### Eliminación

## Complejidad en acceso a memoria secundaria

