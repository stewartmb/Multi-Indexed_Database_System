
# 📘 Lenguaje SQL Personalizado - Documentación

Este documento describe la gramática, sintaxis y uso del lenguaje SQL personalizado soportado por el sistema. Este lenguaje permite operaciones de definición y manipulación de datos, así como configuración de índices.

---

## 📌 Índice

1. [Instrucciones Soportadas](#instrucciones-soportadas)  
2. [CREATE TABLE](#create-table)  
3. [INSERT INTO](#insert-into)  
4. [SELECT](#select)  
5. [DELETE](#delete)  
6. [COPY](#copy)  
7. [DROP INDEX](#drop-index)  
8. [DROP TABLE](#drop-table)  
9. [CREATE INDEX](#create-index)  
10. [SET PARAMS](#set-params)  
11. [Expresiones WHERE](#expresiones-where)  
12. [Tipos de Datos](#tipos-de-datos)  
13. [Índices Soportados](#índices-soportados)  
14. [Parámetros por Tipo de Índice](#parámetros-por-tipo-de-índice)

---

## 🧱 Instrucciones Soportadas

Las siguientes instrucciones están disponibles y deben terminar en punto y coma (`;`):

- `CREATE TABLE`
- `INSERT INTO`
- `SELECT`
- `DELETE`
- `COPY`
- `DROP INDEX`
- `DROP TABLE`
- `CREATE INDEX`
- `SET PARAMS`

---

## 🏗️ CREATE TABLE

```sql
CREATE TABLE nombre_tabla (
    nombre_columna tipo_dato [PRIMARY KEY] [INDEX tipo_indice [(valores)]],
    ...
);
```

- Se pueden definir múltiples columnas separadas por comas.
- Cada columna puede tener opcionalmente:
  - `PRIMARY KEY`: para clave primaria.
  - `INDEX tipo_indice`: para definir un índice.
  - `INDEX tipo_indice (valores)`: para índices con parámetros.

**Ejemplo:**
```sql
CREATE TABLE productos (
    id int PRIMARY KEY index hash,
    nombre varchar[255],
    precio float index bptree (16)
);
```

---

## 📥 INSERT INTO

```sql
INSERT INTO nombre_tabla (col1, col2, ...) VALUES (val1, val2, ...);
```

**Ejemplo:**
```sql
INSERT INTO productos (id, nombre, precio) VALUES (1, "Jabón", 3.5);
```

---

## 🔍 SELECT

```sql
SELECT * FROM nombre_tabla;
SELECT col1, col2 FROM nombre_tabla WHERE condición;
```

---

## 🗑️ DELETE

```sql
DELETE FROM nombre_tabla WHERE condición;
```

---

## 📤 COPY

```sql
COPY nombre_tabla FROM valor;
```

---

## ❌ DROP INDEX

```sql
DROP INDEX tipo_indice ON VALUES (col1, col2, ...) ON nombre_tabla;
```

---

## ❌ DROP TABLE

```sql
DROP TABLE nombre_tabla;
```

---

## 📚 CREATE INDEX

```sql
CREATE INDEX ON nombre_tabla USING tipo_indice (col1, col2, ...) [PARAMS (val1, val2, ...)];
```

---

## ⚖️ Expresiones WHERE

Las expresiones `WHERE` pueden combinar condiciones con:

- `AND`, `OR`, `NOT`
- Operadores: `==`, `!=`, `<`, `>`, `<=`, `>=`
- `BETWEEN`, `IN`, `CLOSEST`, `RADIUS`

---

## 📏 Tipos de Datos

- `int`
- `float`
- `double`
- `date`
- `long`
- `ulong`
- `bool`
- `timestamp`
- `varchar[n]`

---

## 🧮 Índices Soportados

- `rtree`
- `bptree`
- `seq`
- `isam`
- `hash`
- `brin`

---

## ⚙️ Parámetros por Tipo de Índice

A continuación se describe qué parámetros específicos puede aceptar cada tipo de índice. Esta sección debe ser completada según la implementación del sistema.

### 📦 `rtree`
- No toma parámetros.

### 📦 `bptree`
- Parámetros esperados:
  - `max_num_child`: máxima cantidad de hijos que puede tener por page, 100 por default

### 📦 `seq`
- Parámetros esperados:
  - `num_aux`: máxima cantidad del aux antes que se haga merge, 100 default.

### 📦 `isam`
- No toma parámetros.

### 📦 `hash`
- Parámetros esperados:
  - `global depth`: profundidad global, 16 por default.
  - `max_records_per_bucket`: cantidad máxima de registros por bucket, 4 por default.

### 📦 `brin`
- Parámetros esperados:
  - `max_num_pages`: cantidad máxima de páginas, 30 por default.
  - `max_num_keys`: cantidad máxima de llaves, 40 por default.


# 📗 Expresiones Condicionales en el Lenguaje SQL Personalizado

Esta sección detalla el uso de expresiones condicionales en cláusulas `WHERE`, permitiendo realizar filtrado de datos según distintas lógicas y operadores.

---

## 🔁 Operadores Lógicos

### `AND`
Permite combinar dos condiciones que deben cumplirse simultáneamente.

**Ejemplo:**
```sql
SELECT * FROM productos WHERE precio > 10 AND stock > 0;
```

### `OR`
Permite combinar condiciones donde al menos una debe cumplirse.

**Ejemplo:**
```sql
SELECT * FROM productos WHERE precio < 5 OR nombre == "Desinfectante";
```

### `NOT`
Niega una condición.

**Ejemplo:**
```sql
SELECT * FROM productos WHERE NOT precio > 100;
```

---

## ⚖️ Operadores de Comparación

| Operador | Significado            |
|----------|------------------------|
| `==`     | Igual a                |
| `!=`     | Distinto de            |
| `<`      | Menor que              |
| `>`      | Mayor que              |
| `<=`     | Menor o igual que      |
| `>=`     | Mayor o igual que      |

**Ejemplo:**
```sql
SELECT * FROM empleados WHERE edad >= 30;
```

---

## 🔲 BETWEEN

Evalúa si un valor (o conjunto de valores) se encuentra dentro de un rango determinado.

### Para columnas simples:
```sql
SELECT * FROM productos WHERE precio BETWEEN 10 AND 50;
```

### Para consultas multidimensionales (rangos rectangulares):
```sql
SELECT * FROM destinos WHERE latitude, longitud BETWEEN (1, 1) AND (3, 3);
```

Este último ejemplo selecciona puntos dentro del rectángulo definido por las coordenadas `(1,1)` y `(3,3)`.

---

## 🔍 IN

### Uso tradicional:
Evalúa si un valor está contenido en una lista.

```sql
SELECT * FROM productos WHERE nombre IN ("Jabón", "Shampoo");
```

---

## 📍 Consultas Espaciales

Estas condiciones permiten realizar búsquedas espaciales en índices multidimensionales (como R-Trees).

---

### ✅ KNN (Consulta por Vecinos Más Cercanos) — `CLOSEST`

```sql
SELECT * FROM destinos WHERE latitude, longitud IN (5, 6) CLOSEST 5;
```

- Devuelve los **5 puntos más cercanos** al punto `(5,6)`.
- Es útil para recomendaciones, proximidad geográfica o análisis de similitud espacial.

---

### 🌀 Consulta por Radio — `RADIUS`

```sql
SELECT * FROM destinos WHERE latitude, longitud IN (5, 6) RADIUS 5;
```

- Devuelve **todos los puntos ubicados a una distancia menor o igual a 5** del punto `(5,6)`.
- Útil para áreas de cobertura, zonas de influencia o detección de eventos cercanos.

---
