from lark import Lark
from lark import Transformer
import json

sql_grammar = """
?start: stmt+

stmt: create_stmt ";" 
    | select_stmt ";" 
    | insert_stmt ";" 
    | delete_stmt ";"
    | index_stmt ";"
    | copy_stmt ";"

create_stmt: "create" "table" NAME "(" create_attr_list ")"
copy_stmt: "copy" NAME "from" VALUE
create_attr_list: NAME (TYPE | varchar) [ KEY ] ["index" INDEX] ("," NAME (TYPE | varchar) [ KEY ] ["index" INDEX])*
select_stmt: "select" (ALL | attr_list) "from" NAME ["where" condition ("and" condition)*]
attr_list: NAME ("," NAME)*

index_stmt: "create" "index" "on" NAME "using" INDEX "(" attr_list ")"

insert_stmt: "insert" "into" NAME "(" attr_list ")" "values" "(" value_list ")"
value_list: VALUE ("," VALUE)*

delete_stmt: "delete" "from" NAME "where" condition ("and" condition)*

condition: NAME OP VALUE
         | NAME BETWEEN VALUE "and" VALUE

OP: "==" | "!=" | "<" | ">" | "<=" | ">="
NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
VALUE: /[0-9]+/ | ESCAPED_STRING
INDEX: "rtree" | "btree" | "seq" | "isam" | "hash"
KEY: "primary key"
BETWEEN: "between"
ALL: "*"

TYPE: "int" | "string" | "float" | "text" | "bool" | "date" 
varchar: "varchar" "[" VALUE "]"

%import common.ESCAPED_STRING
%import common.WS
%ignore WS
"""


class SQLTransformer(Transformer):
    def start(self, items):
        return items

    def stmt(self, items):
        return items

    def create_stmt(self, items):
        table_name = str(items[0])
        return {"action": "create_table", "name": table_name, "data": items[1]}

    def select_stmt(self, items):
        table = str(items[1])
        if len(items) > 1:
            return {"action": "select", "table": table, "attr": items[0], "condition": items[2]}
        return {"action": "select", "table": table}

    def insert_stmt(self, items):
        return {"action": "insert", "table": str(items[0]), "values": items[1:]}

    def delete_stmt(self, items):
        return {"action": "delete", "table": str(items[0]), "condition": items[1:]}

    def index_stmt(self, items):
        return {"action": "index", "table": str(items[0]), "index": items[1], "attr": items[2]}

    def copy_stmt(self, items):
        return {"action": "copy", "table": str(items[0]), "from": str(items[1])}

    def condition(self, items):
        if str(items[1]) == "between":
            return {"field": str(items[0]), "range_search": True, "range_start": items[2], "range_end": items[3]}
        elif str(items[1]) == "==":
            return {"field": str(items[0]), "range_search": False, "op": str(items[1]), "value": items[2]}
        else:
            range_start = "-infinity"
            range_end =  "infinity"
            if str(items[1]) == ">":
                range_start = str(int(items[2])+1)
            elif str(items[1]) == "<":
                range_end = str(int(items[2])-1)
            elif str(items[1]) == "<=":
                range_end = items[2]
            elif str(items[1]) == ">=":
                range_start = items[2]

            return {"field": str(items[0]), "range_search": True, "range_start": range_start, "range_end": range_end}

    def create_attr_list(self, items):
        result = {}
        dict = {}
        i = 0
        while i < len(items):
            while i < len(items) and items[i] is None:
                i+=1
            if i == len(items):
                break
            attr_name = str(items[i])
            attr_type = items[i+1]
            key = None
            key_index = None
            i+=2
            if i < len(items) and items[i] is not None and str(items[i]) == "primary key":
                result["key"] = attr_name
                i+=1
            if i < len(items) and items[i] is None:
                i+=1
            if i < len(items) and items[i] is not None and items[i] in ["rtree", "btree", "seq", "isam", "hash"]:
                key_index = items[i]
                i+=1
            dict[attr_name] = {"type": attr_type, "index": key_index}
        result["columns"] = dict
        return result

    def attr_list(self, items):
        result = []
        i = 0
        while i < len(items):
            attr_name = str(items[i])
            result.append(attr_name)
            i+=1
        return result

    def value_list(self, items):
        return [str(v) for v in items]

    def value(self, items):
        return str(items[0])

    def NAME(self, tok):
        return tok.value

    def TYPE(self, tok):
        return tok.value

    def INDEX(self, tok):
        return tok.value

    def VALUE(self, tok):
        return tok.value.strip('"')  # remove quotes if present

    def varchar(self, items):
        return f"varchar[{items[0]}]"


if __name__ == "__main__":
    parser = Lark(sql_grammar, start="start", parser="lalr", transformer=SQLTransformer())

    # Example: read SQL statements from a file
    with open("test.txt", "r") as f:
        sql_code = f.read()

    try:
        result = parser.parse(sql_code)
        print(json.dumps(result, indent=4))
    except Exception as e:
        print("Error parsing input:", e)