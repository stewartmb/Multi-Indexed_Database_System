from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()


class TextoInput(BaseModel):
    texto: str

@app.post("/test")
def guardar_texto_a_archivo(input: TextoInput):
    with open('test.dat', 'w') as f:
        f.write(input.texto)
    return JSONResponse(content={"mensaje": "Texto guardado correctamente."})
