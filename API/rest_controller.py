from fastapi import FastAPI
import os
import sys
from lark import Lark
from pydantic import BaseModel
from fastapi.responses import JSONResponse
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from ParserSQL.parser import *
import services

app = FastAPI()
parser = Lark(sql_grammar, start='start', parser='lalr', transformer=SQLTransformer())

class QueryInput(BaseModel):
    query: str

#@app.post("/query")
def parse_sql_query(input: QueryInput):
    sql_code = input.query
    try:
        result = parser.parse(sql_code)
    except Exception as e:
        return JSONResponse(
            content={"error": "Error parsing input", "details": str(e)},
            status_code=400
        )
    for line in result:
        services.convert(line)

with open("test3.txt", "r") as f:
    sql_code = f.read()

test_query = QueryInput(
    query=sql_code
)
parse_sql_query(test_query)