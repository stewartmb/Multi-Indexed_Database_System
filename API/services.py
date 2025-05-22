import json
import os
import sys
import re

from numpy.ma.core import nomask

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Format_Meta import create, select
from Heap_struct.Heap import *
from Hash_struct.Hash import Hash

"varchar[20]"
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
        with open(query["name"] + "_table.bin", "w") as f:
            pass
        create(query["data"], query["name"])
        format = {}
        for key in query["data"]["columns"].keys():
            format[key] = to_struct(query["data"]["columns"][key]["type"])

        # crear indices
        for key in query["data"]["columns"].keys():
            index = query["data"]["columns"][key]["index"]
            if index == None:
                pass
            elif index == "hash":
                buckets_file_name = query["name"] + "_" + key + "_buckets.bin"
                index_file_name = query["name"] + "_" + key + "_index.bin"

                hash = Hash(format,
                            key,
                            buckets_file_name,
                            index_file_name,
                            query["name"] + "_table.bin")
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
                    nombre_tabla + "_table.bin")

        position = heap.insert(query["values"][1])

        # crear indices
        for key in data["columns"].keys():
            index = data["columns"][key]["index"]
            if index == None:
                pass
            elif index == "hash":
                buckets_file_name = nombre_tabla + "_" + key + "_buckets.bin"
                index_file_name = nombre_tabla + "_" + key + "_index.bin"

                hash = Hash(format,
                            key,
                            buckets_file_name,
                            index_file_name,
                            nombre_tabla + "_table.bin")

                hash.insert(query["values"][1], position)



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
