# Explicación del funcionamiento de MultimediaImageRetrieval

## Resumen General

La clase `MultimediaImageRetrieval` implementa un sistema de recuperación de imágenes basado en el modelo Bag of Visual Words (BoVW) y TF-IDF, utilizando almacenamiento en archivos binarios tipo heap. El índice trabaja sobre un archivo heap principal (`data_file`) que contiene todos los atributos de la tabla, incluyendo la ruta de la imagen, y un heap de índice que almacena la posición, el nombre y el vector tf-idf de cada imagen.

---

## Flujo de Trabajo

### 1. Inicialización

- El constructor recibe el formato de la tabla principal (`table_format`), la clave primaria (`key`), el archivo de datos principal (`data_file_name`), el archivo del índice (`index_file_name`), el directorio base y parámetros como el tamaño de redimensión (`z`) y el número de clusters (`n_clusters`).
- Se crean dos heaps:
  - **Heap principal** (`self.HEAP`): almacena todos los registros de la tabla, incluyendo la ruta de la imagen.
  - **Heap del índice** (`self.index_heap`): almacena, para cada imagen indexada, la posición en el heap principal, el nombre de la imagen y su vector tf-idf.

---

### 2. Inserción de imágenes

- El método `insert(self, pos)` recibe la **posición** de un registro en el heap principal.
- Obtiene la ruta de la imagen usando esa posición.
- Redimensiona la imagen y la guarda en una carpeta de imágenes reescaladas.
- Extrae los descriptores SIFT y los agrega a un archivo `.npz` de descriptores.
- Actualiza el vocabulario visual (KMeans) con todos los descriptores.
- Calcula el histograma BoVW de la nueva imagen y lo agrega a un archivo `.npz` de histogramas.
- Actualiza el archivo de vectores tf-idf.
- Inserta en el heap del índice un registro con la posición, el nombre y el vector tf-idf de la imagen.

---

### 3. Búsqueda KNN

- El método `knn_search(self, pos, k=3)` recibe la posición de una imagen en el heap principal.
- Obtiene la ruta de la imagen, la redimensiona y extrae sus descriptores.
- Calcula el histograma y el vector tf-idf de la imagen de consulta.
- Compara este vector con los vectores tf-idf de todas las imágenes indexadas usando similitud de coseno.
- Devuelve las posiciones en el heap principal de las `k` imágenes más similares.

---

### 4. Creación masiva (`creacion`)

- El método `creacion` procesa todas las imágenes de una carpeta:
  - Redimensiona todas las imágenes.
  - Extrae y guarda los descriptores de todas.
  - Crea el vocabulario visual.
  - Calcula los histogramas y los vectores tf-idf.
  - Inserta en el heap del índice la posición, nombre y vector tf-idf de cada imagen, buscando la posición en el heap principal por el nombre de la imagen.

---

### 5. Mostrar el heap

- El método `mostrar_heap` imprime los primeros registros del heap del índice, mostrando la posición, el nombre y los primeros valores del vector tf-idf.

---


# Procesamiento de imágenes
El procesamiento de imágenes se hace mediante una serie de pasos.

## Redimensionamiento de imágenes
Cada imagen pasará por la función `resize_to_256_square()`, que lo que hace es redimensionar la imagen a un tamaño fijo (puede ser 256x256 o 512x512).
Esto se realizó para que todas las imágenes tengan el mismo tamaño y que tengan un tamaño aproximado de descriptores locales.

## Extracción de descriptores locales
Para extraer descriptores locales de una imagen, se utilizó la librería `SIFT` de OpenCV. Lo que se hace es que para una imagen, se obtiene una matriz de descriptores locales y keypoints. Cada fila representa un keypoint de la imagen y cada fila tiene un vector de descriptores locales para ese keypoint. El vector de descriptores tiene un tamaño fijo de 128 dimensiones. Este vector puede ser redimensionado usando PCA.

```
all_descriptors.npz:

Este archivo almacena, para cada imagen, una matriz de descriptores SIFT 
(cada fila es un descriptor, cada columna una dimensión, normalmente 128 
o menos si se usa PCA):

{
  "auto_0001_reescalado": [
    [0.12, 0.34, ..., 0.56],   // Descriptor 1 de la imagen
    [0.22, 0.14, ..., 0.11],   // Descriptor 2 de la imagen
    ...
    [0.05, -0.09, ..., 0.27]   // Descriptor N de la imagen
  ],
  "auto_0002_reescalado": [
    [0.18, 0.21, ..., 0.33],
    ...
  ],
  ...
}

Clave: nombre base de la imagen.
Valor: matriz de descriptores (cada uno de longitud 128 o la dimensión que se use).
```
## Creación del BoVW

El núcleo del BoVW es el vocabulario visual, que consiste en un conjunto de "palabras visuales" (clusters) que representan patrones recurrentes en los descriptores. Para crearlo, se utiliza el algoritmo MiniBatchKMeans, una versión eficiente de K-Means que procesa los datos en lotes.

- Entrada: Todos los descriptores de todas las imágenes apilados en una matriz.

- Proceso: Se agrupan los descriptores en n_clusters clusters (por defecto, 1000). Cada cluster centroide representa una "palabra visual".

- Salida: Un modelo K-Means entrenado, que se guarda en disco (visual_dictionary.pkl) para reutilización.

```
visual_dictionary:

{
  "n_clusters": 1000,
  "centers": [
    [0.12, -0.34, 0.56, ..., 0.01],  // Centro del cluster 0 (vector de dimensión igual a la de los descriptores)
    [0.22, 0.14, -0.26, ..., -0.11], // Centro del cluster 1
    ...
    [0.05, -0.09, 0.33, ..., 0.27]   // Centro del cluster 999
  ]
}


n_clusters: Número de palabras visuales (clusters).

centers: Lista de listas, cada una es el vector centroide de un cluster (palabra visual), 
de dimensión igual a la de los descriptores SIFT (por ejemplo, 128 o menos si se usa PCA).
```

## Creación de vector de histogramas
Una vez creado el vocabulario, cada imagen se representa como un histograma de frecuencias de las palabras visuales:

- Para cada imagen, se predicen las palabras visuales asignando sus descriptores al cluster más cercano usando kmeans.predict().

- Se cuenta cuántos descriptores pertenecen a cada cluster, generando un histograma de tamaño n_clusters.

- Estos histogramas se guardan en un archivo .npz (all_histograms.npz).

```
all_histograms.npz:

Este archivo almacena, para cada imagen, 
el histograma BoVW (vector de longitud igual al número de clusters):

{
  "auto_0001_reescalado": [5, 0, 1, 2, ..., 0],  // Frecuencia de cada palabra visual (cluster)
  "auto_0002_reescalado": [2, 1, 0, 3, ..., 1],
  ...
}

Clave: nombre base de la imagen.
Valor: vector (arreglo) de enteros, 
cada uno indica cuántos descriptores de la imagen cayeron en ese cluster.
```

## Ponderación TF-IDF

Finalmente, para cada una de las imagenes, se calcula el tf-idf. 

```
all_tfidf:

La representación conceptual de all_tfidf.npz es muy similar a la de all_histograms.npz, 
pero en vez de guardar frecuencias de palabras visuales, 
guarda los vectores TF-IDF normalizados para cada imagen.

{
  "auto_0001_reescalado": [0.12, 0.00, 0.08, 0.15, ..., 0.00],  // Vector TF-IDF normalizado para la imagen 1
  "auto_0002_reescalado": [0.05, 0.11, 0.00, 0.09, ..., 0.03],  // Vector TF-IDF normalizado para la imagen 2
  ...
}

Clave: nombre base de la imagen.
Valor: vector TF-IDF normalizado (float), 
de longitud igual al número de clusters (palabras visuales).

```



