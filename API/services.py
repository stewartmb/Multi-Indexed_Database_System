import json
import os
import sys
import re
import csv
from fastapi import HTTPException

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
    if type == "float":
        return "f"
    if type == "double":
        return "d"
    if type == "date":
        return "10s"
    if type == "long":
        return "q"
    if type == "ulong":
        return "Q"
    if type == "bool":
        return "?"
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
            if tokens[pos] == 'not':
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
        if op == 'not':
            child = evaluate_select(node[1], sets, universe)
            return universe - child
        elif op == 'and':
            return evaluate_select(node[1], sets, universe) & evaluate_select(node[2], sets, universe)
        elif op == 'or':
            return evaluate_select(node[1], sets, universe) | evaluate_select(node[2], sets, universe)
        else:
            raise ValueError("Unknown operator: " + op)

def cast(value, type):
    if type == "?":
        if value == 1:
            return 1
        elif value == -1:
            return 0
        return int(value)
    if type == "i" or type == "q" or type == "Q":
        if value == 1:
            return int(1e100)
        elif value == -1:
            return int(-1e100)
        return int(value)
    elif type == "d" or type == "f":
        return float(value)
    elif type[-1] == "s":
        if value == 1:
            return "\U0010FFFF" * 256
        elif value == -1:
            return ""
        return str(value)
    else:
        print("ERROR: tipo no soportado")
        return None

def convert(query):
    # print(json.dumps(query, indent=2))
    if query["action"] == "create_table":
        return create_table(query)
    elif query["action"] == "insert":
        return insert(query)
    elif query["action"] == "select":
        return select(query)
    elif query["action"] == "delete":
        return delete(query)
    elif query["action"] == "index":
        return create_index(query)
    elif query["action"] == "copy":
        return copy(query)
    elif query["action"] == "drop index":
        return drop_index(query)
    elif query["action"] == "drop table":
        return drop_table(query)
    elif query["action"] == "set":
        return set_stmt(query)
    else:
        print("error: accion no soportada")

def create_table(query):
    # crear tabla y añadir a metadata

    os.makedirs(os.path.dirname(table_filename(query["name"])), exist_ok=True)
    with open(table_filename(query["name"]), "w") as f:
        pass
    create_meta(query["data"], query["name"])
    format = {}
    cols = query["data"]["columns"]
    for key in cols.keys():
        format[key] = to_struct(cols[key]["type"])

    indexes_data = select_index_meta()
    print(json.dumps(indexes_data, indent=4))

    # crear indices
    for key in cols.keys():
        index = cols[key]["index"]
        if index == None:
            pass
        elif index == "hash":
            if indexes_data["hash"] is not None:
                hash = Hash(format,
                            key,
                            index_filename(query["name"], key, "buckets"),
                            index_filename(query["name"], key, "index"),
                            table_filename(query["name"]), *indexes_data["hash"])
            else:
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
            if indexes_data["btree"] is not None:
                btree = Btree(format,
                            key,
                            index_filename(query["name"], key, "index"),
                            table_filename(query["name"]),
                            *indexes_data["btree"])
            else:
                btree = Btree(format,
                            key,
                            index_filename(query["name"], key, "index"),
                            table_filename(query["name"]),
                            M)

        else:
            print("INDICE NO IMPLEMENTADO AUN")
    return {
        "message": f"CREATED TABLE {query["name"]}"
    }

def insert(query):
    nombre_tabla = query["table"]
    data = select_meta(nombre_tabla)
    format = {}
    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    # insertar en tabla
    heap = Heap(format,
                data["key"],
                table_filename(nombre_tabla))

    position = heap.insert(query["values"][1])

    indexes_data = select_index_meta()

    # insertar en cada indice si existe
    for key in data["columns"].keys():
        index = data["columns"][key]["index"]
        if index == None:
            pass
        elif index == "hash":
            if indexes_data["hash"] is not None:
                hash = Hash(format,
                            key,
                            index_filename(nombre_tabla, key, "buckets"),
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla), *indexes_data["hash"])
            else:
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

            seq.add(pos_new_record=position)

        elif index == "btree":
            if indexes_data["btree"] is not None:
                btree = Btree(format,
                            key,
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla),
                            *indexes_data["btree"])
            else:
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
    
    return {
        "message": f"INSERTED VALUE ON TABLE {nombre_tabla}"
    }

def create_index(query):
    nombre_tabla = query["table"]
    data = select_meta(nombre_tabla)
    format = {}

    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    for key in query["attr"]:
        data["columns"][key]["index"] = query["index"]

    create_meta(data, nombre_tabla)

    indexes_data = select_index_meta()

    keys = query["attr"]
    
    hash = None
    seq = None
    rtree = None
    btree = None
    isam = None

    heap = Heap(format,
                data["key"],
                table_filename(nombre_tabla))

    index = query["index"]
    if index == None:
        pass
    elif index == "hash":
        if indexes_data["hash"] is not None:
            hash = Hash(format,
                        keys[0],
                        index_filename(nombre_tabla, keys[0], "buckets"),
                        index_filename(nombre_tabla, keys[0], "index"),
                        table_filename(nombre_tabla), *indexes_data["hash"])
        else:
            hash = Hash(format,
                        keys[0],
                        index_filename(nombre_tabla, keys[0], "buckets"),
                        index_filename(nombre_tabla, keys[0], "index"),
                        table_filename(nombre_tabla))

    elif index == "seq":
        seq = Sequential(format,
                         keys[0],
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

    elif index == "btree":
        if indexes_data["btree"] is None:
            btree = Btree(format,
                        keys[0],
                        index_filename(nombre_tabla, keys[0], "index"),
                        table_filename(nombre_tabla),
                        M)
        else:
            btree = Btree(format,
                        keys[0],
                        index_filename(nombre_tabla, keys[0], "index"),
                        table_filename(nombre_tabla),
                        *indexes_data["btree"])

    else:
        print("INDICE NO IMPLEMENTADO AUN")

    records = heap._select_all()
    positions = heap.get_all()
    create_meta(data, nombre_tabla)

    # añadir los registros ya en la tabla al indice creado
    for record, pos in zip(records, positions):
        if hash is not None:
            hash.insert(record, pos)
        elif seq is not None:
            seq.add(pos_new_record=pos)
        elif rtree is not None:
            rtree.insert(record, pos)
        elif btree is not None:
            btree.add(pos_new_record=pos)
    
    return {
        "message": f"CREATED INDEX {index} ON TABLE {nombre_tabla}"
    }
    
def aux_select(query):
    # print(json.dumps(query, indent=2))
    nombre_tabla = query["table"]
    data = select_meta(nombre_tabla)
    format = {}
    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    if query["eval"] is None:
        heap = Heap(format,
                    data["key"],
                    table_filename(query["table"]))

        return set(heap.get_all())

    expr = str(query["eval"])
    tokens = re.findall(r'\(|\)|\d+|and|or|not', expr)

    calc_universe = False
    if "not" in tokens:
        calc_universe = True

    tree = parse_select(tokens)
    sets = []

    indexes_data = select_index_meta()

    for condition in query["conditions"].keys():
        cond = query["conditions"][condition]
        key = cond["field"]

        if isinstance(key, list):
            rtree = Rtree(format,
                          data["key"],
                          key,
                          table_filename(nombre_tabla),
                          index_filename(nombre_tabla, *key, "index"))

            if cond["range_search"] == True:
                start = cond["range_start"]
                end = cond["range_end"]

                for i in range(len(start)):
                    start[i] = cast(start[i], format[key[i]])
                    end[i] = cast(end[i], format[key[i]])
                sets.append(set(rtree.range_search(start, end)))
            else:
                if "knn" in cond:
                    point = cond["point"]
                    for i in range(len(point)):
                        point[i] = cast(point[i], format[key[i]])
                    sets.append(set(rtree.ksearch(int(cond["knn"]), point))) # desordena el knn
                else:
                    point = cond["value"]
                    for i in range(len(point)):
                        point[i] = cast(point[i], format[key[i]])

                    sets.append(set(rtree.search(point)))


        else:
            index = data["columns"][key]["index"]

            left = None
            right = None
            val = None
            if cond["range_search"]:
                left = cast(cond["range_start"], format[key])
                right = cast(cond["range_end"], format[key])
            else:
                val = cast(cond["value"], format[key])

            if index == None:
                heap = Heap(format,
                            cond["field"],
                            table_filename(nombre_tabla))

                if cond["range_search"]:
                    sets.append(set(heap.search(left, right)))
                else:
                    sets.append(set(heap.search(val, val)))
            elif index == "hash":
                if indexes_data["hash"] is not None:
                    hash = Hash(format,
                                key,
                                index_filename(nombre_tabla, key, "buckets"),
                                index_filename(nombre_tabla, key, "index"),
                                table_filename(nombre_tabla), *indexes_data["hash"])
                else:
                    hash = Hash(format,
                                key,
                                index_filename(nombre_tabla, key, "buckets"),
                                index_filename(nombre_tabla, key, "index"),
                                table_filename(nombre_tabla))

                if cond["range_search"]:
                    if cond["op"] != ">" and cond["op"] != "<" and cond["op"] != "!=":
                        sets.append(set(hash.range_search(left, right)))
                    else:
                        valid = set(hash.range_search(left, right))
                        if cond["op"] == ">":
                            invalid = set(hash.search(left))
                        elif cond["op"] == "<":
                            invalid = set(hash.search(right))
                        else:
                            curr = cond["value"]
                            invalid = set(hash.search(curr))

                        sets.append(valid - invalid)


                else:
                    sets.append(set(hash.search(val)))

            elif index == "btree":
                if indexes_data["btree"] is not None:
                    btree = Btree(format,
                                key,
                                index_filename(nombre_tabla, key, "index"),
                                table_filename(nombre_tabla),
                                *indexes_data["btree"])
                else:
                    btree = Btree(format,
                                key,
                                index_filename(nombre_tabla, key, "index"),
                                table_filename(nombre_tabla),
                                M)

                if cond["range_search"]:
                    if cond["op"] != ">" and cond["op"] != "<" and cond["op"] != "!=":
                        sets.append(set(btree.search_range(left, right)))
                    else:
                        valid = set(btree.search_range(left, right))
                        if cond["op"] == ">":
                            invalid = set(btree.search(left))
                        elif cond["op"] == "<":
                            invalid = set(btree.search(right))
                        else:
                            curr = cond["value"]
                            invalid = set(btree.search(curr))

                        sets.append(valid - invalid)
                else:
                    sets.append(set(btree.search(val)))

            elif index == "seq":
                seq = Sequential(format,
                                 key,
                                 index_filename(nombre_tabla, key, "index"),
                                 table_filename(nombre_tabla))

                if cond["range_search"]:
                    if cond["op"] != ">" and cond["op"] != "<" and cond["op"] != "!=":
                        sets.append(set(seq.search_range(left, right)))
                    else:
                        valid = set(seq.search_range(left, right))
                        if cond["op"] == ">":
                            invalid = set(seq.search(left))
                        elif cond["op"] == "<":
                            invalid = set(seq.search(right))
                        else:
                            curr = cond["value"]
                            invalid = set(seq.search(curr))

                        sets.append(valid - invalid)
                else:
                    sets.append(set(seq.search(val)))


    for i in range(len(sets)):
        print(i, ":", sets[i])

    # Evaluar la expresión booleana
    universe = None
    if calc_universe:
        heap = Heap(format,
                    data["key"],
                    table_filename(query["table"]))
        universe = set(heap.get_all())
    return evaluate_select(tree, sets, universe)

def select(query):
    ans_set = aux_select(query)

    # print(ans_set)

    result = []

    data = select_meta(query["table"])
    format = {}
    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    for i in ans_set:
        heap = Heap(format,
                    data["key"],
                    table_filename(query["table"]))
        if not heap.is_deleted(i):
            result.append(heap.read(i))

    columns_names = list(data["columns"].keys())

    return {
        "columns": columns_names,
        "data": result
    }

def copy(query):
    # print(json.dumps(query, indent=4))

    format = {}
    
    nombre_tabla = query["table"]

    data = select_meta(nombre_tabla)
    indexes_data = select_index_meta()

    hash = []
    seq = []
    rtree = None
    btree = []
    isam = []

    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

        index = data["columns"][key]["index"]
        if index == None:
            pass
        elif index == "hash":
            if indexes_data["hash"] is not None:
                hash.append(Hash(format,
                            key,
                            index_filename(nombre_tabla, key, "buckets"),
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla), *indexes_data["hash"]))
            else:
                hash.append(Hash(format,
                            key,
                            index_filename(nombre_tabla, key, "buckets"),
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla)))
        elif index == "seq":
            seq.append(Sequential(format,
                        key,
                        index_filename(nombre_tabla, key, "index"),
                        table_filename(nombre_tabla)))
        elif index == "btree":
            if indexes_data["btree"] is not None:
                btree.append(Btree(format,
                            key,
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla),
                            *indexes_data["btree"]))
            else:
                btree.append(Btree(format,
                            key,
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla),
                            M))
    
    rtree_keys = data.get("indexes", {}).get("rtree")
    if rtree_keys is not None:
        rtree = Rtree(format, 
                    data["key"],
                    rtree_keys, 
                    table_filename(nombre_tabla),  
                    index_filename(nombre_tabla, *rtree_keys, "index"))

    heap = Heap(format,
                data["key"],
                table_filename(nombre_tabla))


    with open(query["from"], mode='r', newline='') as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            # insertar en el principal y en todos los índices
            pos = heap.insert(row)

            for h in hash:
                h.insert(row, pos)
            for bp in btree:
                bp.add(pos_new_record=pos)
            for s in seq:
                s.add(pos_new_record=pos)
            if rtree is not None:
                rtree.insert(row, pos)

    return {
        "message": f"COPIED {query["from"]} ON TABLE {nombre_tabla}"
    }

def delete(query):
    ans_set = aux_select(query)

    nombre_tabla = query["table"]
    data = select_meta(nombre_tabla)

    hash = []
    seq = []
    rtree = None
    btree = []
    isam = []

    format = {}

    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    heap = Heap(format,
                data["key"],
                table_filename(nombre_tabla))
    
    indexes_data = select_index_meta()

    for key in data["columns"].keys():
        index = data["columns"][key]["index"]
        if index == None:
            pass
        elif index == "hash":
            if indexes_data["hash"] is not None:
                hash.append(Hash(format,
                            key,
                            index_filename(nombre_tabla, key, "buckets"),
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla), *indexes_data["hash"]))
            else:
                hash.append(Hash(format,
                            key,
                            index_filename(nombre_tabla, key, "buckets"),
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla)))
        elif index == "seq":
            seq.append(Sequential(format,
                        key,
                        index_filename(nombre_tabla, key, "index"),
                        table_filename(nombre_tabla)))
        elif index == "btree":
            if indexes_data["btree"] is not None:
                btree.append(Btree(format,
                            key,
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla),
                            *indexes_data["btree"]))
            else:
                btree.append(Btree(format,
                            key,
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla),
                            M))
    
    rtree_keys = data.get("indexes", {}).get("rtree")
    if rtree_keys is not None:
        rtree = Rtree(format, 
                    data["key"],
                    rtree_keys, 
                    table_filename(nombre_tabla),  
                    index_filename(nombre_tabla, *rtree_keys, "index"))
    
    
    for pos in ans_set:
        heap.mark_deleted(pos)
        # for h in hash:
        #     h.delete(pos)
        # not implemented in b tree
        # for s in seq:
        #     s.eliminar(pos)
        if rtree is not None:
            rtree.delete(pos)

    return {
        "message": "DELETED"
    }

def drop_index(query):
    nombre_tabla = query["table"]
    index_file = index_filename(nombre_tabla,
                                *query["attr"],
                                "index")
    
    # eliminar indice en metadata

    data = select_meta(nombre_tabla)

    for key in query["attr"]:
        data["columns"][str(key)]["index"] = None

    create_meta(data, nombre_tabla)

    try:
        os.remove(index_file)
        if query["index"] == "hash":
            os.remove(index_filename(nombre_tabla, key, "buckets"))

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    return {
        "message": "DELETED INDEX SUCCESSFULLY"
    }

def drop_table(query):
    nombre_tabla = query["table"]
    data = select_meta(nombre_tabla)

    print(json.dumps(data, indent=4))

    data_file = table_filename(nombre_tabla)
    
    # eliminar indices en la tabla
    for key in data["columns"].keys():
        index = data["columns"][key]["index"]
        if index == "hash":
            os.remove(index_filename(nombre_tabla, key, "buckets"))
        if index is not None and index != "rtree":
            index_file = index_filename(nombre_tabla,
                                    key,
                                    "index")
            os.remove(index_file)

    rtree_keys = data.get("indexes", {}).get("rtree")
    if rtree_keys is not None:
        os.remove(index_filename(nombre_tabla, *rtree_keys, "index"))
    
    # eliminar entrada en metadata
    delete_meta(nombre_tabla)
    
    try:
        os.remove(data_file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    return {
        "message": "DELETED INDEX SUCCESSFULLY"
    }

def set_stmt(query):
    index = query["index"]

    try:
        params = [int(x) for x in query["params"]]
    except ValueError as e:
        print("One of the items couldn't be converted:", e)
    
    if index == "btree" and len(params) != 1:
        raise HTTPException(status_code=404, detail="Wrong amount of parameters")
    elif index == "hash" and len(params) != 2:
        raise HTTPException(status_code=404, detail="Wrong amount of parameters")

    set_index_meta(index, params)

    return {
        "message": "SET INDEXES CORRECTLY"
    }