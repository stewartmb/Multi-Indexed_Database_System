# Informe Técnico - Proyecto 1 Base de datos 2

En el presente informe, se presentará el contenido de la primera parte del proyecto del curso de base de datos 2. Se detallará en la implementación de las técnicas de indexación, asi como en los algoritmos propuestos para realizar las operaciones básicas como inserción, búsqueda y eliminación.

Se ha desarrollado un mini gestor de bases de datos que soporta la indexación eficiente de datos multidimensionales, así como la organización de arhivos físicos.

Además, se ha implementado un Parser que estará conectado con una API para realizar consultas SQL, haciendo uso de los índices que se han creado en este repositorio. 

Por último, se creó un frontend donde se puede apreciar la funcionalidad del proyecto. 

## ¿Por qué usar distintos tipos de índices?
El proyecto busca recrear un gestor de bases de datos como PostgreSQL, el cual soporta distintos tipos de indexación. Como se conoce gracias a la teoría, cada técnica de indexación tiene ventajas respecto otras técnicas. Por ejemplo, si buscamos registros dentro de un rango, sería mejor utilizar un índice B+ a que un índice Hash (Hash no sorporta rangeSearch). Es por ello que, para asegurar la eficiencia en nuestro proyecto, se podrán usar distintos índices en la misma tabla. 
Ejemplo:
```bash
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
En la tabla destinos, se han usado distintos tipos de índices: sequential, hash, btree y rtree. 
Como en la tabla haya atributos de distintos tipos (ids, nombres, coordenadas), es conveniente que cada atributo tenga un índice que sea óptimo para dicho atributo.

## Resultados esperados
Se espera que, con la implementación de los índices, las operaciones fundamentales (búsqueda, inserción y eliminación) deberían de tomar menos tiempo computacional que realizando un Full Table Scan, es decir, no usar ningún índice.

## Estructura del proyecto
El proyecto tiene la siguiente estructura:
- Backend: Base de datos, API, Índices, ParserSQL
- Frontend: Interfaz

Para almacenar todos los registros de una tabla, se decidió usar la estructura del [Heap file](https://github.com/stewartmb/Proyecto_BD2/blob/main/Heap_struct/Hepa.md). Sobre esta estructura es donde se aplicarán las técnicas de indexación.
Aparte, se implementó una clase [Registro](https://github.com/stewartmb/Proyecto_BD2/blob/main/Utils/RegistroREADME.md) personalizada.

En cuanto a los **índices**, se han implementado los siguientes:
- Sequential File
- ISAM-Sparse Index (con solo dos niveles)
- Extendible Hashing
- B+ Tree
- Rtree

Además, se implementó una API RESTful en Python que permite:
- Gestionar las tablas creadas y los datos.
- Ejecutar consultas personalizadas desde el ParserSQL.
- Interactuar con el frontend.

# Documentación de las técnicas implementadas (índices, parser y API)
## Sequential File
Ver documentación:
[Sequential File](https://github.com/stewartmb/Proyecto_BD2/blob/main/Sequential_Struct/Sequential.md)
## ISAM File
Ver documentación:
[ISAM](https://github.com/stewartmb/Proyecto_BD2/tree/main/Isam_struct/ISAM.md)
## Hash File
Ver documentación:
[Extendible Hashing](https://github.com/stewartmb/Proyecto_BD2/blob/main/Hash_struct/Hash.md)
## BTree File
Ver documentación:
[BTree File](https://github.com/stewartmb/Proyecto_BD2/blob/main/BPtree_struct/BTree.md)
## RTree File
Ver documentación:
[Rtree](https://github.com/stewartmb/Proyecto_BD2/blob/main/RTree_struct/Rtree.md)
## ParserSQL
Ver documentación:
[ParserSQL](https://github.com/stewartmb/Proyecto_BD2/blob/main/ParserSQL/README.md)
## API
Ver documentación:
[Documentación de la API](https://github.com/stewartmb/Proyecto_BD2/blob/main/API/README.md)



## Autores

Link de github de los autores del proyecto:
- [@melanie1512](https://github.com/melanie1512)
- [@stewartmb](https://github.com/stewartmb)
- [@RodrigoLiC](https://github.com/RodrigoLiC)
- [@JorgeL2005](https://github.com/JorgeL2005)
