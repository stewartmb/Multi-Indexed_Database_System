import os
from PIL import Image
import math
import sys


def resize_to_256_square(image_path, output_path, z):
    with Image.open(image_path) as img:
        original_width, original_height = img.size

        # Si ya es z x z, se puede guardar directamente
        if original_width == z and original_height == z:
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(output_path)
            return

        # Ajustar área a z*z manteniendo la relación de aspecto
        aspect_ratio = original_width / original_height
        target_area = z * z

        new_height = int(math.sqrt(target_area / aspect_ratio))
        new_width = int(aspect_ratio * new_height)

        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        img_final = img_resized.resize((z, z), Image.LANCZOS)

        if img_final.mode != "RGB":
            img_final = img_final.convert("RGB")
        img_final.save(output_path)
        print(f"Procesado: {output_path}")


def procesar_carpeta(carpeta_entrada, carpeta_salida,z):
    os.makedirs(carpeta_salida, exist_ok=True)
    for archivo in os.listdir(carpeta_entrada):
        if archivo.lower().endswith(".jpg") and "_reescalado" not in archivo:
            ruta_imagen = os.path.join(carpeta_entrada, archivo)
            nombre_base, extension = os.path.splitext(archivo)
            nuevo_nombre = f"{nombre_base}_reescalado{extension}"
            ruta_salida = os.path.join(carpeta_salida, nuevo_nombre)

            resize_to_256_square(ruta_imagen, ruta_salida,z)