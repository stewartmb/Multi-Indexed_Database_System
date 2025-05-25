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

continuará...

