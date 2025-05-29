# Documentación - BRIN (Block Range Index)

Debido a que el índice BRIN es tan simple, es posible describir los componentes internos con casi ninguna simplificación.

Los datos en las tablas PostgreSQL están organizados en el disco en "páginas" de tamaño igual. Así que una tabla residirá físicamente en el disco como una colección de páginas. Dentro de cada página, las filas se empaquetan desde el frente, con huecos que aparecen a medida que se eliminan/actualizan los datos y, por lo general, algo de espacio libre al final para futuras actualizaciones.

![Imagen_SF1](/images/brin1.png)


Debido a que cada página tiene varias filas, podemos indicar que una columna determinada en esa página tiene un valor mínimo y máximo en esa página. Al buscar un valor en particular, se puede omitir toda la página, si el valor no está dentro del mínimo/máximo de la página. Esta es la magia central de BRIN.

Por lo tanto, para que BRIN sea efectivo, necesita una tabla donde el diseño físico y el orden de la columna de interés estén fuertemente correlacionados. En una situación de correlación perfecta (que probamos a continuación) cada página contendrá de hecho un conjunto de valores completamente único.

![Imagen_SF1](/images/brin2.png)


El índice BRIN es una pequeña tabla que asocia un rango de valores con un rango de páginas en el orden de la tabla. Construir el índice solo requiere un solo escaneo de la tabla, por lo que en comparación con construir una estructura como un BTree, es muy rápido.

Debido a que el BRIN tiene una entrada para cada rango de páginas, también es muy pequeño. El número de páginas en un rango es configurable, pero el valor predeterminado es 128. Como veremos, ajustar este número puede marcar una gran diferencia en el rendimiento de la consulta.

![Imagen_SF1](/images/brin3.png)


## Estructura del Índice BRIN

1. **Nivel BRIN**:
   - Contiene resúmenes de rangos (min/max)
   - Apunta a páginas de índice
   - Se mantiene ordenado cuando es posible

2. **Nivel Páginas**:
   - Almacenan claves y punteros reales
   - Cada página cubre un rango específico
   - Se llenan secuencialmente

### 1. Nivel Superior (Índice BRIN)
- **Archivo**: `index_file.bin`
  ```python
  TAM_ENCABEZAD_BRIN = 5  # Tamaño del encabezado en bytes (cantidad de brin y  booleano de orden)
  ```
  Se guarda la cantidad de indices BRIN  y un booleano para saber si esta ordenado, la necesidad de ese booleano es determinante porque cambia entre elegir una busqueda secuencial entre los rangos del brin o hacer una busqueda binaria
- **Estructura**:
  ```python
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
  ```python
  TAM_ENCABEZAD_PAGE = 4  # Tamaño del encabezado en bytes (cantidad de pages)
  ```
  Se guarda la cantidad de paginnas para facilitar la escritura de la misma
- **Estructura**:
  ```python
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
El **índice BRIN** opera como una estructura jerárquica de dos niveles:

**Mecanismo de Inserción**:
1. Siempre se inserta en el último BRIN/página disponible
2. Cuando se llena una página, se crea nueva en el mismo BRIN
3. Cuando se llena un BRIN, se crea uno nuevo

**Mantenimiento de Orden**:
- El flag `is_ordered` permite optimizar búsquedas
- Se actualiza durante inserciones que rompen la secuencia

**Actualización de Rangos**:
- Propagación en cascada desde hojas hasta raíz
- Mantiene consistencia en los resúmenes
- Permite filtrado rápido durante búsquedas

**Pseudocódigo**:
#### Función Principal: add()
```
# Leer metadatos globales
num_brins, is_ordered = leer_encabezado_brin()

# Caso 1: Primer BRIN
SI num_brins == 0:
    RETORNAR _add_brin(key, pos_new_record)

# Caso 2: Insertar en estructura existente
brin = leer_ultimo_brin()
ultima_pagina = leer_ultima_pagina(brin)

# Subcaso 2.1: Espacio en última página
SI ultima_pagina.tiene_espacio():
    ultima_pagina.insertar(key, pos_new_record)
    escribir_pagina(ultima_pagina)
    _update_ranges(ultima_pagina, key)

# Subcaso 2.2: Nueva página en mismo BRIN
SINO SI brin.tiene_espacio_para_paginas():
    nueva_pagina = crear_pagina(key, pos_new_record, brin)
    brin.agregar_pagina(nueva_pagina)
    escribir_brin(brin)
    _update_ranges(nueva_pagina, key)

# Subcaso 2.3: Nuevo BRIN completo
SINO:
    RETORNAR _add_brin(key, pos_new_record)
```
#### Función Auxiliar: _add_brin()
Crea un nuevo índice BRIN con una página inicial.

1. Crea nuevo BRIN con rango inicial [key, key]
2. Crea página inicial conteniendo el registro
3. Establece relaciones padre-hijo
4. Verifica orden global
5. Actualiza metadatos
```
# Leer estado actual
num_brins, is_ordered = leer_encabezado_brin()

# Crear nuevo BRIN
nuevo_brin = NuevoBrin(K)
nuevo_brin.rango = [key, key]

# Crear página inicial
nueva_pagina = NuevaPagina(M)
nueva_pagina.insertar(key, pos_new_record)
nueva_pagina.rango = [key, key]
nueva_pagina.padre = num_brins

# Escribir estructuras
pos_pagina = guardar_pagina(nueva_pagina)
nuevo_brin.paginas[0] = pos_pagina
nuevo_brin.contador_paginas = 1

# Verificar orden con BRIN anterior
SI num_brins > 0:
    brin_anterior = leer_brin(num_brins-1)
    SI brin_anterior.rango[1] > key:
        is_ordered = False

# Actualizar metadatos
guardar_brin(num_brins, nuevo_brin)
actualizar_encabezado(num_brins+1, is_ordered)

RETORNAR (num_brins, pos_pagina)
```
#### Función Auxiliar: _update_ranges()
Actualiza rangos mínimos/máximos desde página hasta BRIN global.

1. Actualiza rango de la página
2. Propaga cambios al BRIN padre
3. Verifica orden entre BRINs vecinos
4. Persiste cambios
```
pagina = leer_pagina(pos_page)

# Actualizar página
SI key > pagina.rango[1]:
    pagina.rango[1] = key
SI key < pagina.rango[0]:
    pagina.rango[0] = key
    pagina.ordenada = False

# Actualizar BRIN padre
brin_padre = leer_brin(pagina.padre)
SI key > brin_padre.rango[1]:
    brin_padre.rango[1] = key
SI key < brin_padre.rango[0]:
    brin_padre.rango[0] = key
    brin_padre.ordenada = False

# Verificar orden entre BRINs
SI pagina.padre > 0:
    brin_anterior = leer_brin(pagina.padre-1)
    SI key < brin_anterior.rango[0]:
        actualizar_orden_global(False) #actualiza el bool del encabezado

# Persistir cambios
guardar_pagina(pagina)
guardar_brin(brin_padre)
```

### 2. Búsqueda Exacta (`search`)

**Optimización por Ordenamiento**:
- Aprovecha flags `is_ordered` para seleccionar algoritmos
- Reduce complejidad promedio mediante búsqueda binaria 

**Filtrado por Rangos**:
- Descarta rápidamente BRINs/páginas fuera de rango
- Minimiza accesos a disco innecesarios

**Recuperación Completa**:
- Garantiza encontrar todas las ocurrencias
- Maneja correctamente claves duplicadas

**Eficiencia en Memoria**:
- Opera por bloques (BRINs/páginas)
- Minimiza carga de datos no relevantes

**Pseudocódigo**:
#### Función Principal: search()
Busca todas las posiciones de registros que coinciden con la clave dada.

1. Filtrado por rangos BRIN para descartar bloques no relevantes
2. Búsqueda binaria cuando la estructura está ordenada
3. Búsqueda secuencial cuando no hay orden garantizado
4. Combinación de resultados de múltiples páginas/BRINs relevantes
    
```
# Inicialización
num_brins, is_ordered = leer_encabezado()
resultados = []

SI num_brins == 0:
    RETORNAR resultados  # Caso vacío

# Fase 1: Selección de BRINs relevantes
brins_relevantes = []

SI is_ordered:
    # Búsqueda binaria optimizada
    pos_inicio = binary_search_all(key)
    PARA i DESDE pos_inicio HASTA num_brins-1:
        brin = leer_brin(i)
        SI brin.range[0] <= key <= brin.range[1]:
            brins_relevantes.agregar(i)
        SI NO SI brin.range[0] > key:
            TERMINAR  # No hay más BRINs posibles
SINO:
    # Búsqueda secuencial completa
    PARA cada brin EN todos_los_brins():
        SI brin.range[0] <= key <= brin.range[1]:
            brins_relevantes.agregar(brin.pos)

# Fase 2: Búsqueda en páginas de BRINs seleccionados
PARA cada pos_brin EN brins_relevantes:
    brin = leer_brin(pos_brin)
    
    # Determinar páginas iniciales
    SI brin.is_ordered:
        pos_pagina_inicio = binary_find_index(brin, key)
    SINO:
        pos_pagina_inicio = 0
    
    # Examinar páginas candidatas
    PARA i DESDE pos_pagina_inicio HASTA brin.page_count-1:
        pagina = leer_pagina(brin.pages[i])
        
        SI pagina.range[0] <= key <= pagina.range[1]:
            # Búsqueda dentro de la página
            SI pagina.is_ordered:
                indice = pagina.binary_find_index(key)
                PARA j DESDE indice HASTA pagina.key_count-1:
                    SI pagina.keys[j] == key:
                        resultados.agregar(pagina.childrens[j])
                    SI NO SI pagina.keys[j] > key:
                        TERMINAR
            SINO:
                PARA cada (clave, posicion) EN pagina:
                    SI clave == key:
                        resultados.agregar(posicion)
        
        SI NO SI pagina.range[0] > key Y brin.is_ordered:
            TERMINAR  # No más páginas relevantes

RETORNAR resultados
```
#### Función Auxiliar: binary_search_all()
Búsqueda binaria adaptada para encontrar el primer BRIN potencialmente relevante.
- Encuentra la primera ocurrencia exacta o el último BRIN con min_val < key
- Maneja casos donde la clave podría estar entre rangos de BRINs
- Optimizado para minimizar accesos a disco
```
low = 0
high = total_brins - 1
first_occurrence = -1
floor_index = -1

MIENTRAS low <= high:
    mid = (low + high) // 2
    brin = leer_brin(mid)
    
    SI brin.min_val == key:
        first_occurrence = mid
        high = mid - 1  # Buscar primera ocurrencia
    SI NO SI brin.min_val < key:
        floor_index = mid
        low = mid + 1
    SI NO:
        high = mid - 1

RETORNAR first_occurrence SI existe SINO floor_index
```
#### Función Auxiliar: binary_find_index()
Búsqueda binaria dentro de las páginas de un BRIN individual.
- Similar a binary_search_all pero a nivel de páginas
- Considera el ordenamiento interno del BRIN
- Devuelve posición segura para inicio de búsqueda lineal
```
low = 0
high = brin.page_count - 1
first_occurrence = -1
floor_index = -1

MIENTRAS low <= high:
    mid = (low + high) // 2
    pagina = leer_pagina(brin.pages[mid])
    
    SI pagina.min_val == key:
        first_occurrence = mid
        high = mid - 1
    SI NO SI pagina.min_val < key:
        floor_index = mid
        low = mid + 1
    SI NO:
        high = mid - 1

# Manejo de casos extremos
SI no_hay_resultados_validos(first_occurrence, floor_index):
    RETORNAR 0  # Buscar desde el inicio

RETORNAR first_occurrence SI existe SINO floor_index
```

#### Diagrama de Flujo de Búsqueda

``` 
           [Inicio]
              │
              ▼
    ¿Índice vacío? ──Sí──> Retornar vacío
              │No
              ▼
    ¿BRINs ordenados? ──Sí──> Búsqueda binaria en BRINs
              │No                     │
              ▼                       ▼
    Búsqueda secuencial       Filtrado por rangos
           en BRINs                 │
              │                     ▼
              └─────> Para cada BRIN relevante:
                             │
                             ▼
                    ¿Páginas ordenadas? ──Sí──> Búsqueda binaria en páginas
                             │No                     │
                             ▼                       ▼
                    Búsqueda secuencial       Filtrado por rangos
                           en páginas               │
                             │                     ▼
                             └─────> Para cada página relevante:
                                             │
                                             ▼
                                    ¿Claves ordenadas? ──Sí──> Búsqueda binaria
                                             │No                     │
                                             ▼                       ▼
                                    Búsqueda secuencial       Agregar coincidencias
                                           en claves               │
                                             │                     ▼
                                             └─────> Recolectar resultados
                                                             │
                                                             ▼
                                                        [Retornar resultados]
```

### 3. Búsqueda por rango (`search_range`)

**Efectividad del BRIN**:
- Máxima eficiencia cuando los datos están físicamente ordenados por la clave
- Rendimiento proporcional a la selectividad del rango

**Impacto del Ordenamiento**:
- Estructuras ordenadas reducen complejidad de O(n) a O(log n)
- El flag `is_ordered` se mantiene automáticamente durante inserciones

**Costo de Acceso**:
- Minimiza accesos a disco mediante filtrado por rangos
- Ideal para tablas grandes con baja selectividad

**Pseudocódigo**:
#### Función Principal: search_range()
Busca todas las posiciones de registros cuyas claves están en el rango [key1, key2].
1. Filtrado inteligente de BRINs que intersectan con el rango
2. Búsqueda binaria cuando la estructura está ordenada
3. Búsqueda secuencial cuando no hay orden garantizado
4. Combinación de resultados de múltiples páginas/BRINs relevantes

La operación clave `max(brin.range[0], key1) <= min(brin.range[1], key2)` determina si:
1. El rango del BRIN/página se solapa con el rango de búsqueda
2. Elimina eficientemente bloques completos que no pueden contener resultados

```
# Inicialización
num_brins, is_ordered = leer_encabezado()
resultados = []

SI num_brins == 0:
    RETORNAR resultados  # Caso vacío

# Fase 1: Selección de BRINs relevantes (que intersectan con el rango)
brins_relevantes = []

SI is_ordered:
    # Búsqueda binaria optimizada para encontrar BRINs iniciales
    pos_inicio = binary_search_all(key1)
    PARA i DESDE pos_inicio HASTA num_brins-1:
        brin = leer_brin(i)
        # Verifica intersección de rangos: [max(brin.min, key1), min(brin.max, key2)]
        SI max(brin.range[0], key1) <= min(brin.range[1], key2):
            brins_relevantes.agregar(i)
        SI NO SI brin.range[0] > key2:
            TERMINAR  # No hay más BRINs posibles
SINO:
    # Búsqueda secuencial completa verificando intersección
    PARA cada brin EN todos_los_brins():
        SI max(brin.range[0], key1) <= min(brin.range[1], key2):
            brins_relevantes.agregar(brin.pos)

# Fase 2: Búsqueda en páginas de BRINs seleccionados
PARA cada pos_brin EN brins_relevantes:
    brin = leer_brin(pos_brin)
    
    # Determinar páginas iniciales (solo si está ordenado)
    SI brin.is_ordered:
        pos_pagina_inicio = binary_find_index(brin, key1)
    SINO:
        pos_pagina_inicio = 0
    
    # Examinar páginas candidatas
    PARA i DESDE pos_pagina_inicio HASTA brin.page_count-1:
        pagina = leer_pagina(brin.pages[i])
        
        # Verificar intersección de rangos
        SI max(pagina.range[0], key1) <= min(pagina.range[1], key2):
            # Búsqueda dentro de la página
            SI pagina.is_ordered:
                indice = pagina.binary_find_index(key1)
                PARA j DESDE indice HASTA pagina.key_count-1:
                    SI key1 <= pagina.keys[j] <= key2:
                        resultados.agregar(pagina.childrens[j])
                    SI NO SI pagina.keys[j] > key2:
                        TERMINAR  # No más claves en rango
            SINO:
                PARA cada (clave, posicion) EN pagina:
                    SI key1 <= clave <= key2:
                        resultados.agregar(posicion)
        
        SI NO SI pagina.range[0] > key2 Y brin.is_ordered:
            TERMINAR  # No más páginas relevantes

RETORNAR resultados
```

#### Diagrama de Flujo de Búsqueda
```
           [Inicio]
              │
              ▼
    ¿Índice vacío? ──Sí──> Retornar vacío
              │No
              ▼
    ¿BRINs ordenados? ──Sí──> Búsqueda binaria para encontrar primer BRIN con max >= key1
              │No                     │
              ▼                       ▼
    Búsqueda secuencial       Verificar intersección de rangos
           en BRINs                 │
              │                     ▼
              └─────> Para cada BRIN con intersección:
                             │
                             ▼
                    ¿Páginas ordenadas? ──Sí──> Búsqueda binaria para 1ra página con max >= key1
                             │No                     │
                             ▼                       ▼
                    Examinar todas          Verificar intersección
                      las páginas               │
                             │                     ▼
                             └─────> Para cada página con intersección:
                                             │
                                             ▼
                                    ¿Claves ordenadas? ──Sí──> Búsqueda binaria para key1
                                             │No                     │
                                             ▼                       ▼
                                    Examinar todas            Agregar claves en
                                      las claves               rango [key1, key2]
                                             │                     │
                                             └─────> Recolectar resultados
                                                             │
                                                             ▼
                                                        [Retornar resultados]
```


### 4. Eliminacion (`delete`)
Elimina registros marcando sus claves como NaN (eliminación lógica).

Flujo:
  1. Busca BRINs que puedan contener la clave (como en search())
  2. En páginas relevantes:
     - Si está ordenado: búsqueda binaria + marcado
     - Si no está ordenado: búsqueda secuencial + marcado
  3. No reorganiza la estructura 

**Pseudocódigo**:
#### Función delete()

```
SI no hay BRINs:
    RETORNAR

# Encontrar BRINs relevantes (misma lógica que search)
brins_relevantes = encontrar_brins_con_key(key)

PARA cada brin EN brins_relevantes:
    # Encontrar páginas relevantes
    paginas = encontrar_paginas_en_brin(brin, key)
    
    PARA cada pagina EN paginas:
        SI pagina.ordenada:
            # Búsqueda binaria + marcado
            indice = busqueda_binaria(pagina, key)
            marcar_claves(pagina, indice, key)
        SINO:
            # Búsqueda secuencial + marcado
            marcar_claves_secuencial(pagina, key)

RETORNAR
```

Marcado de claves:

Usa float('nan') como valor especial para claves eliminadas
No modifica punteros ni estructura, solo el valor de la clave
Las reconstrucciones periódicas limpian estos registros
