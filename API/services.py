import json
import os
import sys
import re
import csv
import time
import datetime
from fastapi import HTTPException

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Format_Meta import *
from Utils.file_format import *
from Heap_struct.Heap import *

from Hash_struct.Hash import Hash
from BPtree_struct.Indice_BPTree_file import BPTree as Bptree
from Sequential_Struct.Indice_Sequential_file import Sequential
from RTree_struct.RTreeFile_Final import RTreeFile as Rtree
from Isam_struct.Indice_Isam_file import ISAM as Isam

M = 1000


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
    if type == "timestamp":
        return "26s"
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
        raise HTTPException(status_code=404, detail="Action not supported")

def create_table(query):
    # crear tabla y añadir a metadata
    start = time.time_ns()

    pk = query["data"].get("key", None)

    if pk is None:
        raise HTTPException(404, "No primary key provided.")
    else:
        if query["data"]["columns"][pk]["index"] is None:
            query["data"]["columns"][pk]["index"] = "bptree"
            query["data"]["columns"][pk]["params"] = [50]

    os.makedirs(os.path.dirname(table_filename(query["name"])), exist_ok=True)
    with open(table_filename(query["name"]), "w") as f:
        pass

    format = {}
    cols = query["data"]["columns"]
    
    for key in cols.keys():
        format[key] = to_struct(cols[key]["type"])

    # crear indices
    for key in cols.keys():
        index = cols[key]["index"]
        params = cols[key].get("params", [])
        if index == None:
            pass
        elif index == "hash":
            hash = Hash(format,
                        key,
                        index_filename(query["name"], key, "buckets"),
                        index_filename(query["name"], key, "index"),
                        table_filename(query["name"]), *params)
        elif index == "seq":
            seq = Sequential(format,
                             key,
                             index_filename(query["name"], key, "index"),
                             table_filename(query["name"]), *params)

        elif index == "bptree":
            if len(params) != 0:
                bptree = Bptree(format,
                            key,
                            index_filename(query["name"], key, "index"),
                            table_filename(query["name"]),
                            *params)
            else:
                print("not enough parameters")
                raise HTTPException(status_code=404, detail="Not enough parameters.")

        else:
            print("INDICE NO IMPLEMENTADO AUN")

    print(json.dumps(query["data"], indent=4))
    create_meta(query["data"], query["name"])
    end = time.time_ns()
    t_ms = end - start

    lista = []
    for key in query["data"]["columns"].keys():
        column = query["data"]["columns"][key]
        lista.append([key, column["type"], column["index"]])


    return {
        "columns": ["column", "type", "index"],
        "data": lista,
        "message": f"CREATED TABLE {query["name"]} in {t_ms/1e6} ms"
    }

def insert(query):
    start = time.time_ns()
    nombre_tabla = query["table"]
    data = select_meta(nombre_tabla)
    format = {}
    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    # insertar en tabla
    heap = Heap(format,
                data["key"],
                table_filename(nombre_tabla))

    if len(format) != query["values"]:
        i = 0
        record = query["values"][1]
        for key in data["columns"].keys():
            if data["columns"][key]["type"] == "timestamp":
                record.insert(i, str(datetime.datetime.now()))
                print(record)
            i += 1

    position = heap.insert(record)

    # insertar en cada indice si existe
    for key in data["columns"].keys():
        index = data["columns"][key]["index"]
        params = data["columns"][key].get("params", [])
        if index == None:
            pass
        elif index == "hash":
            hash = Hash(format,
                        key,
                        index_filename(nombre_tabla, key, "buckets"),
                        index_filename(nombre_tabla, key, "index"),
                        table_filename(nombre_tabla), *params)
            hash.insert(query["values"][1], position)

        elif index == "seq":
            seq = Sequential(format,
                             key,
                             index_filename(nombre_tabla, key, "index"),
                             table_filename(nombre_tabla), *params)

            seq.add(pos_new_record=position)

        elif index == "bptree":
            if len(params) != 0:
                bptree = Bptree(format,
                            key,
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla),
                            *params)
            else:
                raise HTTPException(status_code=404, detail="Not enough parameters.")
            bptree.add(pos_new_record=position)

        elif index == "isam":
            isam = Isam(format,
                        key,
                        index_filename(nombre_tabla, key, "index"),
                        table_filename(nombre_tabla))
            isam.add(pos_new_record=position)

    # indice compuesto en rtree, añadir en el indice
    rtree_keys = data.get("indexes", {}).get("rtree")
    if rtree_keys is not None:
        rtree = Rtree(format,
                      data["key"],
                      rtree_keys,
                      table_filename(nombre_tabla),
                      index_filename(nombre_tabla, *rtree_keys, "index"))
        rtree.insert(query["values"][1], position)
    end = time.time_ns()
    t_ms = end - start

    return {
        "message": f"INSERTED VALUE ON TABLE {nombre_tabla} in {t_ms/1e6} ms"
    }

def create_index(query):
    start = time.time_ns()
    nombre_tabla = query["table"]
    data = select_meta(nombre_tabla)
    format = {}

    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    print(query["attr"])
    for key in query["attr"]:
        print(data["columns"][key]["index"])
        if data["columns"][key]["index"] is None:
            data["columns"][key]["index"] = query["index"]
        else:
            raise HTTPException(status_code=404, detail=f"Index already created on attribute {key}")

    keys = query["attr"]
    
    hash = None
    seq = None
    rtree = None
    bptree = None
    isam = None

    heap = Heap(format,
                data["key"],
                table_filename(nombre_tabla))

    index = query["index"]
    if index == None:
        pass
    elif index == "hash":
        hash = Hash(format,
                    keys[0],
                    index_filename(nombre_tabla, keys[0], "buckets"),
                    index_filename(nombre_tabla, keys[0], "index"),
                    table_filename(nombre_tabla), *query["params"])

    elif index == "seq":
        seq = Sequential(format,
                         keys[0],
                         index_filename(nombre_tabla, keys[0], "index"),
                         table_filename(nombre_tabla), *query["params"])

    elif index == "rtree":
        rtree = Rtree(format,
                      data["key"],
                      keys,
                      table_filename(nombre_tabla),
                      index_filename(nombre_tabla, *keys, "index"))
        if "indexes" not in data:
            data["indexes"] = {}

        data["indexes"]["rtree"] = keys

    elif index == "isam":
        isam = Isam(format,
                    keys[0],
                    index_filename(nombre_tabla, keys[0], "index"),
                    table_filename(nombre_tabla))

    elif index == "bptree":
        if len(query["params"]) != 0:
            bptree = Bptree(format,
                        keys[0],
                        index_filename(nombre_tabla, keys[0], "index"),
                        table_filename(nombre_tabla),
                        *query["params"])
        else:
            raise HTTPException(status_code=404, detail="Not enough parameters.")

    else:
        print("INDICE NO IMPLEMENTADO AUN")

    records = heap._select_all()
    positions = heap.get_all()

    # añadir los registros ya en la tabla al indice creado
    for record, pos in zip(records, positions):
        if hash is not None:
            hash.insert(record, pos)
        elif seq is not None:
            seq.add(pos_new_record=pos)
        elif rtree is not None:
            rtree.insert(record, pos)
        elif bptree is not None:
            bptree.add(pos_new_record=pos)

    end = time.time_ns()
    t_ms = end - start
    
    create_meta(data, nombre_tabla)

    return {
        "message": f"CREATED INDEX {index} ON TABLE {nombre_tabla} in {t_ms/1e6} ms"
    }

def aux_select(query):
    print(json.dumps(query, indent=2))
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
    print("tree: ", tree)
    sets = []

    for condition in query["conditions"].keys():
        cond = query["conditions"][condition]
        print("cond", cond)
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
            params = data["columns"][key].get("params", [])
            left = None
            right = None
            val = None
            if cond["range_search"]:
                left = cast(cond["range_start"], format[key])
                right = cast(cond["range_end"], format[key])
            else:
                val = cast(cond["value"], format[key])

            if index == None:
                print("Entered heap")
                heap = Heap(format,
                            cond["field"],
                            table_filename(nombre_tabla))

                if cond["range_search"]:
                    if cond["op"] != ">" and cond["op"] != "<" and cond["op"] != "!=":
                        print("entered ==")
                        sets.append(set(heap.search(left, right)))
                    else:
                        print("entered other")
                        valid = set(heap.search(left, right))
                        if cond["op"] == ">":
                            invalid = set(heap.search(left,left))
                        elif cond["op"] == "<":
                            invalid = set(heap.search(right,right))
                        else:
                            curr = cast(cond["value"], format[key])
                            print([curr, cond["value"]])
                            invalid = set(heap.search(curr,curr))

                        sets.append(valid - invalid)
                else:
                    sets.append(set(heap.search(val, val)))

            elif index == "hash":
                hash = Hash(format,
                            key,
                            index_filename(nombre_tabla, key, "buckets"),
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla), *params)
            

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
                            curr = cast(cond["value"], format[key])
                            invalid = set(hash.search(curr))

                        sets.append(valid - invalid)


                else:
                    sets.append(set(hash.search(val)))

            elif index == "bptree":
                if len(params) != 0:
                    bptree = Bptree(format,
                                key,
                                index_filename(nombre_tabla, key, "index"),
                                table_filename(nombre_tabla),
                                *params)
                else:
                    raise HTTPException(status_code=404, detail="Not enough parameters.")

                if cond["range_search"]:
                    if cond["op"] != ">" and cond["op"] != "<" and cond["op"] != "!=":
                        sets.append(set(bptree.search_range(left, right)))
                    else:
                        valid = set(bptree.search_range(left, right))
                        if cond["op"] == ">":
                            invalid = set(bptree.search(left))
                        elif cond["op"] == "<":
                            invalid = set(bptree.search(right))
                        else:
                            curr = cast(cond["value"], format[key])
                            invalid = set(bptree.search(curr))

                        sets.append(valid - invalid)
                else:
                    sets.append(set(bptree.search(val)))

            elif index == "seq":
                seq = Sequential(format,
                                 key,
                                 index_filename(nombre_tabla, key, "index"),
                                 table_filename(nombre_tabla), *params)

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
                            curr = cast(cond["value"], format[key])
                            invalid = set(seq.search(curr))

                        sets.append(valid - invalid)
                else:
                    sets.append(set(seq.search(val)))
            elif index == "isam":
                isam = Isam(format,
                            key,
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla))
                if cond["range_search"]:
                    if cond["op"] != ">" and cond["op"] != "<" and cond["op"] != "!=":
                        sets.append(set(isam.search_range(left, right)))
                    else:
                        valid = set(isam.search_range(left, right))
                        if cond["op"] == ">":
                            invalid = set(isam.search(left))
                        elif cond["op"] == "<":
                            invalid = set(isam.search(right))
                        else:
                            curr = cast(cond["value"], format[key])
                            invalid = set(isam.search(curr))

                        sets.append(valid - invalid)
                else:
                    print(val)
                    sets.append(set(isam.search(val)))




    for i in range(len(sets)):
        print(i, ":", sets[i])

    print("a")
    # Evaluar la expresión booleana
    universe = None
    if calc_universe:
        heap = Heap(format,
                    data["key"],
                    table_filename(query["table"]))
        universe = set(heap.get_all())
    print(tree, sets, universe)

    return evaluate_select(tree, sets, universe)

def select(query):
    #cronometrar
    start = time.time_ns()
    print(json.dumps(query, indent=4))

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

    column_indices = {name: i for i, name in enumerate(list(data["columns"].keys()))}

    if query["attr"] == "*":
        columns_names = list(data["columns"].keys())
    else:
        columns_names = query["attr"]
        indices = [column_indices[x] for x in columns_names]
        result = [[r[i] for i in indices] for r in result]

    end = time.time_ns()
    t_ms = end - start
    print("RESULT_DATA:",result)
    return {
        "columns": columns_names,
        "data": result,
        "message": f"SELECTED {len(result)} RECORDS FROM TABLE {query['table']} in {t_ms/1e6} ms",
    }

def copy(query):
    # print(json.dumps(query, indent=4))
    start = time.time_ns()
    format = {}
    
    nombre_tabla = query["table"]

    data = select_meta(nombre_tabla)

    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])
    
    hash = []
    seq = []
    rtree = None
    bptree = []
    isam = []

    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    for key in data["columns"].keys():
        index = data["columns"][key]["index"]
        params = data["columns"][key].get("params", [])

        if index == None:
            pass
        elif index == "hash":
            hash.append(Hash(format,
                        key,
                        index_filename(nombre_tabla, key, "buckets"),
                        index_filename(nombre_tabla, key, "index"),
                        table_filename(nombre_tabla), *params))
        elif index == "seq":
            seq.append(Sequential(format,
                        key,
                        index_filename(nombre_tabla, key, "index"),
                        table_filename(nombre_tabla), *params))
        elif index == "bptree":
            if len(params) != 0:
                bptree.append(Bptree(format,
                            key,
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla),
                            *params))
            else:
                raise HTTPException(status_code=404, detail="Not enough parameters.")
        elif index == "isam":
            isam.append(Isam(format,
                             key,
                             index_filename(nombre_tabla, key, "index"),
                             table_filename(nombre_tabla)))
    
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


    with open(query["from"], mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            # insertar en el principal y en todos los índices
            pos = heap.insert(row)
            print(pos)
            print(heap.read(pos))
            for h in hash:
                h.insert(row, pos)
            for bp in bptree:
                bp.add(pos_new_record=pos)
            for s in seq:
                s.add(pos_new_record=pos)
            for i in isam:
                i.add(pos_new_record=pos)
            if rtree is not None:
                rtree.insert(row, pos)
    
    end = time.time_ns()
    t_ms = end - start

    return {
        "message": f"COPIED {query["from"]} ON TABLE {nombre_tabla} in {t_ms/1e6} ms"
    }

def delete(query):
    start = time.time_ns()
    ans_set = aux_select(query)

    nombre_tabla = query["table"]
    data = select_meta(nombre_tabla)

    hash = []
    seq = []
    rtree = None
    bptree = []
    isam = []

    format = {}

    for key in data["columns"].keys():
        format[key] = to_struct(data["columns"][key]["type"])

    heap = Heap(format,
                data["key"],
                table_filename(nombre_tabla))

    for key in data["columns"].keys():
        index = data["columns"][key]["index"]
        params = data["columns"][key].get("params", [])
        if index == None:
            pass
        elif index == "hash":
            hash.append(Hash(format,
                        key,
                        index_filename(nombre_tabla, key, "buckets"),
                        index_filename(nombre_tabla, key, "index"),
                        table_filename(nombre_tabla), *params))
        elif index == "seq":
            seq.append(Sequential(format,
                        key,
                        index_filename(nombre_tabla, key, "index"),
                        table_filename(nombre_tabla), *params))
        elif index == "bptree":
            if len(params) != 0:
                bptree.append(Bptree(format,
                            key,
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla),
                            *params))
            else:
                raise HTTPException(status_code=404, detail="Not enough parameters.")
        elif index == "isam":
            isam.append(Isam(format,
                             key,
                             index_filename(nombre_tabla, key, "index"),
                             table_filename(nombre_tabla)))

    rtree_keys = data.get("indexes", {}).get("rtree")
    if rtree_keys is not None:
        rtree = Rtree(format,
                    data["key"],
                    rtree_keys,
                    table_filename(nombre_tabla),
                    index_filename(nombre_tabla, *rtree_keys, "index"))

    rebuild = False

    for pos in ans_set:
        if heap.mark_deleted(pos):
            rebuild = True
        # for h in hash:
        #     h.delete(pos)
        # not implemented in b tree
        # for s in seq:
        #     s.eliminar(pos)
        if rtree is not None:
            rtree.delete(pos)

    if rebuild:
        hash = []
        seq = []
        rtree = None
        bptree = []
        isam = []

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

            # remake index files
            if index == None:
                pass
            elif index == "hash":
                hash.append(Hash(format,
                            key,
                            index_filename(nombre_tabla, key, "buckets"),
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla), *params))
            elif index == "seq":
                seq.append(Sequential(format,
                            key,
                            index_filename(nombre_tabla, key, "index"),
                            table_filename(nombre_tabla), *params))
            elif index == "bptree":
                if len(params) != 0:
                    bptree.append(Bptree(format,
                                key,
                                index_filename(nombre_tabla, key, "index"),
                                table_filename(nombre_tabla),
                                *params))
                else:
                    raise HTTPException(status_code=404, detail="Not enough parameters.")
            elif index == "isam":
                isam.append(Isam(format,
                                 key,
                                 index_filename(nombre_tabla, key, "index"),
                                 table_filename(nombre_tabla)))

        rtree_keys = data.get("indexes", {}).get("rtree")
        if rtree_keys is not None:
            os.remove(index_filename(nombre_tabla, *rtree_keys, "index"))

        rtree_keys = data.get("indexes", {}).get("rtree")
        if rtree_keys is not None:
            rtree = Rtree(format,
                        data["key"],
                        rtree_keys,
                        table_filename(nombre_tabla),
                        index_filename(nombre_tabla, *rtree_keys, "index"))

        records = heap._select_all()

        os.remove(table_filename(nombre_tabla)) # borro la tabla

        heap = Heap(format,
                data["key"],
                table_filename(nombre_tabla))

        for r in records:
            pos = heap.insert(r)
            for h in hash:
                h.insert(r, pos)
            for bp in bptree:
                bp.add(pos_new_record=pos)
            for s in seq:
                s.add(pos_new_record=pos)
            if rtree is not None:
                rtree.insert(r, pos)
    
    end = time.time_ns()
    t_ms = end - start

    return {
        "message": f"DELETED {len(ans_set)} RECORDS in {t_ms/1e6} ms"
    }

def drop_index(query):
    start = time.time_ns()
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

    end = time.time_ns()
    t_ms = end - start

    return {
        "message": f"DELETED INDEX SUCCESSFULLY in {t_ms/1e6} ms"
    }

def drop_table(query):
    start = time.time_ns()
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

    end = time.time_ns()
    t_ms = end - start

    return {
        "message": f"DELETED TABLE SUCCESSFULLY in {t_ms/1e6} ms"
    }