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

## Observación importante
En esta implementación de B+ Tree, se ha decidido que las operaciones que se han hecho no serán recursivas, sino que serán de manera "iterativa".
Para lograr esto, cada IndexPage tendrá un puntero a su padre, lo que nos da un acceso directo al padre sin necesidad de tener que realizar una recursión.


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
FUNCIÓN insertar(registro, pos_nuevo_registro):
    // Validación de parámetros
    SI (registro Y pos_nuevo_registro proporcionados):
        RETORNAR error "Solo debe proporcionar uno"
    
    // Obtener clave del registro
    SI (registro proporcionado):
        pos_nuevo_registro = obtener_nueva_posición()
        clave = extraer_clave(registro)
        guardar_registro(registro)
    SINO:
        registro = leer_registro(pos_nuevo_registro)
        clave = extraer_clave(registro)

    // Leer información del árbol
    encabezado = leer_encabezado()
    raíz = encabezado.raíz
    num_páginas = encabezado.num_páginas

    // CASO 1: Árbol vacío
    SI (raíz es inválida):
        nueva_página = crear_página_hoja()
        nueva_página.claves[0] = clave
        nueva_página.hijos[0] = pos_nuevo_registro
        nueva_página.contador_claves = 1
        
        // Actualizar estructura
        num_páginas += 1
        actualizar_raíz(num_páginas)
        agregar_página(nueva_página)
        RETORNAR

    // CASO 2: Árbol no vacío
    pos_hoja = buscar_hoja(raíz, clave)
    página_hoja = leer_página(pos_hoja)

    // CASO 2.1: Página tiene espacio
    SI (página_hoja.contador_claves < M-1):
        nueva_página = insertar_en_hoja(página_hoja, clave, pos_nuevo_registro)
        escribir_página(pos_hoja, nueva_página)
        RETORNAR

    // CASO 2.2: Página llena - División necesaria
    clave_ascender, pos_nueva_página = dividir_hoja(pos_hoja, clave, pos_nuevo_registro)
    
    // Propagación de la división hacia arriba
    pos_actual = pos_hoja
    página_actual = página_hoja
    pos_padre = página_actual.padre

    MIENTRAS (VERDADERO):
        // CASO 2.2.1: Llegamos a la raíz
        SI (pos_padre == -1):
            pos_nueva_raíz = num_páginas + 1
            nueva_raíz = crear_página_interna()
            nueva_raíz.claves[0] = clave_ascender
            nueva_raíz.hijos[0] = pos_actual
            nueva_raíz.hijos[1] = pos_nueva_página
            nueva_raíz.contador_claves = 1

            // Actualizar padres
            página_actual.padre = pos_nueva_raíz
            nueva_página = leer_página(pos_nueva_página)
            nueva_página.padre = pos_nueva_raíz
            escribir_página(pos_actual, página_actual)
            escribir_página(pos_nueva_página, nueva_página)

            // Actualizar estructura
            actualizar_raíz(pos_nueva_raíz)
            agregar_página(nueva_raíz)
            ROMPER

        // CASO 2.2.2: Padre con espacio
        SINO SI (página_padre.contador_claves < M-1):
            nueva_página_padre = insertar_en_interno(página_padre, clave_ascender, pos_nueva_página)
            escribir_página(pos_padre, nueva_página_padre)
            ROMPER

        // CASO 2.2.3: Padre lleno - nueva división
        SINO:
            clave_ascender, pos_nueva_página = dividir_interno(pos_padre, clave_ascender, pos_nueva_página)
            pos_actual = pos_padre
            página_actual = leer_página(pos_actual)
            pos_padre = página_actual.padre

```


Funciones Auxiliares:
```
// Funciones auxiliares usadas
FUNCIÓN dividir_hoja(pos_página, clave, pos_registro):
    página = leer_página(pos_página)
    
    // Crear arrays temporales con claves y punteros
    claves_temp = copiar_claves(página)
    punteros_temp = copiar_punteros(página)
    
    // Insertar nuevo elemento en arrays temporales
    índice = buscar_posición_inserción(claves_temp, clave)
    insertar_en_array(claves_temp, clave, índice)
    insertar_en_array(punteros_temp, pos_registro, índice)
    
    // Calcular punto de división
    mitad = (M // 2) + (M % 2)  // Ajuste para M par/impar
    
    // Crear nueva página hoja
    nueva_página = crear_página_hoja()
    nueva_página.padre = página.padre
    
    // Dividir elementos
    página.claves = claves_temp[0:mitad]
    página.hijos = punteros_temp[0:mitad]
    página.contador_claves = mitad
    
    nueva_página.claves = claves_temp[mitad:]
    nueva_página.hijos = punteros_temp[mitad:]
    nueva_página.contador_claves = len(claves_temp) - mitad
    
    // Mantener enlace entre hojas
    nueva_página.hijos[M-1] = página.hijos[M-1]
    página.hijos[M-1] = pos_nueva_página
    
    // Escribir páginas
    escribir_página(pos_página, página)
    agregar_página(nueva_página)
    
    // Clave a ascender es la primera de la nueva página
    RETORNAR nueva_página.claves[0], pos_nueva_página

FUNCIÓN dividir_interno(pos_página, clave, pos_hijo):
    // Similar a dividir_hoja pero para nodos internos
    // Mantiene punteros a hijos y actualiza padres
    
    RETORNAR nueva_clave_ascender, pos_nueva_página
```

### Búsqueda
Algorimto de búsqueda:

```
FUNCIÓN buscar(clave):
    raíz = leer_posición_raíz()
    
    SI raíz es inválida (-1 o -2):
        RETORNAR lista_vacía
    
    nodo_actual = buscar_nodo_hoja(raíz, clave)
    resultados = []
    primera_iteración = VERDADERO
    
    MIENTRAS nodo_actual no sea NULO:
        inicio = calcular_indice_inicio(nodo_actual, clave, primera_iteración)
        
        PARA cada clave en nodo_actual DESDE inicio HASTA fin:
            SI clave < clave_actual:
                TERMINAR BUCLE
            SI clave == clave_actual:
                registro = leer_registro(puntero_actual)
                SI registro existe:
                    resultados.AÑADIR(puntero_actual)
        
        # Mover a la siguiente hoja si existe
        nodo_actual = obtener_siguiente_hoja(nodo_actual)
        primera_iteración = FALSO
    
    RETORNAR resultados

```

Funciones Auxiliares:

```
FUNCIÓN buscar_nodo_hoja(nodo, clave):
    MIENTRAS nodo no es hoja:
        indice = búsqueda_binaria(clave en nodo.claves)
        nodo = leer_hijo(nodo, indice)
    RETORNAR nodo 
```

### Búsqueda por rango
Algorimto de búsqueda por rango:

```
FUNCIÓN buscar_rango(clave_min, clave_max):
    raíz = leer_posición_raíz()
    nodo_actual = buscar_nodo_hoja(raíz, clave_min)
    resultados = []
    primera_iteración = VERDADERO
    
    SI nodo_actual es inválido:
        RETORNAR lista_vacía
    
    MIENTRAS nodo_actual no sea NULO:
        inicio = calcular_indice_inicio(nodo_actual, clave_min, primera_iteración)
        
        PARA cada clave en nodo_actual DESDE inicio HASTA fin:
            SI clave > clave_max:
                RETORNAR resultados
            SI clave >= clave_min Y clave <= clave_max:
                registro = leer_registro(puntero_actual)
                SI registro existe:
                    resultados.AÑADIR(puntero_actual)
        
        # Mover a la siguiente hoja
        nodo_actual = obtener_siguiente_hoja(nodo_actual)
        primera_iteración = FALSO
    
    RETORNAR resultados
```


Funciones Auxiliares:

```
FUNCIÓN calcular_indice_inicio(nodo, clave, primera_iteración):
    SI primera_iteración:
        RETORNAR búsqueda_binaria(clave en nodo.claves)
    SINO:
        RETORNAR 0  # Empezar desde el principio en hojas siguientes

FUNCIÓN obtener_siguiente_hoja(nodo):
    SI nodo.tiene_siguiente:
        RETORNAR leer_página(nodo.puntero_siguiente)
    SINO:
        RETORNAR NULO

FUNCIÓN búsqueda_binaria(clave, claves):
    # Implementación estándar de búsqueda binaria
    # Retorna el índice donde debería estar la clave
    izquierda = 0
    derecha = longitud(claves) - 1
    
    MIENTRAS izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        SI claves[medio] < clave:
            izquierda = medio + 1
        SINO SI claves[medio] > clave:
            derecha = medio - 1
        SINO:
            RETORNAR medio  # Clave exacta encontrada
    
    RETORNAR izquierda  # Posición de inserción
```

### Eliminación

Lamentablemente, la eliminación en la estructura demostró ser de mucha complejidad para implementarse. Entonces, se decidió obviar esta operación.

Igualmente, al momento de probar la eliminación en el frontend usando el índice se puede hacer, pero no se maneja correctamente.
