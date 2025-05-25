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
FUNCIÓN insertar(registro):
    // Obtener el número actual de registros
    count = leer_encabezado()
    
    // Calcular la posición donde se insertará (final del archivo)
    offset = HEADER_SIZE + (count * RECORD_SIZE)
    
    // Escribir el registro
    ABRIR archivo EN MODO append-binario
        MOVER puntero A offset
        ESCRIBIR datos_del_registro
        ESCRIBIR flag_eliminado = 0 (activo) // Porque es uno nuevo, asi que esta activo
    CERRAR archivo
    
    // Actualizar el contador en el encabezado
    escribir_encabezado(count + 1)
    
    RETORNAR count  // Posición donde se insertó
```

### Leer un archivo 
Algoritmo para leer un archivo:
```
FUNCIÓN read(pos):
    SI pos < 0 O pos >= leer_encabezado() ENTONCES
        RETORNAR None  // Posición inválida
    
    ABRIR archivo EN MODO lectura-binaria
        MOVER puntero A HEADER_SIZE + (pos * RECORD_SIZE)
        LEER datos_registro
        LEER flag_eliminado
    CERRAR archivo
    
    SI flag_eliminado == 1 ENTONCES
        RETORNAR None
    
    registro = convertir_bytes_a_registro(datos_registro)
    RETORNAR registro
```
### Búsqueda por rango
Algoritmo para buscar un registro dentro de un rango (los resultados incluyen al mínimo y al máximo):
```
FUNCIÓN buscar(left, right):
    registros_encontrados = []
    count = leer_encabezado()
    
    ABRIR archivo EN MODO lectura-binaria
        MOVER puntero A HEADER_SIZE  // Saltar encabezado
        
        PARA i DESDE 0 HASTA count-1 HACER:
            LEER datos_registro
            LEER flag_eliminado
            
            SI flag_eliminado == 1 ENTONCES
                CONTINUAR  // Saltar registros eliminados
            
            registro = convertir_bytes_a_registro(datos_registro)
            valor_clave = obtener_clave(registro)
            
            SI valor_clave >= left Y valor_clave <= right ENTONCES
                AGREGAR i A registros_encontrados  // Guardar posición
        FIN PARA
    CERRAR archivo
    
    RETORNAR registros_encontrados

```

## Complejidad en memoria secundaria


| Operación| Acceso a disco    | Complejidad       |        
| :-------- | :------- | :------------------------- |
| Inserción | 1 (lectura=) + 1 (escritura) | O(1) |
| Búsqueda por rango | N + 1 veces | O(n) |
| Leer un archivo | 1| O(1) |
