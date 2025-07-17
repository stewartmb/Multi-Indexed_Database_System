import json
import os
from fastapi import HTTPException

def create_meta(data: dict, name: str) -> None:
    """Agrega un nuevo diccionario con clave 'name' a una lista en MetaData"""
    filename = "Schema/metadata"+".meta"
    all_data = []

    # Si el archivo existe, cargar la lista existente
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                print("Advertencia: El archivo estaba corrupto. Se sobrescribirá.")

    # Eliminar entrada anterior si ya existía con ese nombre
    all_data = [item for item in all_data if name not in item]

    # Agregar nueva entrada
    all_data.append({name: data})

    # Guardar la lista actualizada
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)

    print(f"Dato guardado bajo la clave '{name}' en '{filename}'.")

def select_meta(name: str) -> dict:
    """Busca y devuelve el diccionario correspondiente a 'name' desde MetaData"""
    filename = "Schema/metadata"+".meta"

    
    if not os.path.exists(filename):
        print(f"El archivo '{filename}' no existe en {os.getcwd()}.")
        return {}

    with open(filename, "r", encoding="utf-8") as f:
        try:
            all_data = json.load(f)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error: No se pudo leer el archivo metadata.")

    for item in all_data:
        if name in item:
            return item[name]

    raise HTTPException(status_code=404, detail=f"No se encontró una entrada con el nombre '{name}'.")

def delete_meta(name: str) -> None:
    """Elimina la entrada con clave 'name' de la lista en MetaData"""
    filename = "Schema/metadata"+".meta"
    all_data = []

    # Si el archivo existe, cargar la lista existente
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                print("Advertencia: El archivo estaba corrupto. Se sobrescribirá.")

    # Eliminar entrada anterior
    all_data = [item for item in all_data if name not in item]

    # Se vuelve a escribir el diccionario de metadata
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)

    print(f"Se elimino la entrada '{name}' en '{filename}'.")


def get_info_from_meta() -> dict:
    print("Currently in:", os.getcwd())
    """Devuelve el diccionario"""
    filename = "Schema/metadata"+".meta"

    if not os.path.exists(filename):
        print(f"El archivo '{filename}' no existe en {os.getcwd()}.")
        return {}

    with open(filename, "r", encoding="utf-8") as f:
        try:
            all_data = json.load(f)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error: No se pudo leer el archivo metadata.")

    info = {"name":"Schema 1", "tables":[]}

    for table in all_data:
        new = {}
        name = None
        for attr in table.keys():
            name = attr

        new["name"] = name
        new["indices"] = []
        for col in table[name]["columns"].keys():
            extra = ""
            if table[name]["key"] == col:
                extra += " (PK)"
            if table[name]["columns"][col]["index"] != None:
                extra += f" ({table[name]['columns'][col]['index']})"
            extra += " type::" + table[name]["columns"][col]["type"]
            new["indices"].append(col + extra)

        info["tables"].append(new)

    return [info]



def create_index_meta():
    filename = "Schema/indexes"+".meta"

    dict = {
        "hash": None,
        "btree": None
    }

    if os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            try:
                json.dump(dict, f, indent=4)
            except json.JSONDecodeError:
                print("Advertencia: El archivo estaba corrupto. Se sobrescribirá.")
    print(f"Informacion de índices creado en {filename}")

def set_index_meta(index: str, params: list):
    filename = "Schema/indexes"+".meta"

    dict = {
        "hash": None,
        "btree": None
    }

    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(dict, f, indent=4)
            print("a")

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                all_data = json.load(f)
            except json.JSONDecodeError:
                print("Advertencia: El archivo estaba corrupto. Se sobrescribirá.")

    all_data[index] = params;

    if os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            try:
                json.dump(all_data, f, indent=4)
            except json.JSONDecodeError:
                print("Advertencia: El archivo estaba corrupto. Se sobrescribirá.")

    print(f"Edited {filename} correcty.")

def select_index_meta():
    filename = "Schema/indexes"+".meta"

    if not os.path.exists(filename):
        print(f"El archivo '{filename}' no existe.")
        return {
            "hash": None,
            "btree": None
        }

    with open(filename, "r", encoding="utf-8") as f:
        try:
            all_data = json.load(f)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error: No se pudo leer el archivo metadata.")

    return all_data

