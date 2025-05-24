import json
import os
import sys
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Format_Meta import *
from Utils.file_format import *
from Heap_struct.Heap import *

from Hash_struct.Hash import Hash
from BPtree_struct.Indice_BPTree_file import BPTree as Btree
from Sequential_Struct.Indice_Sequential_file import Sequential
from RTree_struct.RTreeFile_Final import RTreeFile as Rtree


M = 10



def to_struct(type):
    varchar_match = re.match(r"varchar\[(\d+)\]", type)

    if type == "int":
        return "i"
    if type == "double":
        return "d"
    elif varchar_match:
        size = varchar_match.group(1)  # Extraemos el tamaño entre los corchetes
        return f"{size}s"
    else:
        print("ERROR: tipo no soportado")
        return None

def parse_select(tokens: list):
    def helper(pos):
        if tokens[pos] == '(':
            pos += 1
            if tokens[pos] == 'NOT':
                op = tokens[pos]
                pos += 1
                operand, pos = helper(pos)
                assert tokens[pos] == ')'
                return (op, operand), pos + 1
            else:
                left, pos = helper(pos)
                op = tokens[pos]
                pos += 1
                right, pos = helper(pos)
                assert tokens[pos] == ')'
                return (op, left, right), pos + 1
        elif tokens[pos].isdigit():
            return int(tokens[pos]), pos + 1
        else:
            raise ValueError("Unexpected token: " + tokens[pos])
    tree, _ = helper(0)
    return tree

def evaluate_select(node, sets, universe):
    if isinstance(node, int):
        return sets[node]
    elif isinstance(node, tuple):
        op = node[0]
        if op == 'NOT':
            child = evaluate_select(node[1], sets, universe)
            return universe - child
        elif op == 'AND':
            return evaluate_select(node[1], sets, universe) & evaluate_select(node[2], sets, universe)
        elif op == 'OR':
            return evaluate_select(node[1], sets, universe) | evaluate_select(node[2], sets, universe)
        else:
            raise ValueError("Unknown operator: " + op)

def convert(query):
    print(json.dumps(query, indent=2))
    if query["action"] == "create_table":
        create_table(query)
    elif query["action"] == "insert":
        insert(query)
    elif query["action"] == "select":
        select(query)
    elif query["action"] == "delete":
        print("Z")
    elif query["action"] == "index":
        create_index(query)
    elif query["action"] == "copy":
        print("B")
    else:
        print("error")

def create_table(query):
    # crear tabla y añadir a metadata
    with open(table_filename(query["name"]), "w") as f:
        pass
    create_meta(query["data"], query["name"])
    format = {}
    cols = query["data"]["columns"]
    for key in cols.keys():
        format[key] = to_struct(cols[key]["type"])

    # crear indices
    for key in cols.keys():
        index = cols[key]["index"]
        if index == None:
            pass
        elif index == "hash":
            hash = Hash(format,
                        key,
                        index_filename(query["name"], key, "buckets"),
                        index_filename(query["name"], key, "index"),
                        table_filename(query["name"]))
        elif index == "seq":
            seq = Sequential(format,
                        key,
                        index_filename(query["name"], key, "index"),
                        table_filename(query["name"]))

        elif index == "btree":
            btree = Btree(format,
                            key,
                            index_filename(query["name"], key, "index"),
                            table_filename(query["name"]),
                            M)

        else:
            print("INDICE NO IMPLEMENTADO AUN")

def insert(query):
    nombre_tabla = query["table"]
    data =  select_meta(nombre_tabla)
    format = {}
    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    # insertar en tabla
    heap = Heap(format,
                data["key"],
                table_filename(nombre_tabla))

    position = heap.insert(query["values"][1])

    # insertar en cada indice si existe
    for key in data["columns"].keys():
        index = data["columns"][key]["index"]
        if index == None:
            pass
        elif index == "hash":
            hash = Hash(format,
                        key,
                        index_filename(nombre_tabla, key, "buckets"),
                        index_filename(nombre_tabla, key, "index"),
                        table_filename(nombre_tabla))

            hash.insert(query["values"][1], position)
        elif index == "seq":
            seq = Sequential(format,
                        key,
                        index_filename(nombre_tabla, key, "index"),
                        table_filename(nombre_tabla))

            seq.add(position)

        elif index == "btree":
            print("OLA soy un btree")
            print()
            btree = Btree(format,
                            key,
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla),
                            M)
            btree.add(pos_new_record=position)

    # indice compuesto en rtree, añadir en el indice
    rtree_keys = data.get("indexes", {}).get("rtree")
    if rtree_keys is not None:
        rtree = Rtree(format, 
                    data["key"],
                    rtree_keys, 
                    table_filename(nombre_tabla),  
                    index_filename(nombre_tabla, *rtree_keys, "index"))
        rtree.insert(query["values"][1], position)

def create_index(query):
    nombre_tabla = query["table"]
    data = select_meta(nombre_tabla)
    format = {}

    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    for key in query["attr"]:
        data["columns"][key]["index"] = query["index"]
    
    create_meta(data, nombre_tabla)
    
    keys = query["attr"]

    hash = None
    seq = None
    rtree = None

    index = query["index"]
    if index == None:
        pass
    elif index == "hash":
        hash = Hash(format,
                    keys[0],
                    index_filename(nombre_tabla, keys[0], "buckets"),
                    index_filename(nombre_tabla, keys[0], "index"),
                    table_filename(nombre_tabla))

    elif index == "seq":
        seq = Sequential(format,
                    key,
                    index_filename(nombre_tabla, keys[0], "index"),
                    table_filename(nombre_tabla))
    
    elif index == "rtree":
        rtree = Rtree(format, 
                        data["key"],
                        keys, 
                        table_filename(nombre_tabla),  
                        index_filename(nombre_tabla, *keys, "index"))
        if "indexes" not in data:
            data["indexes"] = {}

        data["indexes"]["rtree"] = keys
    
    else:
        print("INDICE NO IMPLEMENTADO AUN")
    
    create_meta(data, nombre_tabla)


def select(query):
    # TODO: TEMPORAL BEGIN
    query = {
        "action": "select",
        "table": "users",
        "attr": "*",
        "operations": "(0 AND ((1 OR (NOT 3)) AND (NOT 2)))",
        "conditions": [
            {
                "field": "id",
                "range_search": True,
                "range_start": 103,
                "range_end": 10000
            },
            {
                "field": "name",
                "range_search": True,
                "range_start": "L",
                "range_end": '\U0010FFFF'*256
            },
            {
                "field": "name",
                "range_search": True,
                "range_start": "",
                "range_end": "M"
            },
            {
                "field": "nacimiento",
                "range_search": True,
                "range_start": "",
                "range_end": "2000-01-01"
            },
          ]
    }
    #TODO: TEMPORAL END
    expr = query["operations"]
    tokens = re.findall(r'\(|\)|\d+|AND|OR|NOT', expr)
    tree = parse_select(tokens)
    sets = []
    nombre_tabla = query["table"]
    data = select_meta(nombre_tabla)
    format = {}
    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    print(query["conditions"])
    for condition in query["conditions"]:
        key = condition["field"]
        index = data["columns"][key]["index"]

        if index == None:
            heap = Heap(format,
                        data["key"],
                        table_filename(nombre_tabla))

            if condition["range_search"]:
                sets.append(set(heap.find(condition["range_start"], condition["range_end"])))
            else:
                sets.append(set(heap.find(condition["value"], condition["value"])))
        elif index == "hash":
            hash = Hash(format,
                        key,
                        index_filename(nombre_tabla, key, "buckets"),
                        index_filename(nombre_tabla, key, "index"),
                        table_filename(nombre_tabla))

            if condition["range_search"]:
                sets.append(set(hash.range_search(condition["range_start"], condition["range_end"])))
            else:
                sets.append(set(hash.search(condition["value"])))

        elif index == "btree":
            btree = Btree(format,
                          key,
                          index_filename(nombre_tabla, key, "index"),
                          table_filename(nombre_tabla),
                          M)

            if condition["range_search"]:
                sets.append(set(btree.search_range(condition["range_start"], condition["range_end"])))
            else:
                sets.append(set(btree.search(condition["value"])))

    for i in range(len(sets)):
        print(i, ":", sets[i])

    # Evaluar la expresión booleana
    universe = set(range(len(sets)))
    result_set = evaluate_select(tree, sets, universe)
    print("RESULTADO FINAL DE ", query["operations"])
    print(result_set)