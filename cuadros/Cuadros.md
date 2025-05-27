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
 bla bla bla 



 ## Prueba 3: Tiempo de búsqueda por rango de los índices

Primero, se realizó la creación de la data con un total de 10k, 50k y 100k registros. 

El siguiente experimento consiste en que, de la data, se elige aleatoriamente un rango y se procede a usar todos los índices para buscar dicho rango. El R-tree tiene 3 funciones que buscan dado un rango, por lo que para estas 3 funciones se eligieron rangos espaciales.

Los experimentos se realizaron un total de 100 veces. Se sacó el tiempo máximo y mínimo, el tiempo promedio y la desviación estándar.

### Para 10k

**Cuadro 1:**



| Índice             | Máximo   | Mínimo   | Promedio | Desviación Estándar |
|------------------------|----------|----------|----------|----------------------|
| **heap**               | 26.9928  | 20.8769  | 21.5296  | 0.6289               |
| **bptree**             | 12.1050  | 0.1438   | 5.9454   | 3.4346               |
| **hash**               | 262.8202 | 184.2222 | 196.4279 | 12.9245              |
| **sequential**         | 1.4780   | 0.1762   | 0.2560   | 0.1298               |
| **isam**               | 1.1051   | 0.0720   | 0.1182   | 0.1344               |
| **brin**               | 0.2930   | 0.0701   | 0.0874   | 0.0225               |
| **rtree_point_to_point** | 7.0190 | 1.3680   | 3.2386   | 0.8987               |
| **rtree_knn**          | 16.6841  | 3.4418   | 10.5534  | 2.3755               |
| **rtree_radio**        | 9.2432   | 2.4409   | 5.9142   | 1.4445               |


**Gráfico 1:**

![Grafico1](10k_RS.png)

### Para 50k

**Cuadro 2:**



| Índice             | Máximo   | Mínimo   | Promedio | Desviación Estándar |
|------------------------|----------|----------|----------|----------------------|
| **heap**               | 128.5312 | 106.2160 | 108.3308 | 2.2024               |
| **bptree**             | 13.0410  | 0.0668   | 1.3171   | 2.9216               |
| **hash**               | 211.9560 | 183.4760 | 190.0892 | 5.2127               |
| **sequential**         | 1.9648   | 0.1669   | 0.3020   | 0.1745               |
| **isam**               | 1.0121   | 0.0851   | 0.1638   | 0.1478               |
| **brin**               | 0.2339   | 0.0689   | 0.0859   | 0.0249               |
| **rtree_point_to_point** | 9.1083 | 1.6260   | 3.1636   | 1.0839               |
| **rtree_knn**          | 15.5158  | 3.3863   | 9.3521   | 2.7005               |
| **rtree_radio**        | 10.1259  | 3.1421   | 5.9650   | 1.5833               |


**Gráfico 2:**

![Grafico1](50k_RS.png)

### Para 100k

**Cuadro 3:**


| Índice             | Máximo   | Mínimo   | Promedio | Desviación Estándar |
|------------------------|----------|----------|----------|----------------------|
| **heap**               | 219.5749 | 210.7370 | 214.3201 | 1.4923               |
| **bptree**             | 12.7239  | 0.0691   | 0.8215   | 2.7184               |
| **hash**               | 247.9300 | 184.1941 | 194.4659 | 11.1113              |
| **sequential**         | 1.4760   | 0.2031   | 0.2908   | 0.1222               |
| **isam**               | 0.6952   | 0.0961   | 0.1748   | 0.0779               |
| **brin**               | 0.1931   | 0.0770   | 0.0828   | 0.0117               |
| **rtree_point_to_point** | 6.3679 | 1.1740   | 3.0954   | 0.9713               |
| **rtree_knn**          | 15.6000  | 3.5222   | 9.6166   | 2.4041               |
| **rtree_radio**        | 9.3052   | 2.2810   | 5.5537   | 1.6455               |



**Gráfico 3:**

![Grafico1](100k_RS.png)

### Análisis de los resultados:
bla bla bla


