# Documentación - ISAM
## ¿Qué es?
El Método de Acceso Secuencial Indexado **(ISAM)** es una solución especial de organización de archivos que se implementa en sistemas de bases de datos para acelerar la recuperación de datos y optimizar los procesos. Iniciado por IBM en la década de 1960, también conocido como Método de Acceso Secuencial Indexado o ISAM, este método de almacenamiento de datos permitía el acceso secuencial y aleatorio a los registros mediante índices. Esto dio lugar a un sistema eficiente que permitía acceder a los archivos mediante métodos de acceso secuencial o directo.

(Imagen acá)

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

(Imagen)

### Sparse-Index file 
Contiene entradas solo para algunos registros en el archivo de datos, generalmente el primer registro en cada bloque de datos.

Para encontrar un registro específico, primero se busca en el índice el bloque que podría contener el registro y luego se busca secuencialmente dentro del bloque asociado.

(Imagen)

Para la implementación del proyecto, se utilizó el Sparse-Index con dos niveles de índices como se aprecia en la siguiente imagen:

(Imagen)

## ¿Como construir la parte estática?

Como el índice es estático, se debe hacer la creación del índice después de insertar los datos. 

Para realizar la construcción, debemos tener los datos ordenados (Se puede realizar un algorimto de ordenación) y después, desde las hojas, ir construyendo el ISAM hasta llegar a la raíz. 

(Imagen)

En el siguiente link, se puede apreciar como se hace la construcción: https://youtu.be/-GyqvYHVEWo?si=FTJ_mkv8zXiCJFnH



## Estructura del índice

La estructura del índice ISAM es la siguiente:



## Algoritmos 

### Inserción

### Búsqueda 

### Búsqueda por rango

### Eliminación 
