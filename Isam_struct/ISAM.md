# Documentación - ISAM
## ¿Qué es?
El Método de Acceso Secuencial Indexado **(ISAM)** es una solución especial de organización de archivos que se implementa en sistemas de bases de datos para acelerar la recuperación de datos y optimizar los procesos. Iniciado por IBM en la década de 1960, también conocido como Método de Acceso Secuencial Indexado o ISAM, este método de almacenamiento de datos permitía el acceso secuencial y aleatorio a los registros mediante índices. Esto dio lugar a un sistema eficiente que permitía acceder a los archivos mediante métodos de acceso secuencial o directo.

(Imagen acá)

## Características
- **Archivo de datos primarios**: El archivo de disco contendrá registros reales vinculados por uno o más campos de clave primaria. Los registros apilados se organizan de forma que resulte fácil consultarlos en su conjunto, lo que permite procesar rápidamente una gran cantidad de datos simultáneamente.
- **Archivo de índice**: El archivo de índice, que contiene las direcciones de enlace que conducen desde la clave a su respectiva ubicación de registro en el archivo de datos principal, está compuesto por las claves que facilitan la búsqueda. Esta carrera suele tener menos nodos que el archivo de datos, lo que reduce el tiempo de búsqueda.
- **Área de desbordamiento**: La naturaleza contigua de los registros permite a ISAM gestionar los desbordamientos mediante un área de desbordamiento. Cuando el búfer principal se llena o cuando se introducen nuevos registros en un elemento no secuencial, estos se transfieren al área de desbordamiento. Además, cuenta con este sistema de indexación, lo que facilita el acceso.

Observación: Una característica distintiva de la estructura del índice ISAM es su estaticidad, lo que significa que no cambia según los datos útiles. Por lo tanto, la demanda de inicio de sesión y ordenamiento aumentará, lo que reducirá la eficiencia del sistema para gestionar inserciones, eliminaciones y actualizaciones. 

## ¿Como construir la parte estática?
