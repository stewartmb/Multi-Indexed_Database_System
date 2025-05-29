# Documentación - Hash File
## ¿Qué es un Hash File?
Las técnicas de hash se utilizan para recuperar datos específicos. Buscar entre todos los valores de índice para encontrar los datos deseados resulta muy ineficiente. En este caso, podemos usar el hash como una técnica eficiente para localizar los datos deseados directamente en el disco sin usar una estructura de índice.
La configuración de archivo hash también se conoce como configuración directa de archivo.

La organización de archivos hash puede ser una estrategia para almacenar y acceder a información en un registro utilizando un trabajo hash para calcular la dirección de la información dentro del registro.

Esto permite una rápida recuperación de información basada en una clave.

En Hashing nos referimos principalmente a los siguientes términos:

- **Bucket de datos**: Un bucket de datos es una ubicación de almacenamiento donde se almacenan registros. Estos cubos también se consideran unidades de almacenamiento.
- **Función hash**: Una función hash es una función de mapeo que asigna todas las claves de búsqueda a las direcciones de registro reales. Generalmente, una función hash utiliza una clave principal para generar un índice hash (dirección de un bloque de datos). Las funciones hash varían desde funciones matemáticas simples hasta complejas.
- **Índice hash**: El prefijo del valor hash completo se utiliza como índice hash. Cada índice hash tiene un valor de profundidad que indica el número de bits utilizados para calcular la función hash.

Ejemplo de índice hash:

![Imagen_hash](/images/hash1.png)

## Extendible Hahsing
Para el proyecto, se ha decido implementar el Extendible Hashing. A diferencia de un hash tradicional, es un tipo de hash **dinámico** para gestionar base de datos que crecen y reducen su tamaño en el tiempo (transaccionales).

La función hash de esta estructura tiene la caraterística de que genera una secuencia de bits (secuencia binaria). En cualquier momento, solo se usa un prefijo/sufijo del binario para indexar los registros en una tabla de direcciones de buckets.

Ejemplo de extendible hash:

![Imagen_hash2](/images/hash2.png)

Un extendible hash se compone de:
- **Directorio**: Tabla que almacena punteros a buckets. Su tamaño es 2^D (donde D = profundidad global). La profundidad global es el número de bits utilizados por el directorio para indexar los buckets.
- **Buckets**: Contenedores que almacenan registros. Cada bucket tiene una profundidad local (d). La profundidad local es el número de bits usados por un bucket específico para determinar qué registros almacena.
- **Función de Hash**: Se usan los D bits más significativos para indexar el directorio.


## Representación usando un árbol
La implementación de la estructura se ha decidido que, en vez de hacer una tabla plana, el directorio estará organizado como un árbol. Este enfoque ha sudo basado en un laboratorio que se tuvo en clase. 

![Imagen_hash3](/images/hash3.png)

Con este enfoque, el directorio se divide en dos:
- Nodos Internos (Internal Directory Nodes): Contienen decisiones de enrutamiento basadas en bits del hash.
- Nodos Hoja (Leaf Directory Nodes): Apuntan directamente a los buckets que almacenan registros.


## Estructura del índice:
El índice implementado se divide en tres partes:

### Archivo de índice
El archivo de índices tiene dos partes:
- **Header**: 	Metadatos globales. Contiene:
  - Profundidad global del árbol
  - Última posición usada en Heap File
  - Última posición usada en buckets_file
  - Última posición usada para nodos del árbol
- **Árbol de directorios**: Estructura jerárquica que guía la búsqueda usando bits del hash. Contiene:
  - Puntero al bucket (-1 si es nodo interno)
  - Índice del hijo izquierdo
  - Índice del hijo derecho
  - Profundidad del nodo en el árbol
  
### Archivo de buckets 
El archivo de buckets contiene los buckets que almacenan referencias a registros en el Heap File.	
Además, tiene:
- Posiciones en Heap File (-1 = vacío)
- Profundidad local del bucket
- Cantidad de registros almacenados
- Puntero a bucket de overflow (-1 = no hay)

### Archivo de datos
Almacena los registros completos en formato no ordenado usando el Heap File.

## Algoritmos de las operaciones
A continuación, se presentará el algoritmo implementado para cada una de las operaciones.
### Inserción
Algoritmo de inserción de un elemento:
```
FUNCIÓN insert(record, data_position=None):
    SI data_position es None:
        data_position = HEAP.insert(record)  # Insertar en Heap File
    
    index_hash = get_bits(clave_del_registro, global_depth)
    
    ABRIR archivos (index_file, buckets_file) EN MODO lectura/escritura:
        _add_to_hash(buckets_file, index_file, data_position, index_hash)
```
Se implementaron funciones auxiliares para realizar la inserción:

Algoritmo para añadir una posición al directorio. Realiza split en caso un bucket ya esté lleno.
```
FUNCIÓN _add_to_hash(buckets_file, index_file, data_position, index_hash):
    # Navegar por el árbol
    node_index = 0
    k = 1
    MIENTRAS True:
        node = leer_nodo(index_file, node_index)
        SI node.bucket_position != -1:
            DETENER
        SI index_hash[-k] == '0':
            node_index = node.left
        SI NO:
            node_index = node.right
        k += 1
    
    # Intentar inserción en bucket
    inserted = _insert_value_in_bucket(buckets_file, index_file, node.bucket_position, data_position)
    
    SI NO inserted:  # Bucket lleno y necesita split
        old_bucket = leer_bucket(buckets_file, node.bucket_position)
        
        # Crear nuevos buckets
        bucket_left_pos = node.bucket_position
        bucket_right_pos = reservar_nuevo_bucket()
        
        # Actualizar árbol
        nuevo_nodo_padre = crear_nodo_interno()
        nuevo_nodo_izq = crear_nodo_hoja(bucket_left_pos)
        nuevo_nodo_der = crear_nodo_hoja(bucket_right_pos)
        
        # Reinsertar registros del bucket viejo
        PARA cada registro en old_bucket:
            _aux_insert(registro)
        
        # Reinsertar el nuevo registro
        _aux_insert(nuevo_registro)
```

Algoritmo para insertar un registro dentro de un bucket. Devuelve un booleano para ver si es que se realizó la operación.
```
FUNCIÓN _insert_value_in_bucket(buckets_file, index_file, bucket_position, data_position):
    bucket = leer_bucket(buckets_file, bucket_position)
    
    SI bucket no está lleno:
        agregar data_position al bucket
        actualizar_bucket(buckets_file, bucket)
    SI NO:
        SI bucket.local_depth < global_depth:
            RETORNAR False  # Trigger split
        SI NO:
            SI no tiene overflow:
                crear_nuevo_bucket_overflow()
            insertar_en_overflow(buckets_file, index_file, bucket.overflow_position, data_position)
    RETORNAR True
```
### Búsqueda
Algoritmo de búsqueda de un elemento específico:
```
FUNCIÓN search(key):
    key = convertir_a_tipo_correcto(key)
    index_hash = get_bits(key, global_depth)
    
    ABRIR archivos (index_file, buckets_file) EN MODO lectura:
        root = leer_nodo(index_file, 0)
        SI index_hash[-1] == '0':
            RETORNAR _aux_search(buckets_file, index_file, root.left, index_hash[:-1], key)
        SI NO:
            RETORNAR _aux_search(buckets_file, index_file, root.right, index_hash[:-1], key)

```

Funciones auxiliares:

Algoritmo recursivo de búsqueda:
```
FUNCIÓN _aux_search(buckets_file, index_file, node_index, index_hash, key):
    node = leer_nodo(index_file, node_index)
    
    SI node es nodo_interno:
        SI index_hash[-1] == '0':
            RETORNAR _aux_search(buckets_file, index_file, node.left, index_hash[:-1], key)
        SI NO:
            RETORNAR _aux_search(buckets_file, index_file, node.right, index_hash[:-1], key)
    SI NO:  # Es nodo hoja
        bucket = leer_bucket(buckets_file, node.bucket_position)
        matches = buscar_en_bucket(bucket, key)
        
        # Buscar en overflow chain
        MIENTRAS bucket.overflow_position != -1:
            bucket = leer_bucket(buckets_file, bucket.overflow_position)
            matches += buscar_en_bucket(bucket, key)
        
```
Algoritmo para buscar una llave en un bucket. Puede retornar varias si existen muchas colisiones:
```

FUNCIÓN buscar_en_bucket(bucket, key):
    matches = []
    PARA cada posición_en_heap en bucket.records:
        SI posición_en_heap != -1:
            record = HEAP.read(posición_en_heap)
            SI record.clave == key:
                matches.append(posición_en_heap)
    RETORNAR matches
```

### Búsqueda por rango

Como se sabe, las técnicas de hashing no sorpotan por defecto la búsqueda por rango. Por lo que para este algoritmo, se hace una búsqueda recorriendo todos los bucekts que se encuentren en el hash.

Algoritmo para la búsqueda por rango:

```
FUNCIÓN range_search(lower, upper):
    ABRIR archivos (index_file, buckets_file) EN MODO lectura:
        root = leer_nodo(index_file, 0)
        SI root es nodo_interno:
            lista += _aux_range_search(buckets_file, index_file, root.left, lower, upper)
            lista += _aux_range_search(buckets_file, index_file, root.right, lower, upper)
        RETORNAR lista
```

Funciones auxiliares:

Algoritmo para buscar recursivamente por rango:
```
FUNCIÓN _aux_range_search(buckets_file, index_file, node_index, lower, upper):
    node = leer_nodo(index_file, node_index)
    lista = []
    
    SI node es nodo_interno:
        lista += _aux_range_search(buckets_file, index_file, node.left, lower, upper)
        lista += _aux_range_search(buckets_file, index_file, node.right, lower, upper)
    SI NO:
        bucket = leer_bucket(buckets_file, node.bucket_position)
        lista += buscar_en_rango(bucket, lower, upper)
        
        # Buscar en overflow chain
        MIENTRAS bucket.overflow_position != -1:
            bucket = leer_bucket(buckets_file, bucket.overflow_position)
            lista += buscar_en_rango(bucket, lower, upper)
    
    RETORNAR lista
```
Algoritmo para buscar elementos dentro de un rango en un bucket.
```
FUNCIÓN buscar_en_rango(bucket, lower, upper):
    matches = []
    PARA cada posición_en_heap en bucket.records:
        SI posición_en_heap != -1:
            record = HEAP.read(posición_en_heap)
            SI lower <= record.clave <= upper:
                matches.append(posición_en_heap)
    RETORNAR matches
```
### Eliminación
Algoritmo de eliminación en el hash:
```
FUNCIÓN delete(key):
    key = convertir_a_tipo_correcto(key)
    index_hash = get_bits(key, global_depth)
    
    ABRIR archivos (index_file, buckets_file) EN MODO lectura/escritura:
        root = leer_nodo(index_file, 0)
        SI index_hash[-1] == '0':
            RETORNAR _aux_delete(buckets_file, index_file, root.left, index_hash[:-1], key)
        SI NO:
            RETORNAR _aux_delete(buckets_file, index_file, root.right, index_hash[:-1], key)
```

Funciones auxiliares:
Algoritmo recursivo para realizar la eliminación
```
FUNCIÓN _aux_delete(buckets_file, index_file, node_index, index_hash, key):
    node = leer_nodo(index_file, node_index)
    
    SI node es nodo_interno:
        SI index_hash[-1] == '0':
            RETORNAR _aux_delete(buckets_file, index_file, node.left, index_hash[:-1], key)
        SI NO:
            RETORNAR _aux_delete(buckets_file, index_file, node.right, index_hash[:-1], key)
    SI NO:  # Es nodo hoja
        bucket = leer_bucket(buckets_file, node.bucket_position)
        eliminado = eliminar_de_bucket(bucket, key)
        
        # Buscar en overflow chain
        MIENTRAS NO eliminado Y bucket.overflow_position != -1:
            bucket = leer_bucket(buckets_file, bucket.overflow_position)
            eliminado = eliminar_de_bucket(bucket, key)
        
        RETORNAR eliminado
```
Algoritmo para eliminar de un bucket. Retorna un booleano para verificar si se llego a eliminar.
```

FUNCIÓN eliminar_de_bucket(bucket, key):
    PARA cada posición_en_heap en bucket.records:
        SI posición_en_heap != -1:
            record = HEAP.read(posición_en_heap)
            SI record.clave == key:
                # Eliminación lógica (marcar como vacío)
                bucket.records[i] = -1
                bucket.fullness -= 1
                actualizar_bucket(buckets_file, bucket)
                RETORNAR True
    RETORNAR False
```

## Complejidad en términos de acceso a memoria secundaria

| Operación       | Mejor Caso      | Peor Caso         | Escenario Crítico                          |
|----------------|----------------|------------------|-------------------------------------------|
| **Inserción**  | `O(1)`         | `O(N)`       | Split de buckets + reinserción de registros |
| **Búsqueda**   | `O(1)`         | `O(D + n)`   | Registro en último bucket de overflow      |
| **Búsqueda por Rango**      | `O(N)`         | `O(N)`           | Escaneo completo de todos los buckets      |
| **Eliminación**| `O(1)`         | `O(D + n)`   | Eliminación en último bucket de overflow   |

**Clave**:
- `n`: Número total de registros   
- `D`: Profundidad 
