# Documentación - BRIN (Block Range Index)

Debido a que el índice BRIN es tan simple, es posible describir los componentes internos con casi ninguna simplificación.

Los datos en las tablas PostgreSQL están organizados en el disco en "páginas" de tamaño igual de 8kb cada una. Así que una tabla residirá físicamente en el disco como una colección de páginas. Dentro de cada página, las filas se empaquetan desde el frente, con huecos que aparecen a medida que se eliminan/actualizan los datos y, por lo general, algo de espacio libre al final para futuras actualizaciones.

![Imagen_SF1](/images/brin1.png)


Una tabla con filas estrechas (pocas columnas, valores pequeños) encajará muchas filas en una página. Una tabla con filas anchas (más columnas, cadenas largas) solo cabrán unas pocas.

Debido a que cada página tiene varias filas, podemos indicar que una columna determinada en esa página tiene un valor mínimo y máximo en esa página. Al buscar un valor en particular, se puede omitir toda la página, si el valor no está dentro del mínimo/máximo de la página. Esta es la magia central de BRIN.

Por lo tanto, para que BRIN sea efectivo, necesita una tabla donde el diseño físico y el orden de la columna de interés estén fuertemente correlacionados. En una situación de correlación perfecta (que probamos a continuación) cada página contendrá de hecho un conjunto de valores completamente único.

![Imagen_SF1](/images/brin2.png)


El índice BRIN es una pequeña tabla que asocia un rango de valores con un rango de páginas en el orden de la tabla. Construir el índice solo requiere un solo escaneo de la tabla, por lo que en comparación con construir una estructura como un BTree, es muy rápido.

Debido a que el BRIN tiene una entrada para cada rango de páginas, también es muy pequeño. El número de páginas en un rango es configurable, pero el valor predeterminado es 128. Como veremos, ajustar este número puede marcar una gran diferencia en el rendimiento de la consulta.

![Imagen_SF1](/images/brin3.png)


## Estructura del Índice BRIN

El índice BRIN implementado sigue una estructura jerárquica de dos niveles:

### 1. Nivel Superior (Índice BRIN)
- **Archivo**: `index_file.bin`
  ```c
  TAM_ENCABEZAD_BRIN = 5  # Tamaño del encabezado en bytes (cantidad de brin y  booleano de orden)
  ```
  Se guarda la cantidad de indices BRIN  y un booleano para saber si esta ordenado, la necesidad de ese booleano es determinante porque cambia entre elegir una busqueda secuencial entre los rangos del brin o hacer una busqueda binaria
- **Estructura**:
  ```c
  class Indice_Brin():
      def __init__(self, K):
          self.range_values = [None,None]                      # Valor mínimo y máximo de la página (formato: formato_key)
          self.pages = [-1] * K                                # Lista de posiciones de las páginas, inicialmente todas son -1 (no hay páginas)
          self.page_count = 0                                  # Contador de páginas
          self.is_order = True                                 # Indica si el índice BRIN está ordenado
          self.K = K                                           # Número máximo de páginas por índice BRIN
  ```

### 2. Nivel Inferior (Páginas de Índice)
las paginas se conforman por una lista de keys (clave de ordenamiento del registro) y childrens (posicion del registro en el data_file) 
- **Archivo**: `page_file.bin`
  ```c
  TAM_ENCABEZAD_PAGE = 4  # Tamaño del encabezado en bytes (cantidad de pages)
  ```
  Se guarda la cantidad de paginnas para facilitar la escritura de la misma
- **Estructura**:
  ```c
  class Index_Page():
      def __init__(self, M=None):
          self.keys = [None] * (M)                # Lista de claves, inicialmente todas son None
          self.childrens = [-1] * M               # Lista de posiciones, inicialmente todas son -1 (no hay registros)
          self.range_values = [None, None]        # Valores mínimo y máximo de la página
          self.key_count = 0                      # Contador de claves
          self.is_order = True                    # Indica si la página está ordenada
          self.father_brin = -1                   # Posición del padre, inicialmente -1 (sin padre)
          self.M = M                              # Número máximo de claves por página
    };
  ```

### 3. Almacenamiento de Datos
- **Archivo**: `data_file.bin` (Heap File)
- Almacena los registros completos con acceso directo mediante posiciones, al igual q los demas indices 

## Operaciones Principales

### 1. Inserción (`add`)
**Flujo**:
1. Inserta el registro en el Heap File
2. Obtiene la clave y posición del nuevo registro
3. Busca el último BRIN y última página
4. Si hay espacio, inserta en la página existente
5. Si no hay espacio, crea nueva página o nuevo BRIN según corresponda
6. Actualiza rangos mínimos/máximos en toda la jerarquía
7. Actualiza si lo ordenes se respetan

**Pseudocódigo**:
```python
def add(record):
    pos = heap.insert(record)
    key = get_key(record)
    
    if no_hay_brins():
        crear_nuevo_brin(key, pos)
        return
    
    brin = ultimo_brin()
    pagina = ultima_pagina(brin)
    
    if pagina.tiene_espacio():
        pagina.insertar(key, pos)
        actualizar_rangos(pagina, key)
    else:
        if brin.tiene_espacio():
            nueva_pagina = crear_pagina(key, pos, brin)
            brin.agregar_pagina(nueva_pagina)
            actualizar_rangos(nueva_pagina, key)
        else:
            nuevo_brin = crear_brin(key, pos)
```

### 2. Búsqueda Exacta (`search`)
**Estrategia**:
1. Búsqueda binaria en BRINs para encontrar rangos relevantes
2. Búsqueda binaria en páginas de cada BRIN relevante
3. Recuperación de posiciones coincidentes

**Complejidad**: O(log B + log P + K), donde:
- B = número de BRINs
- P = páginas por BRIN
- K = registros por página

### 3. Búsqueda por Rango (`search_range`)
**Optimizaciones**:
- Aprovecha el orden de los BRINs y páginas para saltar rangos no relevantes
- Usa búsqueda binaria para encontrar límites inferiores
- Combina resultados de múltiples páginas solapadas

### 4. Eliminación (`delete`)
**Implementación**:
- Marcado lógico (no físico) de registros eliminados
- Usa valores especiales (NaN para floats, -2³¹ para enteros) para marcar eliminados
- Las reconstrucciones periódicas limpian los eliminados

## Mantenimiento Automático

### Reconstrucción Parcial
- Se dispara automáticamente cuando:
  - Se detecta desorden significativo
  - Se alcanzan límites de capacidad
- Reorganiza páginas y BRINs manteniendo el orden

### Actualización de Rangos
- Propagación automática de cambios en mínimos/máximos:
  ```python
  def actualizar_rangos(pagina, key):
      # Actualiza página
      pagina.min = min(pagina.min, key)
      pagina.max = max(pagina.max, key)
      
      # Actualiza BRIN padre
      brin = obtener_brin(pagina.father_brin)
      brin.min = min(brin.min, key)
      brin.max = max(brin.max, key)
      
      # Verifica orden global
      if key < brin_anterior.max:
          marcar_desordenado()
  ```

## Formatos de Archivo

### 1. BRIN Index File
```
[Encabezado]
  int: número total de BRINs
  bool: índice ordenado

[BRINs]
  Repetido para cada BRIN:
    Key: min_val
    Key: max_val
    int[K]: array de posiciones de páginas
    int: page_count
    bool: is_order
```

### 2. Page File
```
[Encabezado]
  int: número total de páginas

[Páginas]
  Repetido para cada página:
    Key[M]: array de claves
    int[M]: array de posiciones
    Key: range_min
    Key: range_max
    int: key_count
    bool: is_order
    int: father_brin
```

## Ventajas de la Implementación

1. **Compactabilidad**: Ocupa ~1% del espacio de los datos originales
2. **Eficiencia en Datos Ordenados**: 
   - Búsqueda por rango en O(log n)
   - Inserciones rápidas en modo append-only

3. **Auto-optimización**:
   - Detecta automáticamente patrones de acceso
   - Reorganiza estructura según necesidad

4. **Tolerancia a Desorden**:
   - Funciona bien incluso con cierta desorganización
   - Reconstrucciones parciales mantienen rendimiento

## Ejemplo de Uso

```python
# Crear índice BRIN para tabla de ventas
brin = BRIN(
    table_format={'date': 's10', 'amount': 'f'},
    name_key='date',
    max_num_pages=30,
    max_num_keys=40
)

# Insertar registros
brin.add({'date': '2023-01-01', 'amount': 100.0})
brin.add({'date': '2023-01-02', 'amount': 150.0})

# Búsqueda exacta
results = brin.search('2023-01-01')

# Búsqueda por rango
results = brin.search_range('2023-01-01', '2023-01-31')

# Eliminación
brin.delete('2023-01-01')
```

Esta implementación está especialmente optimizada para:
- Datos con alta correlación física (ej: series temporales)
- Escenarios con limitaciones de memoria
- Cargas de trabajo con predominio de lecturas sobre escrituras
