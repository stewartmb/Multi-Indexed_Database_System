# Cuadros comparativos de desempeño y Gráficos resultantes
En esta sección se mostraran los cuadros comparativos de las pruebas realizadas para analizar la eficiencia de los índices.

## Prueba 1: Tiempo de creación de los índices

Primero, se realizó la creación de la data con datasets  de 10k, 50k y 100k registros. 

Posteriormente, se realizó la medición del tiempo en que demora la creación de todos los índices sobre los datasets. 

Se hizo este experimento un total de 10 veces. Se sacó el tiempo máximo y mínimo, el tiempo promedio y la desviación estándar

### Para 10k datos


**Cuadro 1:**

| Índice  | Máximo  | Mínimo  | Promedio | Desviación estándar |
|------------|---------|---------|----------|---------------------|
| heap       | 0.8802  | 0.8502  | 0.8515   | 0.0118             |
| bptree     | 4.7545  | 4.5852  | 4.6746   | 0.0479             |
| hash       | 1.1640  | 0.9014  | 0.9747   | 0.0659             |
| sequential | 13.4000 | 12.7459 | 13.0642  | 0.2164             |
| isam       | 0.8259  | 0.7195  | 0.7604   | 0.0300             |
| b+tree     | 2.3175  | 2.1017  | 2.1996   | 0.0715             |
| brin       |  2.3175 |  2.1017 |   2.1926 |   0.0715           |
| rtree      | 18.0558 | 15.6037 | 16.2561  | 0.6891             |


**Gráfico 1:**

![Grafico1](10k_creacion.png)


### Para 50k datos

### Para 100k datos
