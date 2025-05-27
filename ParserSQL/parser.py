from lark import Lark
from lark import Transformer
import json

sql_grammar = r"""
?start: stmt+

stmt: create_stmt ";" 
    | select_stmt ";" 
    | insert_stmt ";" 
    | delete_stmt ";"
    | index_stmt ";"
    | copy_stmt ";"
    | drop_index_stmt ";"
    | drop_table_stmt ";"

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

TYPE: "int"i | "float"i | "double"i | "bool"i | "date"i | "long"i | "ulong"i | "timestamp"i
varchar: "varchar"i "[" VALUE "]"

%import common.ESCAPED_STRING
%import common.WS
%ignore WS
"""

conditions_map = {}
condition_expr = ""
counter = 0

class SQLTransformer(Transformer):
    # def __init__(self):
        # super().__init__()
        # self.counter = [chr(i) for i in range(97, 123)]  # a, b, c, ...
        # self.conditions_map = {}
        # self.condition_expr = None

    def label_conditions(self, expr):
        global counter, conditions_map, condition_expr
        if isinstance(expr, dict):
            label = counter
            counter += 1
            conditions_map[label] = expr
            return label
        elif isinstance(expr, str):
            return expr
        elif isinstance(expr, list):
            return [self.label_conditions(e) for e in expr]
        elif isinstance(expr, tuple):
            return tuple(self.label_conditions(e) for e in expr)
        elif isinstance(expr, (int, float)):
            return expr
        else:
            # Assume it's an expression like a boolean operation string
            expr_str = str(expr)
            for k, v in conditions_map.items():
                expr_str = expr_str.replace(str(v), k)
            return expr

    def start(self, items):
        return items

    def stmt(self, items):
        return items

    def create_stmt(self, items):
        table_name = str(items[0])
        return {"action": "create_table", "name": table_name, "data": items[1]}

    def select_stmt(self, items):
        global counter, conditions_map, condition_expr

        attributes = items[0]
        table = str(items[1])
        if len(items) > 2:
            raw_expr = items[2]
            labeled_expr = self.label_conditions(raw_expr)
            condition_expr = labeled_expr
        ans = {
            "action": "select",
            "table": table,
            "attr": attributes,
            "eval": condition_expr,
            "conditions": conditions_map
        }
        counter = 0
        conditions_map = {}
        condition_expr = None
        return ans;

    def insert_stmt(self, items):
        return {"action": "insert", "table": str(items[0]), "values": items[1:]}

    def delete_stmt(self, items):
        global counter, conditions_map, condition_expr

        table = str(items[0])
        if len(items) > 1:
            raw_expr = items[1]
            labeled_expr = self.label_conditions(raw_expr)
            condition_expr = labeled_expr
        ans = {
            "action": "delete",
            "table": table,
            "eval": condition_expr,
            "conditions": conditions_map
        }
        counter = 0
        conditions_map = {}
        condition_expr = None
        return ans;

    def index_stmt(self, items):
        dict =  {"action": "index", "table": str(items[0]), "index": items[1], "attr": items[2]}
        if items[3] is not None:
            dict["params"] = [int(x) for x in items[3]]
        else:
            dict["params"] = []
        return dict

    def copy_stmt(self, items):
        return {"action": "copy", "table": str(items[0]), "from": str(items[1])}
    
    def drop_index_stmt(self, items):
        return {"action": "drop index", "table": items[2], "index": items[0], "attr": items[1]}
    
    def drop_table_stmt(self, items):
        return {"action": "drop table", "table": items[0]}
    
    def condition(self, items):
        if (str(items[2]) == "closest"):
            return {"field": items[0], "range_search": False, "point": items[1], "knn": items[3]}
        if (str(items[2]) == "radius"):
            return {"field": items[0], "range_search": False, "point": items[1], "radius": items[3]}
        if str(items[1]) == "between":
                return {"field": items[0], "range_search": True, "op": "between", "range_start": items[2], "range_end": items[3]}
        elif str(items[1]) == "==":
            return {"field": items[0], "range_search": False, "op": str(items[1]), "value": items[2]}
        else:
            range_start = -1
            range_end = 1
            if str(items[1]) == ">":
                range_start = items[2]
            elif str(items[1]) == "<":
                range_end = items[2]
            elif str(items[1]) == "<=":
                range_end = items[2]
            elif str(items[1]) == ">=":
                range_start = items[2]
            elif str(items[1] == "!="):
                val = items[2]
                return {"field": items[0], "range_search": True, "op": items[1], "range_start": range_start, "range_end": range_end, "value": val}

            return {"field": items[0], "range_search": True, "op": items[1], "range_start": range_start, "range_end": range_end}


    def and_expr(self, items):
        return f"({self.label_conditions(items[0])} and {self.label_conditions(items[1])})"

    def or_expr(self, items):
        return f"({self.label_conditions(items[0])} or {self.label_conditions(items[1])})"

    def not_expr(self, items):
        return f"(not {self.label_conditions(items[0])})"

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
            if i < len(items) and items[i] is not None and items[i] in ["rtree", "bptree", "seq", "isam", "hash", "brin"]:
                key_index = items[i]
                i+=1
            dict[attr_name] = {"type": attr_type, "index": key_index}
            if i < len(items) and items[i] is None:
                i+=1
            else:
                dict[attr_name]["params"] = [int(x) for x in items[i]]
                i+=1
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
        return tok.value.lower()

    def INDEX(self, tok):
        return tok.value.lower()

    def VALUE(self, tok):
        return tok.value.strip('"')  # remove quotes if present

    def RADIUS(self, tok):
        return tok.value.lower()

    def CLOSEST(self, tok):
        return tok.value.lower()

    def BETWEEN(self, tok):
        return tok.value.lower()

    def KEY(self, tok):
        return tok.value.lower()

    def ALL(self, tok):
        return str(tok)

    def varchar(self, items):
        return f"varchar[{items[0]}]"


# if __name__ == "__main__":
#     parser = Lark(sql_grammar, start="start", parser="lalr", transformer=SQLTransformer())
#     # parser = Lark(sql_grammar, start="start", parser="lalr")

#     # Example: read SQL statements from a file
#     with open("ParserSQL/test2.txt", "r") as f:
#         sql_code = f.read()
#     try:
#         result = parser.parse(sql_code)
#         print(json.dumps(result, indent=4))
#         # print(result.pretty())
#     except Exception as e:
#         print("Error parsing input:", e)