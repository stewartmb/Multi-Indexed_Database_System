# Documentación - Sequential File
## ¿Qué es un Sequential File?
La organización secuencial de archivos es un método que permite almacenar los registros en un orden específico. Por ejemplo, imagine los nombres de los estudiantes ordenados alfabéticamente en una secuencia correcta. Al final del archivo, se pueden agregar nuevos registros; no tiene una longitud fija, ya que se puede actualizar. Resulta eficiente para conjuntos de datos pequeños, ya que la estructura lineal permite un procesamiento rápido y permite recorrer todo el conjunto fácilmente.

Ejemplo de un secuencial file usado para ordenar nombres:

![Imagen_SF1](/images/Sequential_img1.png)

**Observación**: Los registros se guardan de manera secuencial, usualmente basándose en la clave primaria de la tabla.Para lograr esto, es fundamental que el archivo conserve los registros organizados físicamente de acuerdo con el valor del campo de búsqueda (clave). Se puede implementar la **búsqueda binaria** para lograr una complejidad de acceso a memoria secundaria de O(log n).

Ejemplo de búsqueda binaria - pseudocódigo:

![Imagen_BS](/images/Binary_search.png)


La búsqueda binaria será fundamental al momento de realizar las búsquedas y para encontrar la posición en dónde insertar un nuevo registro. Pero, ¿cómo podemos asegurar que siempre esté ordenado?

## Estrategia de archivo auxiliar
Para asegurar que siempre esté ordenado, las inserciones más recientes se almacenarán en un archivo auxiliar (Un espacio extra del que ofrece el sequential). Para que este espacio adicional no sea igual de grande que el sequential, le asignaremos un tamaño máximo `k`. 

Teniendo esto en cuenta, al momento de hacer búsquedas, estas se deben realizar también dentro del espacio auxiliar. Para evitar que la búsqueda en el auxiliar sea ineficiente, se optó por que este espacio esté ordenado por la clave.

Ejemplo sequential con espacio extra ordenado por clave:

![Imagen_aux1](/images/aux3.png)

**Observación 2**: Llegará un punto en dónde el sequential como su espacio extra se llenen. Esto significa que necesitamos una manera de reconstruir el archivo de índice (Combinamos el sequential con su auxiliar para formar un nuevo sequential). Por ello, tendremos un algoritmo que reconstruya el archivo cuando el espacio auxiliar se llene.

Para poder realizar una reconstrución correcta, debemos saber dónde se encuentra cada registro, ya que el sequential resultante debe estar ordenado. Para ello se utilizarán punteros al siguiente registro:

![Imagen_aux2](/images/aux2.png)

Entonces para cada registro en el archivo de índices, tendrá un puntero que apunte a su siguiente y se debe conocer a que espacio pertenece (si está en el principal o en el auxiliar).

Cuando se elimine un registro, se debe marcar como eliminado, para que duranta la reconstrucción del sequential este registro se omita. Como ya tenemos al -1 para cuando un registro no tiene un next, usaremos al -2 para marcar como eliminado.

## Estructura del índice
El índice implementado es una lista enlazada ordenada con las siguientes características:
### Archivo de índice (index_file.bin):
El archivo de índice tiene dos partes:
- Encabezado: 12 bytes
  - pos_root: Posición del primer registro en el espacio principal.
  - num_dat: Número de registros en el espacio principal.
  - tam_aux: Número de registros en el espacio adicional.
- Registro:
  - key: Clave de búsqueda.
  - pos: Posición en el archivo de datos (data_file.bin).
  - next: Puntero al siguiente registro en el índice (-2 si el registro está eliminado)
### Archivo de datos (data_file.bin):
Almacena los registros completos en el Heap File.

## Algoritmos auxiliares para las búsquedas e inserciones:
### Algoritmo de búsqueda binaria:
```
FUNCIÓN binary_search_prev(key):
    pos_root, num_dat, _ = leer_encabezado()
    
    SI pos_root == -1:
        RETORNAR pos_root
    
    left = 0
    right = num_dat - 1
    mid = pos_root
    
    MIENTRAS left <= right:
        mid = (left + right) / 2
        registro = leer_índice(mid)
        
        SI registro.key == key:
            // Buscar primer registro menor que key
            pos_prev = mid - 1
            MIENTRAS pos_prev >= 0 Y (registro.next == -2 O registro.key >= key):
                pos_prev = pos_prev - 1
            SI pos_prev < 0:
                RETORNAR pos_root
            RETORNAR pos_prev
            
        SI NO registro.key < key:
            left = mid + 1
        SI NO:
            right = mid - 1
    
    // Si no se encontró la clave exacta
    pos_prev = mid
    MIENTRAS pos_prev >= 0 Y (registro.next == -2 O registro.key >= key):
        pos_prev = pos_prev - 1
    SI pos_prev < 0:
        RETORNAR pos_root
    RETORNAR pos_prev
```

### Algoritmo de búsqueda lineal:
```
FUNCIÓN linear_search(key, pos):
    SI pos == -1:
        RETORNAR (-1, -1)
    
    pos_root, num_dat, tam_aux = leer_encabezado()
    root = leer_índice(pos_root)
    
    SI root.key == key:
        RETORNAR (-1, pos_root)
    
    SI root.key > key:
        RETORNAR (-1, -1)
    
    prev_ptr = pos
    temp_ptr = pos
    
    MIENTRAS temp_ptr != -1:
        registro = leer_índice(temp_ptr)
        
        SI registro.key == key:
            RETORNAR (prev_ptr, temp_ptr)
        
        SI registro.key > key:
            RETORNAR (prev_ptr, -1)
        
        prev_ptr = temp_ptr
        temp_ptr = registro.next
    
    RETORNAR (prev_ptr, -1)
```

## Algoritmo de reconstrucción:
Para realizar la reconstrución del archivo sequential: 
```
FUNCIÓN reconstruction():
    pos_root, num_dat, _ = leer_encabezado()
    pos_index = pos_root
    total_dat = 0
    
    // Crear archivo temporal
    ABRIR "temp.bin" PARA ESCRITURA
    ESCRIBIR encabezado (-1, 0, 0)
    
    // Recorrer lista enlazada
    MIENTRAS pos_index != -1:
        registro = leer_índice(pos_index)
        next_pos = registro.next
        
        // Saltar eliminados
        SI registro.next == -2:
            pos_index = next_pos
            CONTINUAR
        
        // Actualizar puntero
        registro.next = total_dat + 1
        
        // Escribir en temporal
        ESCRIBIR registro EN "temp.bin"
        total_dat = total_dat + 1
        pos_index = next_pos
    
    // Ajustar último puntero
    SI total_dat > 0:
        MOVER puntero A posición (total_dat - 1) EN "temp.bin"
        ESCRIBIR next = -1
    
    // Actualizar encabezado
    ESCRIBIR encabezado (0, total_dat, 0) EN "temp.bin"
    CERRAR "temp.bin"
    
    // Reemplazar archivo
    ELIMINAR index_file
    RENOMBRAR "temp.bin" COMO index_file
    
    // Actualizar K
    K = REDONDEAR(RAIZ_CUADRADA(total_dat) + 0.5)
```


## Algoritmos para las operaciones básicas
### Inserción:
Algoritmo de inserción:

El algoritmo de inserción maneja la adición de registros a un índice secuencial sobre un *Heap File*, asegurando que se mantenga ordenado por clave. Primero valida los parámetros: debe recibir **o bien** el registro a insertar **o bien** su posición en el *Heap File*. Luego, obtiene la clave del registro y la posición donde se almacenó en el *Heap*. Si el índice está vacío, el nuevo registro se convierte en la raíz. Si no, busca la posición correcta en el índice mediante una **búsqueda binaria** seguida de una **búsqueda lineal** para ajustar los punteros. Si la inserción requiere actualizar la raíz (por ser la clave más pequeña), se modifica; en caso contrario, se enlaza el nuevo nodo entre los registros existentes. Finalmente, si el archivo auxiliar alcanza un tamaño crítico (**K**), se dispara una **reconstrucción** del índice para mantener su eficiencia. El algoritmo garantiza que el índice siga siendo secuencial y accesible para búsquedas rápidas.

```
FUNCIÓN add(record, pos_new_record):
    // Validación de parámetros
    SI record != NULO Y pos_new_record != NULO:
        RETORNAR "Error"
    SI record == NULO Y pos_new_record == NULO:
        RETORNAR "Error"
    
    // Obtener posición y clave
    SI record != NULO:
        pos_new_record = insertar_en_heap(record)
        key = obtener_clave(record)
    SI NO:
        record = leer_datos(pos_new_record)
        key = obtener_clave(record)
    
    pos_root, num_dat, tam_aux = leer_encabezado()
    
    // Crear nuevo registro de índice
    nuevo_index = Index_Record(key, pos_new_record)
    pos_new_index = agregar_a_índice(nuevo_index)
    
    // Caso 1: Índice vacío
    SI pos_root == -1:
        actualizar_raiz(pos_new_index)
        SI tam_aux + 1 == K:
            reconstruction()
        RETORNAR
    
    // Búsqueda de posición
    pos = binary_search_prev(key)
    prev_ptr, temp_ptr = linear_search(key, pos)
    
    // Caso 2: Insertar como nueva raíz
    SI prev_ptr == -1:
        nuevo_index.next = pos_root
        actualizar_raiz(pos_new_index)
        escribir_índice(nuevo_index, pos_new_index)
        SI tam_aux + 1 == K:
            reconstruction()
        RETORNAR
    
    // Caso 3: Insertar en medio
    registro_prev = leer_índice(prev_ptr)
    nuevo_index.next = registro_prev.next
    registro_prev.next = pos_new_index
    escribir_índice(registro_prev, prev_ptr)
    escribir_índice(nuevo_index, pos_new_index)
    
    SI tam_aux + 1 == K:
        reconstruction()
```
### Búsqueda:

Algoritmo de búsqueda:

Primero, verifica si el índice está vacío, en cuyo caso retorna una lista vacía. Si hay datos, utiliza una búsqueda binaria para encontrar una posición aproximada  y luego una búsqueda lineal para ubicar el primer registro de índice con la clave buscada. A partir de ahí, recorre la lista enlazada de registros de índice (seguir el campo next) mientras las claves coincidan, acumulando las posiciones correspondientes del Heap File en un arreglo de resultados. Finalmente, retorna todas las posiciones encontradas o una lista vacía si no hay coincidencias.

```
FUNCIÓN search(key):
    resultado = []
    pos_root, num_dat, _ = leer_encabezado()
    
    SI pos_root == -1:
        RETORNAR resultado
    
    // Búsqueda inicial
    pos = binary_search_prev(key)
    prev_ptr, temp_ptr = linear_search(key, pos)
    
    // Recorrer coincidencias
    MIENTRAS temp_ptr != -1:
        registro = leer_índice(temp_ptr)
        SI registro.key != key:
            DETENER
        resultado.agregar(registro.pos)
        temp_ptr = registro.next
    
    RETORNAR resultado
```
### Búsqueda por rango:

Algoritmo de búsqueda por rango:

El algoritmo de **búsqueda por rango** recupera eficientemente todas las posiciones en el *Heap File* cuyas claves estén dentro del intervalo `[key1, key2]`. Primero, verifica si el índice está vacío, devolviendo una lista vacía en ese caso. Si hay datos, utiliza una **búsqueda binaria** seguida de una **búsqueda lineal** para ubicar el primer registro con clave mayor o igual a `key1`. Si no se encuentra una coincidencia exacta, ajusta el puntero al primer registro relevante. Luego, recorre secuencialmente los registros del índice (siguiendo el campo `next`), agregando al resultado las posiciones cuyas claves caigan dentro del rango, hasta superar `key2`. Este método aprovecha el orden del índice para minimizar accesos a disco y garantiza resultados completos y ordenados.

```
FUNCIÓN search_range(key1, key2):
    resultado = []
    pos_root, num_dat, _ = leer_encabezado()
    
    SI pos_root == -1:
        RETORNAR resultado
    
    // Búsqueda inicial
    pos = binary_search_prev(key1)
    prev_ptr, temp_ptr = linear_search(key1, pos)
    
    // Ajustar si no se encontró key1 exacta
    SI temp_ptr == -1:
        temp_ptr = prev_ptr
        SI prev_ptr == -1:
            temp_ptr = pos_root
    
    // Recorrer rango
    MIENTRAS temp_ptr != -1:
        registro = leer_índice(temp_ptr)
        SI registro.key > key2:
            DETENER
        SI registro.key >= key1:
            resultado.agregar(registro.pos)
        temp_ptr = registro.next
    
    RETORNAR resultado
```
### Eliminación:

Algoritmo de la eliminación:

El algoritmo de **eliminación** maneja la eliminación lógica de todos los registros del índice que coincidan con una clave dada, manteniendo la estructura ordenada del archivo secuencial. Primero verifica si el índice está vacío, retornando un mensaje en tal caso. Si hay datos, utiliza una **búsqueda binaria** seguida de una **búsqueda lineal** para encontrar la primera aparición de la clave. Luego, recorre todos los registros con esa clave, marcándolos como eliminados (estableciendo `next = -2`) sin borrarlos físicamente, lo que permite reconstrucciones posteriores. Si el registro eliminado era la raíz (`prev_ptr == -1`), actualiza la raíz al siguiente nodo válido; de lo contrario, ajusta los punteros del nodo anterior para "saltar" los eliminados, manteniendo la integridad de la lista enlazada. Este enfoque asegura eficiencia sin reorganización inmediata, delegando posibles compactaciones a una futura **reconstrucción**.

```
FUNCIÓN delete(key):
    pos_root, num_dat, tam_aux = leer_encabezado()
    
    SI pos_root == -1:
        RETORNAR "Vacío"
    
    // Buscar registro
    pos = binary_search_prev(key)
    prev_ptr, temp_ptr = linear_search(key, pos)
    
    SI temp_ptr == -1:
        RETORNAR "No encontrado"
    
    // Marcar como eliminado
    MIENTRAS temp_ptr != -1:
        registro = leer_índice(temp_ptr)
        SI registro.key != key:
            DETENER
        
        next_ptr = registro.next
        registro.next = -2  // Marcar eliminado
        escribir_índice(registro, temp_ptr)
        temp_ptr = next_ptr
    
    // Actualizar punteros
    SI prev_ptr == -1:
        actualizar_raiz(next_ptr)
    SI NO:
        registro_prev = leer_índice(prev_ptr)
        registro_prev.next = next_ptr
        escribir_índice(registro_prev, prev_ptr)
```

## Complejidad - Acceso a memoria secundaria:

| Operación| Acceso a disco    | Complejidad       |        
| :-------- | :------- | :------------------------- |
| Inserción | log(N) + K  | O(log (n) + k) / Peor caso: O(n) |
| Búsqueda  | log(N) + K  |  O(log (n) + k) |
| Búsqueda por rango | log(N) + K  + R (Registros dentro del rango)| O(log (n) + k + r) |
| Eliminación | log(N) + K |  O(log (n) + k) |
| Reconstrucción | N (Se construye un Sequential nuevo) |  O(n) |
