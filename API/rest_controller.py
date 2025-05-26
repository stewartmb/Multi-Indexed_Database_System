import traceback
from fastapi import FastAPI
import os
import sys
from lark import Lark
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from ParserSQL.parser import *
from API.services import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] to be specific
    allow_credentials=True,
    allow_methods=["*"],  # or ["GET", "POST"]
    allow_headers=["*"],
)

parser = Lark(sql_grammar, start='start', parser='lalr', transformer=SQLTransformer())

class QueryInput(BaseModel):
    query: str


@app.get("/")
def read_root():
    return {"state": "Running"}

@app.get("/info")
def get_info():
    return JSONResponse(
        content={"info": get_info_from_meta()},
        status_code=200
    )

@app.post("/query")
def parse_sql_query(input: QueryInput):
    sql_code = input.query
    try:
        result = parser.parse(sql_code)
    except Exception as e:
        print("ERROR:", e)
        return JSONResponse(
            content={"error": "Error parsing input", "details": str(e)},
            status_code=500
        )
    try:
        for line in result:
            if isinstance(line, list):
                response = execute_parsed_query(line[0])
            else:
                response = execute_parsed_query(line)
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exception(type(e), e, e.__traceback__)
        return JSONResponse(
            content={"error": "Error processing parsed result", "details": str(e)},
            status_code=400
        )
    return response