# Documentación - ISAM
## ¿Qué es?
El Método de Acceso Secuencial Indexado **(ISAM)** es una solución especial de organización de archivos que se implementa en sistemas de bases de datos para acelerar la recuperación de datos y optimizar los procesos. Iniciado por IBM en la década de 1960, también conocido como Método de Acceso Secuencial Indexado o ISAM, este método de almacenamiento de datos permitía el acceso secuencial y aleatorio a los registros mediante índices. Esto dio lugar a un sistema eficiente que permitía acceder a los archivos mediante métodos de acceso secuencial o directo.

![Imagen_isam](/images/ISAM.png)

## Características
- **Archivo de datos primarios**: El archivo de disco contendrá registros reales vinculados por uno o más campos de clave primaria. Los registros apilados se organizan de forma que resulte fácil consultarlos en su conjunto, lo que permite procesar rápidamente una gran cantidad de datos simultáneamente.
- **Archivo de índice**: El archivo de índice, que contiene las direcciones de enlace que conducen desde la clave a su respectiva ubicación de registro en el archivo de datos principal, está compuesto por las claves que facilitan la búsqueda. Esta carrera suele tener menos nodos que el archivo de datos, lo que reduce el tiempo de búsqueda.
- **Área de desbordamiento**: La naturaleza contigua de los registros permite a ISAM gestionar los desbordamientos mediante un área de desbordamiento. Cuando el búfer principal se llena o cuando se introducen nuevos registros en un elemento no secuencial, estos se transfieren al área de desbordamiento. Además, cuenta con este sistema de indexación, lo que facilita el acceso.

Observación: Una característica distintiva de la estructura del índice ISAM es su estaticidad, lo que significa que no cambia según los datos útiles. Por lo tanto, la demanda de inicio de sesión y ordenamiento aumentará, lo que reducirá la eficiencia del sistema para gestionar inserciones, eliminaciones y actualizaciones. 


## Tipos 
El ISAM puede ser implementado de dos manera: como un Dense-Index File o como un Sparse Index-File.

### Dense-Index file
Contiene una entrada para cada registro en el archivo de datos.

Permite búsquedas muy rápidas de registros individuales, ya que cada registro tiene su propia entrada en el índice.

![Imagen_isam](/images/isamdi.png)

### Sparse-Index file 
Contiene entradas solo para algunos registros en el archivo de datos, generalmente el primer registro en cada bloque de datos.

Para encontrar un registro específico, primero se busca en el índice el bloque que podría contener el registro y luego se busca secuencialmente dentro del bloque asociado.

![Imagen_isam](/images/isamsi.png)

Para la implementación del proyecto, se utilizó el Sparse-Index con dos niveles de índices.


## ¿Como construir la parte estática?

Como el índice es estático, se debe hacer la creación del índice después de insertar los datos. 

Para realizar la construcción, debemos tener los datos ordenados (Se puede realizar un algorimto de ordenación) y después, desde las hojas, ir construyendo el ISAM hasta llegar a la raíz. 

![Imagen_isam](/images/ISAM_construccion.png)

En el siguiente link, se puede apreciar como se hace la construcción: https://youtu.be/-GyqvYHVEWo?si=FTJ_mkv8zXiCJFnH

## Observación importante
Para la construcción de la parte estática, se optó por realizarlo de la siguiente manera:
-  Dividimos el archivo original en varios bloques ordenados (se ordena usando RAM) y los guardamos en archivos temporales separados (index_temp).
-  Una vez cada uno de estos bloques estan internamente ordenados, los mezclamos usando un heap.
-  Ya teniendo todo el archivo de indices ordenado, podemos construirlo siguiendo el bottom-up approach.

## Estructura del índice

La estructura del índice ISAM es la siguiente:

### Archivo de índice 
EL index file se compone de dos partes:

- **Header**: Contiene la metadata.
   - Número de páginas de datos (nivel hoja)
   - Número de páginas de overflow
   - Orden del árbol (M)
   - Posición de la página raíz
     
- **Index Page**:
  - Booleano que indica si es nodo hoja o no
  - Arreglo de claves de búsqueda de tamaño M-1
  - Arreglo de punteros a hijos/páginas (o posiciones en Heap si es hoja) de tamaño M
  -  Puntero a página de overflow (-1 si no hay)
  -  Número de claves actuales en la página

### Archivo de indice temporal
La clase Index_temp es una estructura auxiliar utilizada en la implementación del ISAM para manejar temporalmente pares de clave-posición durante la construcción y reorganización de índices.
Contiene:
- Valor de la clave de indexación
- Posición en el Heap File (offset)

### Archivo de datos 
Almacena los registros de datos usando el Heap File.

## Algoritmos 
A continucación, se presentará los algoritmos para las operaciones dadas:

### Inserción

Algoritmo de la inserción:

```
FUNCIÓN add(record, pos_new_record):
    // Validar parámetros
    SI record NO es NULO Y pos_new_record NO es NULO:
        RETORNAR "Error: Solo debe proporcionar record o pos_new_record"
    SI record es NULO Y pos_new_record es NULO:
        RETORNAR "Error: Debe proporcionar record o pos_new_record"
    
    // Obtener clave y posición del nuevo registro
    SI record NO es NULO:
        pos_new_record = HEAP.insert(record)
        key = OBTENER_CLAVE(record)
    SINO:
        record = HEAP.read(pos_new_record)
        key = OBTENER_CLAVE(record)
    
    // Obtener posición de la raíz
    (_, _, _, pos_root) = LEER_ENCABEZADO_INDICE()
    
    // Buscar hoja adecuada para la inserción
    pos_hoja = buscar_hoja(pos_root, key)
    pagina_hoja = LEER_PAGINA_INDICE(pos_hoja)
    
    // Intentar inserción en hoja principal
    SI pagina_hoja.key_count < M - 1:
        // Hay espacio en la hoja principal
        pagina_hoja.keys[pagina_hoja.key_count] = key
        pagina_hoja.childrens[pagina_hoja.key_count] = pos_new_record
        pagina_hoja.key_count += 1
        ESCRIBIR_PAGINA_INDICE(pos_hoja, pagina_hoja)
    SINO:
        // Buscar última página de overflow
        pos_ultima_overflow = encontrar_ultima_overflow(pagina_hoja)
        pagina_ultima = LEER_PAGINA_INDICE(pos_ultima_overflow)
        
        SI pagina_ultima.key_count < M - 1:
            // Hay espacio en la última página de overflow
            pagina_ultima.keys[pagina_ultima.key_count] = key
            pagina_ultima.childrens[pagina_ultima.key_count] = pos_new_record
            pagina_ultima.key_count += 1
            ESCRIBIR_PAGINA_INDICE(pos_ultima_overflow, pagina_ultima)
        SINO:
            // Crear nueva página de overflow
            nueva_pagina = CREAR_PAGINA_HOJA(M)
            nueva_pagina.keys[0] = key
            nueva_pagina.childrens[0] = pos_new_record
            nueva_pagina.key_count = 1
            nueva_pagina.next = -1
            
            // Registrar nueva página
            pos_nueva = AGREGAR_PAGINA_OVERFLOW(nueva_pagina)
            
            // Enlazar nueva página a la cadena
            pagina_ultima.next = pos_nueva
            ESCRIBIR_PAGINA_INDICE(pos_ultima_overflow, pagina_ultima)

```

Funciones auxiliares:

Algoritmo para encontrar la ultima página de overflow:

```
FUNCIÓN encontrar_ultima_overflow(pagina_inicial):
    pagina_actual = pagina_inicial
    pos_actual = OBTENER_POSICION(pagina_inicial)
    
    MIENTRAS pagina_actual.next != -1:
        pos_actual = pagina_actual.next
        pagina_actual = LEER_PAGINA_INDICE(pos_actual)
    
    RETORNAR pos_actual
```

### Búsqueda 

Algoritmo de búsqueda:

```
FUNCIÓN search(key):
    // Obtener posición de la raíz desde el encabezado
    (_, _, _, pos_root) = LEER_ENCABEZADO_INDICE()
    
    // Encontrar la hoja donde debería estar la clave
    pos_hoja = buscar_hoja(pos_root, key)
    
    // Si no se encontró hoja válida
    SI pos_hoja == -1:
        RETORNAR lista_vacia
    
    resultados = []
    detener = FALSO
    
    // Buscar en la hoja y posibles páginas de overflow
    MIENTRAS VERDADERO:
        pagina_actual = LEER_PAGINA_INDICE(pos_hoja)
        
        // Buscar en las claves de la página actual
        PARA cada clave_en_pagina EN pagina_actual:
            SI clave_en_pagina > key:
                detener = VERDADERO
            SI clave_en_pagina == key:
                registro = LEER_HEAP(pagina_actual.childrens[i])
                SI registro NO es eliminado:
                    AGREGAR registro A resultados
        
        // Buscar en páginas de overflow
        resultados_overflow, detener_overflow = buscar_en_overflow(pagina_actual, key, key)
        resultados.AGREGAR(resultados_overflow)
        detener = detener O detener_overflow
        
        // Decidir si continuar con la siguiente página
        SI NO detener Y pos_hoja < M²:
            pos_hoja = pos_hoja + 1
        SINO:
            TERMINAR BUCLE
    
    RETORNAR resultados
```

Funciones auxiliares:

Algoritmo para buscar un registro en una hoja:

```
FUNCIÓN buscar_hoja(pos_node, key_min):
    SI pos_node == -2:  // Caso inválido
        RETORNAR -1
    
    pagina_actual = LEER_PAGINA_INDICE(pos_node)
    
    // Descender por el árbol hasta encontrar una hoja
    MIENTRAS NO pagina_actual.es_hoja:
        encontrado = FALSO
        
        // Buscar el hijo adecuado
        PARA i DESDE 0 HASTA pagina_actual.key_count-1:
            SI key_min <= pagina_actual.keys[i]:
                pos_node = pagina_actual.childrens[i]
                pagina_actual = LEER_PAGINA_INDICE(pos_node)
                encontrado = VERDADERO
                TERMINAR BUCLE
        
        // Si no se encontró, usar el último hijo
        SI NO encontrado:
            pos_node = pagina_actual.childrens[pagina_actual.key_count]
            pagina_actual = LEER_PAGINA_INDICE(pos_node)
    
    RETORNAR pos_node  // Posición de la hoja encontrada
```

Algoritmo para buscar dentro de un overflow:

```
FUNCIÓN buscar_en_overflow(pagina_hoja, key1, key2):
    resultados = []
    detener = FALSO
    
    SI pagina_hoja.next == -1:
        RETORNAR resultados, detener
    
    pagina_overflow = pagina_hoja.next
    
    // Recorrer la cadena de overflow
    MIENTRAS pagina_overflow != -1:
        pagina_actual = LEER_PAGINA_INDICE(pagina_overflow)
        
        PARA cada clave_en_pagina EN pagina_actual:
            SI clave_en_pagina >= key1 Y clave_en_pagina <= key2:
                registro = LEER_HEAP(pagina_actual.childrens[i])
                SI registro NO es eliminado:
                    AGREGAR registro A resultados
            SI clave_en_pagina > key2:
                detener = VERDADERO
        
        pagina_overflow = pagina_actual.next
    
    RETORNAR resultados, detener
```


### Búsqueda por rango

Algoritmo de búsqueda por rango:

```
FUNCIÓN search_range(key1, key2):
    // Validar rango
    SI key1 > key2:
        INTERCAMBIAR(key1, key2)
    
    // Obtener posición de la raíz desde el encabezado
    (_, _, _, pos_root) = LEER_ENCABEZADO_INDICE()
    
    // Encontrar la hoja donde comienza el rango
    pos_hoja_inicial = buscar_hoja(pos_root, key1)
    
    // Si no se encontró hoja válida
    SI pos_hoja_inicial == -1:
        RETORNAR lista_vacia
    
    resultados = []
    detener = FALSO
    pos_hoja_actual = pos_hoja_inicial
    
    // Buscar en hojas consecutivas hasta cubrir el rango
    MIENTRAS VERDADERO:
        pagina_actual = LEER_PAGINA_INDICE(pos_hoja_actual)
        
        // Buscar en las claves de la página actual
        PARA cada clave_en_pagina EN pagina_actual:
            SI clave_en_pagina > key2:
                detener = VERDADERO
            SI clave_en_pagina >= key1 Y clave_en_pagina <= key2:
                registro = LEER_HEAP(pagina_actual.childrens[i])
                SI registro NO es eliminado:
                    AGREGAR registro A resultados
        
        // Buscar en páginas de overflow asociadas
        resultados_overflow, detener_overflow = buscar_en_overflow(pagina_actual, key1, key2)
        resultados.AGREGAR(resultados_overflow)
        detener = detener O detener_overflow
        
        // Decidir si continuar con la siguiente página
        SI NO detener Y pos_hoja_actual < M²:
            pos_hoja_actual = pos_hoja_actual + 1
        SINO:
            TERMINAR BUCLE
    
    RETORNAR resultados
```


### Eliminación

Algoritmo de eliminación:

```
FUNCIÓN delete(key):
    // Obtener posición raíz
    (_, _, _, pos_root) = LEER_ENCABEZADO_INDICE()
    
    // Buscar primera hoja que podría contener la clave
    pos_hoja_actual = buscar_hoja(pos_root, key)
    
    // Verificar si la clave existe
    SI BUSCAR(key) está vacío:
        RETORNAR  // No hacer nada si la clave no existe
    
    detener = FALSO
    
    // Recorrer hojas relevantes
    MIENTRAS VERDADERO:
        detener = eliminar_en_hoja(pos_hoja_actual, key, detener)
        
        SI detener O pos_hoja_actual >= M²:
            TERMINAR BUCLE
        SINO:
            pos_hoja_actual = pos_hoja_actual + 1
```

Funciones auxiliares:

Algoritmo para eliminar un registro en una hoja:

```
FUNCIÓN eliminar_en_hoja(pos_hoja, key, detener):
    pagina = LEER_PAGINA_INDICE(pos_hoja)
    
    // Caso sin overflow
    SI pagina.next == -1:
        nueva_pagina = CREAR_PAGINA_HOJA_VACIA(M)
        
        PARA cada (clave, hijo) EN pagina:
            SI clave > key:
                detener = VERDADERO
            SI clave != key:
                AGREGAR (clave, hijo) A nueva_pagina
        
        ESCRIBIR_PAGINA_INDICE(pos_hoja, nueva_pagina)
        RETORNAR detener
    
    // Caso con overflow
    SINO:
        // 1. Procesar página principal
        nueva_pagina_principal = CREAR_PAGINA_HOJA_VACIA(M)
        
        PARA cada (clave, hijo) EN pagina:
            SI clave > key:
                detener = VERDADERO
            SI clave != key:
                AGREGAR (clave, hijo) A nueva_pagina_principal
        
        nueva_pagina_principal.next = pagina.next
        ESCRIBIR_PAGINA_INDICE(pos_hoja, nueva_pagina_principal)
        
        // 2. Procesar cadena de overflow
        lista_overflow = OBTENER_LISTA_OVERFLOW(pagina.next)
        pos_anterior = pos_hoja
        
        PARA cada pos_overflow EN lista_overflow:
            pagina_overflow = LEER_PAGINA_INDICE(pos_overflow)
            nueva_pagina_overflow = CREAR_PAGINA_HOJA_VACIA(M)
            
            PARA cada (clave, hijo) EN pagina_overflow:
                SI clave > key:
                    detener = VERDADERO
                SI clave != key:
                    AGREGAR (clave, hijo) A nueva_pagina_overflow
            
            nueva_pagina_overflow.next = pagina_overflow.next
            
            // Actualizar o eliminar página de overflow
            SI nueva_pagina_overflow.key_count > 0:
                ESCRIBIR_PAGINA_INDICE(pos_overflow, nueva_pagina_overflow)
                pos_anterior = pos_overflow
            SINO:
                // Eliminar página vacía
                pagina_anterior = LEER_PAGINA_INDICE(pos_anterior)
                pagina_anterior.next = nueva_pagina_overflow.next
                ESCRIBIR_PAGINA_INDICE(pos_anterior, pagina_anterior)
        
        RETORNAR detener
```

Algoritmo para retornar una lista de overflows:

```
FUNCIÓN obtener_lista_overflow(pos_inicial):
    lista = []
    pos_actual = pos_inicial
    
    MIENTRAS pos_actual != -1:
        AGREGAR pos_actual A lista
        pagina = LEER_PAGINA_INDICE(pos_actual)
        pos_actual = pagina.next
    
    RETORNAR lista

```

## Complejidad en acceso a memoria secundaria 
| Operación       | Mejor Caso       | Peor Caso            | Caso Promedio        | Condiciones Clave                     |
|----------------|------------------|----------------------|----------------------|---------------------------------------|
| **Inserción**  | `O(1)`          | `O(logₘn + k)`      | `O(logₘn + k/2)`    | k = longitud cadena overflow          |
| **Búsqueda**   | `O(logₘn)`     | `O(logₘn + k)`      | `O(logₘn + k/2)`    | n = número total de registros         |
| **Rango**      | `O(logₘn + 1)` | `O(logₘn + p + o)`  | `O(logₘn + (p+o)/2)`| p = páginas hoja, o = páginas overflow|
| **Eliminación**| `O(logₘn + 1)` | `O(logₘn + k + m)`  | `O(logₘn + (k+m)/2)`| m = páginas overflow modificadas      |

**Leyenda:**
- `m`: Orden del árbol (fan-out)
- `n`: Número total de registros
- `k`: Máxima longitud de cadena overflow
- `p`: Páginas hoja en rango de búsqueda
- `o`: Páginas overflow en rango de búsqueda

