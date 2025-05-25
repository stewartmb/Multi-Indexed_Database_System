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

(Imagen)

Un extendible hash se compone de:
- **Directorio**: Tabla que almacena punteros a buckets. Su tamaño es 2^D (donde D = profundidad global). La profundidad global es el número de bits utilizados por el directorio para indexar los buckets.
- **Buckets**: Contenedores que almacenan registros. Cada bucket tiene una profundidad local (d). La profundidad local es el número de bits usados por un bucket específico para determinar qué registros almacena.
- **Función de Hash**: Se usan los D bits más significativos para indexar el directorio.


## Representación usando un árbol
La implementación de la estructura se ha decidido que, en vez de hacer una tabla plana, el directorio estará organizado como un árbol. Este enfoque ha sudo basado en un laboratorio que se tuvo en clase. 

(Imagen 2)

Con este enfoque, el directorio se divide en dos:
- Nodos Internos (Internal Directory Nodes): Contienen decisiones de enrutamiento basadas en bits del hash.
- Nodos Hoja (Leaf Directory Nodes): Apuntan directamente a los buckets que almacenan registros.


## Estructura del índice:

### Archivo de índice
### Archivo de bucket 
### Archivo de datos

## Algoritmos de las operaciones

## Conplejidad

