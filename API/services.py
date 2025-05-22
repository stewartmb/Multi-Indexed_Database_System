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

def to_struct(type):
    varchar_match = re.match(r"varchar\[(\d+)\]", type)

    if type == "int":
        return "i"
    elif varchar_match:
        size = varchar_match.group(1)  # Extraemos el tamaño entre los corchetes
        return f"{size}s"
    else:
        print("ERROR: tipo no soportado")
        return None


def convert(query):
    print(json.dumps(query, indent=2))
    if query["action"] == "create_table":
        # crear tabla y añadir a metadata
        with open(table_filename(query["name"]), "w") as f:
            pass
        create(query["data"], query["name"])
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
                               4)

            else:
                print("INDICE NO IMPLEMENTADO AUN")


    elif query["action"] == "insert":
        nombre_tabla = query["table"]
        data = select(nombre_tabla)
        format = {}
        for key in data["columns"].keys():
            format[key] = to_struct(data["columns"][key]["type"])

        # insertar en tabla
        heap = Heap(format,
                    data["key"],
                    table_filename(nombre_tabla))

        position = heap.insert(query["values"][1])

        # crear indices
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

                seq.add(query["values"][1], position)

    elif query["action"] == "select":
        print("Y")
    elif query["action"] == "delete":
        print("Z")
    elif query["action"] == "index":
        print("A")
    elif query["action"] == "copy":
        print("B")
    else:
        print("error")
