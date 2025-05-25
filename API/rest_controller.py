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

@app.post("/query")
def parse_sql_query(input: QueryInput):
    sql_code = input.query
    try:
        result = parser.parse(sql_code)
    except Exception as e:
        print("ERROR:", e)
        return JSONResponse(
            content={"error": "Error parsing input", "details": str(e)},
            status_code=400
        )
    for line in result:
        if isinstance(line, list):
            response = convert(line[0])
        else:
            response = convert(line)
    
    print(response)
    return response

print("comenzar")

consultas = ["", "", "", "", "", ""]
# consultas[0]= "API/consultas/crear_tabla.txt"
# consultas[1]= "API/consultas/crear_indice.txt"
# consultas[2]= "API/consultas/insertar_datos.txt"
# consultas[3]= "API/consultas/select_datos.txt"
consultas[4] = "API/consultas/prueba2.txt"
# consultas[5]= "API/consultas/copy.txt"
# consultas[5]= "ParserSQL/test2.txt"

# eliminar todo lo de la  carpeta Schema
def eliminar_directorio(directorio):
    for root, dirs, files in os.walk(directorio, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
eliminar_directorio("Schema")

for c in consultas:
    if c != "":
        with open(c, "r") as f:
            sql_code = f.read()

        test_query = QueryInput(
            query=sql_code
        )
        parse_sql_query(test_query)

print("terminar")