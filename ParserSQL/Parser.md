# Parser SQL - Proyecto BD2

Este componente implementa un analizador sintáctico (parser) para un subconjunto del lenguaje SQL utilizando la librería [Lark](https://github.com/lark-parser/lark) en Python.

---

## 📌 Objetivo

El parser permite interpretar las siguientes sentencias SQL y las transformar en estructuras de datos JSON que son usados por la API y el archivo de servicios.py.

---

## 🧱 Lenguaje Soportado

Se soporta un subconjunto del lenguaje SQL con soporte para:

- `CREATE TABLE`, `DROP TABLE`
- `INSERT INTO`, `DELETE FROM`
- `SELECT ... FROM ... WHERE ...`
- `CREATE INDEX`, `DROP INDEX`
- `COPY FROM`

Además:
- Condiciones lógicas: `AND`, `OR`, `NOT`
- Condiciones avanzadas: `BETWEEN`, `CLOSEST`
- Tipos de datos: `int`, `float`, `double`, `bool`, `date`, `timestamp`, `long`, `ulong`, `varchar[n]`
- Tipos de índice: `bptree`, `rtree`, `hash`, `seq`, `isam`, `brin` 


Para más información, puede hacer click [aquí](https://github.com/stewartmb/Proyecto_BD2/blob/main/ParserSQL/Docs.md).

---

## 🧩 Gramática SQL

La gramática está definida en una cadena multilínea `sql_grammar` y usa el parser `LALR` de Lark.

Tokens y producciones incluyen:

```ebnf
?start: stmt+

stmt: create_stmt ";" 
    | select_stmt ";" 
    | insert_stmt ";" 
    | delete_stmt ";"
    | index_stmt ";"
    | copy_stmt ";"
    | drop_index_stmt ";"
    | drop_table_stmt ";"
    | set_stmt ";"

create_stmt: "create"i "table"i NAME "(" create_attr_list ")"
copy_stmt: "copy"i NAME "from"i VALUE
create_attr_list: NAME (TYPE | varchar) [ KEY ] ["index"i INDEX ["(" value_list ")"]] ("," NAME (TYPE | varchar) [ KEY ] ["index"i INDEX ["(" value_list ")"]] )*
select_stmt: "select"i (ALL | attr_list) "from"i NAME ["where"i expr]
attr_list: NAME ("," NAME)*
drop_index_stmt: "drop"i "index"i INDEX "on"i "values"i attr_list "on"i NAME
drop_table_stmt: "drop"i "table"i NAME

index_stmt: "create"i "index"i "on"i NAME "using"i INDEX "(" attr_list ")" [ "params"i "(" value_list ")" ]

insert_stmt: "insert"i "into"i NAME "(" attr_list ")" "values"i "(" value_list ")"
value_list: VALUE ("," VALUE)*

delete_stmt: "delete"i "from"i NAME "where"i expr

?expr: expr "or"i expr     -> or_expr
     | expr "and"i expr    -> and_expr
     | "not"i expr         -> not_expr
     | "(" expr ")"
     | condition

condition: NAME OP VALUE
         | NAME BETWEEN VALUE "and"i VALUE
         | attr_list OP  "[" value_list "]"
         | attr_list BETWEEN  "[" value_list "]" "and"i "[" value_list "]"
         | attr_list "in"i "(" value_list ")" CLOSEST VALUE
         | attr_list "in"i "(" value_list ")" RADIUS VALUE

OP: "==" | "!=" | "<" | ">" | "<=" | ">="
NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
VALUE: "-"? /[0-9]+(\.[0-9]+)?/ | ESCAPED_STRING
INDEX: "rtree"i | "bptree"i | "seq"i | "isam"i | "hash"i | "brin"i
KEY: "primary key"i
BETWEEN: "between"i
CLOSEST: "closest"i
RADIUS: "radius"i
ALL: "*"

TYPE: "int"i | "float"i | "double"i | "date"i | "long"i | "ulong"i | "bool"i | "timestamp"i
varchar: "varchar"i "[" VALUE "]"

```

---

## 🔄 Transformer: SQLTransformer

Se define una clase SQLTransformer que convierte el árbol sintáctico generado por Lark en diccionarios JSON.

Ejemplo básico de lo que devuelve el transformer.
``` json
{
    "action": "action",
    "table": "table_name",
    ...
}
```
En el campo `"action"`, se indica que tipo de query se va a ejecutar. Esto luego es categorizado por la API en su respectiva ejecución. Los distintos tipos de queries tienen más campos únicos a ellos, que indican información requerida para su ejecución.

Se resalta el manejo de las condiciones en el caso de las queries de `SELECT` y `DELETE`. Para mantener el orden en el que deben ser ejecutadas las consultas booleanas, lo convertimos a un string y añadimos un mapa con la relación de condiciones. Un ejemplo se puede ver en lo siguiente:

``` json

{
    "action": "select",
    "table": "clientes",
    "attr": ["nombre", "edad"],
    "eval": "(0 and 1)",
    "conditions": {
        0: {"field": "edad", "op": ">", "range_search": true, "range_start": 30, "range_end": 1},
        1: {"field": "nombre", "op": "==", "range_search": false, "value": "Juan"}
    }
}
```

---

## 📈 Futuras mejoras
- Se podría implementar un soporte para UPDATE.
- Actualmente, el parser no soporta subqueries.