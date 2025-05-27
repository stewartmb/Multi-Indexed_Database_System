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
   - Capacidad máxima por nodo (b)
   - Mínimo de entradas por nodo (m)
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
A continuación, se presetarán los algoritmos implementados de las operaciones pedidas:

### Inserción
Algoritmo de la inserción en el R-Tree:
```
FUNCIÓN insert(record, record_pos=None):
    SI record_pos es None:
        record_pos = HEAP.insert(record)  # Insertar en Heap File
    
    coords = RT.get_key(record)  # Obtener coordenadas del registro
    point = Point(coords=coords, index=record_pos)
    
    SI árbol está vacío:
        crear_nodo_raiz(point)
    SINO:
        __insert__(root_pos, point)

```

Funciones auxiliares:

```
FUNCIÓN __insert__(u_pos, point):
    u = leer_nodo(u_pos)
    
    SI u es hoja:
        u.add_point(point)
        escribir_nodo(u)
        
        SI u.size() > b:  # Overflow
            handle_overflow(u_pos)
    SINO:
        v_pos = choose_subtree(u, point)  # Elegir subárbol
        __insert__(v_pos, point)
        actualizar_mbr_padres(u_pos)  # Ajustar MBRs hacia arriba
```

Algoritmo para realizar el split:
```
FUNCIÓN handle_overflow(u_pos):
    u = leer_nodo(u_pos)
    grupo1, grupo2 = split(u)  # Split cuadrático
    
    SI u es raíz:
        crear_nueva_raiz(grupo1, grupo2)
    SINO:
        padre = leer_nodo(u.parent)
        padre.eliminar(u)
        padre.add_rectangle(grupo1)
        padre.add_rectangle(grupo2)
        
        SI padre.size() > b:
            handle_overflow(padre.pos)  # Propagación

```

### Búsqueda

Algoritmo de búsqueda:

```
FUNCIÓN search(query_coords):
    point = Point(coords=query_coords)
    resultados = []
    __search__(root_pos, point, resultados)
    RETORNAR resultados

```

Funciones auxiliares:

```
FUNCIÓN __search__(u_pos, point, resultados):
    u = leer_nodo(u_pos)
    
    SI u es hoja:
        PARA cada p en u.points:
            SI p.coords == point.coords:
                resultados.append(p.index)
    SINO:
        PARA cada rect_pos en u.rectangles:
            rect = leer_nodo(rect_pos)
            SI point está dentro de rect.mbr:
                __search__(rect_pos, point, resultados)

```

### Búsqueda por Rango

Algoritmo de búsqueda por rango:

```
FUNCIÓN range_search(min_coords, max_coords):
    resultados = []
    __range_search__(root_pos, min_coords, max_coords, resultados)
    RETORNAR resultados

```
Funciones auxiliares:

```

FUNCIÓN __range_search__(u_pos, min_coords, max_coords, resultados):
    u = leer_nodo(u_pos)
    
    SI u es hoja:
        PARA cada p en u.points:
            SI p está dentro de [min_coords, max_coords]:
                resultados.append(p.index)
    SINO:
        PARA cada rect_pos en u.rectangles:
            rect = leer_nodo(rect_pos)
            SI rect.mbr intersecta con [min_coords, max_coords]:
                __range_search__(rect_pos, min_coords, max_coords, resultados)

```

### K-NN

Algoritmo de la búsqueda K-NN:

```
FUNCIÓN ksearch(k, query_coords):
    point = Point(coords=query_coords)
    max_heap = []  # Heap de máximos (para mantener los k más cercanos)
    __ksearch__(root_pos, k, point, max_heap)
    
    # Ordenar resultados de menor a mayor distancia
    resultados_ordenados = ordenar(max_heap, key=lambda x: -x[0])
    RETORNAR [p.index for (dist, p) in resultados_ordenados]


```
Funciones auxiliares:

```
FUNCIÓN __ksearch__(u_pos, k, point, max_heap):
    u = leer_nodo(u_pos)
    
    SI u es hoja:
        PARA cada p en u.points:
            dist = distancia(p, point)
            SI len(max_heap) < k:
                heapq.heappush(max_heap, (-dist, p))  # Uso negativo para max-heap
            SINO SI dist < -max_heap[0][0]:
                heapq.heappushpop(max_heap, (-dist, p))
    SINO:
        # Ordenar hijos por mindist (distancia mínima entre point y MBR)
        hijos_ordenados = ordenar(u.rectangles, key=lambda rect_pos: mindist(point, rect.mbr))
        
        PARA cada rect_pos en hijos_ordenados:
            rect = leer_nodo(rect_pos)
            SI len(max_heap) < k O mindist(point, rect.mbr) < -max_heap[0][0]:
                __ksearch__(rect_pos, k, point, max_heap)

```



### Eliminación
Algoritmo de eliminación:

```
FUNCIÓN delete(record_pos):
    point = Point(coords=obtener_coords_desde_heap(record_pos), index=record_pos)
    aux_delete(record_pos, point)

```
Funciones auxiliares:

```
FUNCIÓN aux_delete(record_pos, point):
    # Buscar nodo hoja que contiene el punto
    u_pos = find_rec(root_pos, point)
    SI u_pos == -1:
        RETORNAR  # Punto no existe
    
    u = leer_nodo(u_pos)
    u.remove_exact(point)  # Eliminación lógica
    escribir_nodo(u)
    
    SI u.size() < m:  # Underflow
        condense_tree(u_pos)
    
    # Reorganizar raíz si es necesario
    SI raíz tiene solo 1 hijo y no es hoja:
        reemplazar_raíz_con_hijo()
```

```
FUNCIÓN condense_tree(u_pos):
    nodos_eliminados = []
    
    MIENTRAS u_pos no sea raíz:
        padre = leer_nodo(u.parent)
        SI u.size() < m:
            padre.remove(u)
            nodos_eliminados += obtener_puntos_desde_subárbol(u_pos)
            marcar_nodo_como_eliminado(u)
        
        u_pos = u.parent
    
    # Reinsertar puntos de nodos eliminados
    PARA cada p en nodos_eliminados:
        aux_insert(p)
```

## Complejidad en acceso a memoria secundaria
| Operación         | Mejor Caso       | Peor Caso         | Escenario Crítico                          |
|-------------------|------------------|-------------------|--------------------------------------------|
| **Inserción**     | `O(log N)`       | `O(N)`            | Splits propagados hasta la raíz            |
| **Búsqueda**      | `O(log N)`       | `O(N)`            | MBRs altamente solapados                   |
| **Rango**         | `O(log N + K)`   | `O(N)`            | K resultados válidos con MBRs solapados    |
| **k-NN**          | `O(log N + k)`   | `O(N)`            | Datos mal distribuidos (k vecinos lejanos) |
| **Eliminación**   | `O(log N)`       | `O(N)`            | Underflow con múltiples re-inserciones     |

**Leyenda**:
- `N`: Número total de registros  
- `K`: Resultados en rango de consulta  
- `k`: Vecinos más cercanos solicitados  
- `MBR`: Minimum Bounding Rectangle
