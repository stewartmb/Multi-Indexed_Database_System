# Documentación - BRIN (Block Range Index)

## Estructura del Índice BRIN

El índice BRIN implementado sigue una estructura jerárquica de dos niveles:

### 1. Nivel Superior (Índice BRIN)
- **Archivo**: `index_file.bin`
- **Estructura**:
  ```c
  struct BrinIndex {
      Key min_val;      // Valor mínimo del rango
      Key max_val;      // Valor máximo del rango
      int pages[K];     // Array de posiciones de páginas (K = max_num_pages)
      int page_count;   // Número de páginas actuales
      bool is_order;    // Indica si el BRIN está ordenado
  };
  ```

### 2. Nivel Inferior (Páginas de Índice)
- **Archivo**: `page_file.bin`
- **Estructura**:
  ```c
  struct IndexPage {
      Key keys[M];      // Array de claves (M = max_num_keys)
      int children[M];  // Array de posiciones en heap file
      Key range_min;    // Mínimo del rango en la página
      Key range_max;    // Máximo del rango en la página
      int key_count;    // Número de claves actuales
      bool is_order;    // Indica si la página está ordenada
      int father_brin;  // Posición del BRIN padre
  };
  ```

### 3. Almacenamiento de Datos
- **Archivo**: `data_file.bin` (Heap File)
- Almacena los registros completos con acceso directo mediante posiciones

## Operaciones Principales

### 1. Inserción (`add`)
**Flujo**:
1. Inserta el registro en el Heap File
2. Obtiene la clave y posición del nuevo registro
3. Busca el último BRIN y última página
4. Si hay espacio, inserta en la página existente
5. Si no hay espacio, crea nueva página o nuevo BRIN según corresponda
6. Actualiza rangos mínimos/máximos en toda la jerarquía

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
