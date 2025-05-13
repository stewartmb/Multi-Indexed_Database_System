import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Format_Meta import create, select

def convert(query):
    print(json.dumps(query, indent=4))
    if query["action"] == "create_table":
        with open(query["name"] + "_table.bin", "w") as f:
            pass
        create(query["data"], query["name"])
    elif query["action"] == "insert":
        print("X")
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
