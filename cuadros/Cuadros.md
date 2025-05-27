# Cuadros comparativos de desempeño y Gráficos resultantes
En esta sección se mostraran los cuadros comparativos de las pruebas realizadas para analizar la eficiencia de los índices.

## Prueba 1: Tiempo de creación de los índices

Primero, se realizó la creación de la data con un total de 10k, 50k y 100k registros. 

Posteriormente, se realizó la medición del tiempo en que demora la creación de todos los índices sobre los datasets creados. 

Los experimentos se realizaron un total de 10 veces. Se sacó el tiempo máximo y mínimo, el tiempo promedio y la desviación estándar.

### Para 10k datos


**Cuadro 1:**


| Índice  | Máximo  | Mínimo  | Promedio | Desviación Estándar |
|--------------|---------|---------|----------|----------------------|
| **heap**     | 1.1552  | 0.7855  | 0.8731   | 0.0977               |
| **bptree**   | 1.8730  | 1.5849  | 1.6497   | 0.0864               |
| **hash**     | 2.7562  | 2.4452  | 2.5259   | 0.0888               |
| **sequential**| 13.6686 | 12.6166 | 12.9852  | 0.3435               |
| **isam**     | 1.0444  | 0.6843  | 0.8017   | 0.0903               |
| **brin**     | 2.6176  | 2.0207  | 2.2080   | 0.1659               |
| **rtree**    | 16.1120 | 15.1551 | 15.6448  | 0.2726               |



**Gráfico 1:**

![Grafico1](10k_creacion.png)


## Para 50k datos

**Cuadro 2:**



| Índice   | Máximo  | Mínimo  | Promedio | Desviación Estándar |
|--------------|---------|---------|----------|----------------------|
| **heap**     | 4.4133  | 0.7714  | 2.3518   | 1.8331               |
| **bptree**   | 1.6583  | 1.5614  | 1.5869   | 0.0298               |
| **hash**     | 2.5319  | 2.4235  | 2.4672   | 0.0340               |
| **sequential**| 13.2518 | 12.6458 | 12.9419  | 0.2107               |
| **isam**     | 4.2747  | 0.1599  | 1.8330   | 1.7540               |
| **brin**     | 2.3651  | 2.0002  | 2.1657   | 0.1283               |
| **rtree**    | 16.8225 | 15.3492 | 15.9139  | 0.5156               |



**Gráfico 2:**

![Grafico1](50k_creacion.png)

## Para 100k datos

**Cuadro 3:**


| Índice   | Máximo  | Mínimo  | Promedio | Desviación Estándar |
|--------------|---------|---------|----------|----------------------|
| **heap**     | 8.5390  | 0.8173  | 3.7171   | 3.8909               |
| **bptree**   | 1.7211  | 1.5699  | 1.6230   | 0.0490               |
| **hash**     | 2.5803  | 2.4541  | 2.4884   | 0.0463               |
| **sequential**| 13.1378 | 12.8701 | 12.9502  | 0.0890               |
| **isam**     | 8.1527  | 0.1676  | 2.5018   | 3.4176               |
| **brin**     | 2.4801  | 2.0721  | 2.2217   | 0.1340               |
| **rtree**    | 17.0213 | 15.5345 | 16.0672  | 0.5454               |


**Gráfico 3:**

![Grafico1](100k_creacion.png)

**Análisis de los resultados:**

bla bla bla

## Prueba 2: Tiempo de búsqueda de los índices

Primero, se realizó la creación de la data con un total de 10k, 50k y 100k registros. 

El experimento consiste en que, de la data, se elige aleatoriamente un valor y se usan los índices para buscarlo. El único índice que elige uno distinto es el R-Tree, ya que solo trabaja con índices espaciales.

Los experimentos se realizaron un total de 100 veces. Se sacó el tiempo máximo y mínimo, el tiempo promedio y la desviación estándar.


### Para 10k datos

**Cuadro 1:**


| Índice   | Máximo  | Mínimo  | Promedio | Desviación Estándar |
|--------------|---------|---------|----------|----------------------|
| **heap**     | 77.6799 | 20.9570 | 22.8878  | 5.9423               |
| **bptree**   | 12.5291 | 0.1669  | 6.0920   | 3.5255               |
| **hash**     | 2.3029  | 0.3219  | 0.3957   | 0.2059               |
| **sequential**| 4.9536 | 0.1791  | 0.3439   | 0.5765               |
| **isam**     | 9.0532  | 0.0901  | 0.2693   | 0.9216               |
| **brin**     | 0.8597  | 0.1709  | 0.2238   | 0.0987               |
| **rtree**    | 7.1070  | 1.2891  | 3.0567   | 0.8668               |


**Gráfico 1:**

![Grafico1](10k_search.png)


### Para 50k datos

**Cuadro 2:**


| Índice   | Máximo   | Mínimo  | Promedio | Desviación Estándar |
|--------------|----------|---------|----------|----------------------|
| **heap**     | 130.3728 | 103.8802| 106.4127 | 3.0323               |
| **bptree**   | 13.1109  | 0.0620  | 1.4266   | 3.1658               |
| **hash**     | 2.4242   | 0.3359  | 0.4321   | 0.2262               |
| **sequential**| 1.3051  | 0.1709  | 0.2654   | 0.1084               |
| **isam**     | 1.0371   | 0.0999  | 0.1792   | 0.1436               |
| **brin**     | 1.0898   | 0.0708  | 0.1279   | 0.1425               |
| **rtree**    | 6.1738   | 1.6038  | 2.8371   | 0.8836               |


**Gráfico 2:**

![Grafico1](50k_search.png)

### Para 100k datos

**Cuadro 3:**


| Índice   | Máximo   | Mínimo  | Promedio | Desviación Estándar |
|--------------|----------|---------|----------|----------------------|
| **heap**     | 279.1712 | 209.3751| 214.6863 | 8.6746               |
| **bptree**   | 13.4051  | 0.0639  | 0.7753   | 2.6238               |
| **hash**     | 7.5009   | 0.3290  | 0.8703   | 1.3409               |
| **sequential**| 3.9210  | 0.2072  | 0.4883   | 0.5104               |
| **isam**     | 0.6797   | 0.1168  | 0.2212   | 0.0762               |
| **brin**     | 0.6790   | 0.0761  | 0.1228   | 0.0972               |
| **rtree**    | 6.1681   | 1.2310  | 2.6929   | 0.9718               |



**Gráfico 3:**

![Grafico1](100k_search.png)


**Análisis de los resultados:**
