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