import json
import os

def create(data: dict, name: str) -> None:
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

def select(name: str) -> dict:
    """Busca y devuelve el diccionario correspondiente a 'name' desde MetaData"""
    filename = "Schema/metadata"+".meta"

    if not os.path.exists(filename):
        print(f"El archivo '{filename}' no existe.")
        return {}

    with open(filename, "r", encoding="utf-8") as f:
        try:
            all_data = json.load(f)
        except json.JSONDecodeError:
            print("Error: No se pudo leer el archivo. ¿Está corrupto?")
            return {}

    for item in all_data:
        if name in item:
            return item[name]

    print(f"No se encontró una entrada con el nombre '{name}'.")
    return {}