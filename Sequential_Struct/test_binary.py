import Indice_Sequential_file as archivo
import os

def test_index():
    # Crear un registro de índice
    index_record = archivo.Index_Record(key="A1", pos=0, next=1)
    print ("Registro de índice original:")
    print (index_record)

    # Convertir el registro a bytes
    index_bytes = index_record.to_bytes(format_key='3s')
    print("Bytes del registro de índice:", index_bytes)

    # Reconstruir el registro desde los bytes
    reconstructed_index = archivo.Index_Record.from_bytes(index_bytes, format_key='3s')
    print ( reconstructed_index)
    print("Registro de índice reconstruido:")
    print("Clave:", reconstructed_index.key)
    print("Posición:", reconstructed_index.pos)
    print("Siguiente posición:", reconstructed_index.next)

    # Verificar que los datos sean consistentes
    print("Verificando datos...")
    if reconstructed_index.key != index_record.key:
        raise ValueError("Error: La clave no coincide", reconstructed_index.key, index_record.key, reconstructed_index , index_record) 

    print("Prueba exitosa: Los datos del registro de índice son consistentes.")

test_index()