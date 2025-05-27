# 📘 Informe Técnico – Proyecto 1: Base de Datos 2

Este informe presenta la **primera parte del proyecto** del curso **Base de Datos 2**, enfocándose en la implementación de técnicas de **indexación**, así como en los algoritmos desarrollados para operaciones fundamentales como:

- 📥 Inserción  
- 🔍 Búsqueda  
- ❌ Eliminación  

Se ha desarrollado un **mini gestor de bases de datos** que:

- Soporta indexación eficiente de datos **multidimensionales**
- Administra la organización de **archivos físicos**
- Incluye un **Parser SQL** conectado a una API
- Presenta un **frontend interactivo** para demostrar la funcionalidad

---

## ❓ ¿Por qué usar distintos tipos de índices?

Inspirado en gestores como **PostgreSQL**, este proyecto implementa diversos tipos de índices, ya que **cada técnica tiene sus fortalezas** dependiendo del caso de uso.

> 🔑 *Ejemplo*: Para búsquedas por rango, un índice **B+ Tree** es más eficiente que uno de tipo **Hash** (que no soporta `rangeSearch`).

### 🧪 Ejemplo SQL

```sql
create table destinos (
    id int primary key index hash,
    name varchar[25] index seq,
    latitud double,
    longitud double,
    ciudad varchar[20] index btree,
    pais varchar[20]
);
create index on destinos using rtree(latitud, longitud);
```
🔎 En este ejemplo se combinan:
- `hash` para identificadores
- `seq` para nombres
- `btree` para textos ordenables
- `rtree` para coordenadas espaciales

Como la tabla tiene atributos de distintos tipos (IDs, nombres, coordenadas), se asigna a cada uno el índice más óptimo según su naturaleza.

## 🎯 Resultados Esperados
Se espera que, con la implementación de los índices, las operaciones fundamentales (búsqueda, inserción y eliminación) deberían de tomar menos tiempo computacional que realizando un Full Table Scan, es decir, no usar ningún índice.

## 🧱 Estructura del Proyecto
El proyecto está estructurado en dos grandes partes:
```
📦 Proyecto_BD2/
│
├── 🔙 Backend
│   ├── Base de datos
│   ├── Índices (5 tipos)
│   ├── ParserSQL
│   └── API RESTful
│
├── 💻 Frontend
│   └── Interfaz de usuario
```

Para almacenar todos los registros de una tabla, se decidió usar la estructura del [Heap file](https://github.com/stewartmb/Proyecto_BD2/blob/main/Heap_struct/Hepa.md). Sobre esta estructura es donde se aplicarán las técnicas de indexación.
Aparte, se implementó una clase [Registro](https://github.com/stewartmb/Proyecto_BD2/blob/main/Utils/RegistroREADME.md) personalizada.

## 📂 Índices Implementados
En cuanto a los **índices**, se han implementado los siguientes:

| Tipo de Índice         | Descripción                                         | Documentación                                                                              |
| ---------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 📄 Sequential File     | Búsqueda ordenada secuencial                        | [Ver](https://github.com/stewartmb/Proyecto_BD2/blob/main/Sequential_Struct/Sequential.md) |
| 🗂 ISAM (Sparse Index) | Índice jerárquico con dos niveles                   | [Ver](https://github.com/stewartmb/Proyecto_BD2/tree/main/Isam_struct/ISAM.md)             |
| #️⃣ Extendible Hashing | Hash dinámico para inserciones eficientes           | [Ver](https://github.com/stewartmb/Proyecto_BD2/blob/main/Hash_struct/Hash.md)             |
| 🌳 B+ Tree             | Árbol balanceado para búsquedas por rango           | [Ver](https://github.com/stewartmb/Proyecto_BD2/blob/main/BPtree_struct/BTree.md)          |
| 🗺 R-Tree              | Índice espacial para coordenadas multidimensionales | [Ver](https://github.com/stewartmb/Proyecto_BD2/blob/main/RTree_struct/Rtree.md)           |


## 🧠 Parser SQL
Se ha desarrollado un componente ParserSQL que interpreta y ejecuta sentencias SQL básicas, utilizando los índices implementados.
[ParserSQL](https://github.com/stewartmb/Proyecto_BD2/blob/main/ParserSQL/Parser.md)

## 🔌 API RESTful
La API desarrollada en Python permite:

- Crear y gestionar tablas

- Insertar, buscar y eliminar datos

- Ejecutar consultas a través del ParserSQL

- Interactuar con el frontend

[Documentación de la API](https://github.com/stewartmb/Proyecto_BD2/blob/main/API/README.md)


## 🌐 Frontend
Se ha creado una interfaz web sencilla e intuitiva para:

- Visualizar las tablas y los datos almacenados

- Ejecutar comandos SQL desde el navegador

- Ver los resultados en tiempo real

## 📈 Experimentos y Resultados experimentales

Para probar la eficiencia de todos los índices, se han realizados pruebas con distintos volúmenes de datos.

Cabe recalcar que los dataset que hemos utilizado para las pruebas han sido generados por nosotros mismos. Esta decisión fue tomada para realizar las pruebas de los índices en el mismo dataset y aplicándolos en el mismo atributo, asi se podrá analizar mejor los resultados.

Los tamaños de los dataset son de: 10k, 50k y 100k.

### Métricas
- Tiempo de ejecución en ms
- Accesos a Memoria Secundaria

## Cuadros Comparativos de Desempeño, Gráficos y Resultados

[Ver aquí](https://github.com/stewartmb/Proyecto_BD2/blob/main/cuadros/Cuadros.md)


## 👥 Autores

| Nombre  | GitHub                                         |
| ------- | ---------------------------------------------- |
| Melanie Cortez | [@melanie1512](https://github.com/melanie1512) |
| Stewart Maquera | [@stewartmb](https://github.com/stewartmb)     |
| Rodrigo Li | [@RodrigoLiC](https://github.com/RodrigoLiC)   |
| Jorge Leon | [@JorgeL2005](https://github.com/JorgeL2005)   |
