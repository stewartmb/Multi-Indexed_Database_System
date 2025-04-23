from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()


class TextoInput(BaseModel):
    texto: str

class QueryInput(BaseModel):
    query: str

@app.post("/test")
def guardar_texto_a_archivo(input: TextoInput):
    with open('test.dat', 'w') as f:
        f.write(input.texto)
    return JSONResponse(content={"mensaje": "Texto guardado correctamente."})

@app.post("/query")
def guardar_texto_a_archivo(input: QueryInput):
    if (input.query == "CREATE TABLE":
        return {"nombre":"10s", "apellido":"20s", "edad": "i", "ciudad": "25s"}
