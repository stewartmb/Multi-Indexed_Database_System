# Documentación - Heap File
## ¿Qué es un Heap File?
El heap file para la organización de archivos en bases de datos es un método fundamental para almacenar datos en bases de datos. Es la forma más simple, que prioriza la inserción eficiente sobre la recuperación según criterios específicos. 
En términos de estructura, podemos imaginarlo fácilmente como un espacio desorganizado donde se guardan registros sin un orden claro. En el esquema de anexión, el flujo de datos se añade como una nueva entrada al final del archivo de registro existente, creando así una lista secuencial.

Imagen de Heap File:

![Imagen_HeapFile](/images/heap_img1.png)

Observación: Se permite la gestión de registros de longitud variable, por lo que resulta útil para el proyecto.
## Estructura Del Heap File
- **Header**: Al inicio del archivo, hay un encabezado que almacena el número total de registros (4 bytes, en formato 'i')
- **Registros**: Cada registro que ocupa un espacio que incluye los datos de este convertidos a bytes y un byte adicional como un **flag de eliminación** (0 si está activo, 1 si está eliminado).

## Funcionalidades Principales
A continuación, la explicación en las funcionalidades que tiene el heap file:
### Inicialización
- Se crea el archivo si no existe o lo vacía `force_create = True`
- Se configura el formato de los registros usando la clase registro universal `RegistroType`.
- El tamaño total de cada registro se establece como la cantidad de datos + un byte para el flag de eliminación.

### Inserción
Algoritmo de inserción:
```
insert(registro):

```


