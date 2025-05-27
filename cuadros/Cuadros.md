# Cuadros comparativos de desempeño
En esta sección se mostraran los cuadros comparativos de las pruebas realizadas para analizar la eficiencia de los índices.

## Para 10k datos

### Prueba 1: Tiempo de creación de los índices

Primero, se realizó la creación de la data con un total de 10k registros. 

Posteriormente, se realizó la medición del tiempo en que demora la creación de todos los índices en el dataset creado. 

Se hizo este experimento un total de 10 veces. Se sacó el tiempo máximo y mínimo, el tiempo promedio y la desviación estándar.

**Cuadro 1:**

| Índice  | Máximo  | Mínimo  | Promedio | Desviación estándar |
|------------|---------|---------|----------|---------------------|
| heap       | 0.8802  | 0.8502  | 0.8515   | 0.0118             |
| bptree     | 4.7545  | 4.5852  | 4.6746   | 0.0479             |
| hash       | 1.1640  | 0.9014  | 0.9747   | 0.0659             |
| sequential | 13.4000 | 12.7459 | 13.0642  | 0.2164             |
| isam       | 0.8259  | 0.7195  | 0.7604   | 0.0300             |
| b+tree     | 2.3175  | 2.1017  | 2.1996   | 0.0715             |
| rtree      | 18.0558 | 15.6037 | 16.2561  | 0.6891             |


**Análisis:**

Los resultados experimentales con 10,000 registros revelan diferencias significativas en el rendimiento de los métodos de indexación evaluados. ISAM emerge como el método más eficiente con 0.76 ms promedio, seguido por Heap (0.85 ms) y Hash (0.97 ms), mientras que Sequential (13.06 ms) y R-Tree (16.26 ms) muestran los peores rendimientos.

El excelente rendimiento de **ISAM** se debe a su arquitectura híbrida que combina indexación y acceso secuencial. Su estructura de dos niveles permite acceso directo al bloque correcto mediante el índice primario, seguido de una búsqueda secuencial local sobre un conjunto reducido de datos. Esta característica, junto con su optimización para operaciones de consulta frecuentes y la ausencia de overhead de reorganización, explica tanto su velocidad como su baja desviación estándar (0.03), indicando consistencia en el rendimiento.

**Heap** demuestra un rendimiento casi tan bueno como ISAM debido a su naturaleza de acceso directo. La estructura permite acceso O(1) por posición, almacenamiento contiguo que optimiza el uso de memoria caché, y ausencia de overhead de mantenimiento durante las consultas. Su desviación estándar extremadamente baja (0.012) confirma la predictibilidad del método cuando se aprovechan sus características de acceso directo.
Hash presenta un buen rendimiento pero con mayor variabilidad (desviación 0.066), lo cual es consistente con su naturaleza probabilística. Aunque teóricamente ofrece acceso O(1), la presencia de colisiones introduce overhead adicional que depende de la calidad de la función hash y el método de resolución de colisiones empleado. Esta variabilidad explica por qué, a pesar de su complejidad teórica constante, no supera consistentemente a ISAM o Heap.

**B+ Tree** muestra un rendimiento intermedio (2.20 ms) que refleja su complejidad logarítmica O(log n). Para 10K registros, cada búsqueda requiere aproximadamente 13-14 comparaciones atravesando múltiples niveles del árbol desde la raíz hasta las hojas. Cada nivel puede implicar operaciones de E/S adicionales, y el mantenimiento de las propiedades de balance del árbol introduce overhead computacional. Su desviación estándar moderada (0.071) indica variabilidad según la profundidad de búsqueda requerida.

**Sequential** presenta el segundo peor rendimiento debido a su complejidad lineal O(n), requiriendo examinar potencialmente todos los registros sin aprovechar ninguna estructura de indexación. Para 10K registros, esto implica un promedio de 5K comparaciones por búsqueda. La desviación estándar moderada (0.216) refleja la variabilidad según la posición del elemento buscado en la secuencia.

**R-Tree** exhibe el peor rendimiento, lo cual es explicable considerando que fue diseñado para datos multidimensionales pero se está aplicando a datos unidimensionales. El solapamiento de regiones (MBR) obliga a explorar múltiples caminos durante la búsqueda, los cálculos geométricos de intersección y contención son computacionalmente costosos, y la estructura no aprovecha las ventajas del particionamiento espacial en datos 1D. Su alta desviación estándar (0.689) indica la naturaleza impredecible de estas operaciones espaciales mal aplicadas.


## Para 50k datos




## Para 100k datos
