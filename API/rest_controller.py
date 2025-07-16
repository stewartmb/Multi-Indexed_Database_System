import traceback
from fastapi import FastAPI, UploadFile, File
import os
import sys
from lark import Lark, UnexpectedToken, UnexpectedEOF, UnexpectedCharacters
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from ParserSQL.parser import *
from API.services import *
from typing import List

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

    except UnexpectedToken as e:
        details = ""
        if e.token.type == "$END":
            details += "fin de entrada inesperado\n"
        else:
            details += f"token inesperado '{e.token}' \n"
        details += "se esperaba alguno de las siguientes opciones: [" + ', '.join(list(e.expected)) + "]" + "\n"
        details += "detalles:\n\n"
        details += e.get_context(sql_code)

        print({"error": "Unexpected token in input", "details": details + str(e)})
        return JSONResponse(
            content={"error": "Unexpected token in input", "details": details + str(e)},
            status_code=400
        )

    except Exception as e:
        print("ERROR:", e)
        return JSONResponse(
            content={"error": "Error parsing input", "details": ''.join(traceback.format_exception(type(e), e, e.__traceback__))},
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
            content={"error": "Error processing parsed result", "details": ''.join(traceback.format_exception(type(e), e, e.__traceback__))},
            status_code=400
        )
    return response


@app.post("/upload_files/")
async def upload_files(files: List[UploadFile] = File(...)):
    # Puedes guardarlos o procesarlos aquí
    file_names = []
    for file in files:
        contents = await file.read()
        # Por ejemplo, guardarlo:
        with open(f"uploaded_{file.filename}", "wb") as f:
            f.write(contents)
        file_names.append(file.filename)
    return JSONResponse(content={"message": "Files uploaded successfully", "files": file_names})
