import sys
import os
import struct
import csv
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *
import math

# Constantes generales
AUX_ENCABEZADO_SIZE = 8   # Tamaño del encabezado en aux.bin (8 bytes para un int)
TAM_ENCABEZADO = 9        # Encabezado de datos.bin: 4+4+1 = 9 bytes

class Sequential:
    def __init__(self, table_format , name_key: str ,
                 nombre_datos='Sequential_Struct/datos.bin', 
                 nombre_aux='Sequential_Struct/sequencial_aux.bin', 
                 num_aux = 100):
        
        self.RT = RegistroType(table_format, name_key)               # Formato de los datos
        self.format_key = table_format[name_key]                     # Formato de la clave (KEY)
        self.tam_registro = self.RT.size+5                           # Tamaño del registro


        self.K = num_aux
        self.nombre_datos = nombre_datos
        self.nombre_aux = nombre_aux
        self._inicializar_archivos()

    def _inicializar_archivos(self):
        # datos.bin se inicializa con un encabezado de 9 bytes:
        # (num_registros en datos.bin, puntero_inicio, lugar_inicio)
        if not os.path.exists(self.nombre_datos):
            with open(self.nombre_datos, 'wb') as f:
                f.write(struct.pack('iib', 0, -2, 0))
        # aux.bin se inicializa con un encabezado de 4 bytes (contador de registros = 0)
        if not os.path.exists(self.nombre_aux):
            with open(self.nombre_aux, 'wb') as f:
                f.write(struct.pack('ii', 0, 0))  # (efectivos=0, totales=0)

    # Métodos para manejar el encabezado de aux.bin
    def _leer_encabezado_aux(self):
        with open(self.nombre_aux, 'rb') as f:
            data = f.read(AUX_ENCABEZADO_SIZE)
            if len(data) != AUX_ENCABEZADO_SIZE:
                return (0, 0)  # Valores por defecto si el archivo está corrupto
            return struct.unpack('ii', data)  # Devuelve tupla (efectivos, totales)

    def _actualizar_encabezado_aux(self, efectivos, totales):
        with open(self.nombre_aux, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack('ii', efectivos, totales))

    # Métodos para el encabezado de datos.bin
    def _leer_encabezado(self):
        with open(self.nombre_datos, 'rb') as f:
            return struct.unpack('iib', f.read(TAM_ENCABEZADO))

    def _escribir_encabezado(self, num, pos, lugar):
        with open(self.nombre_datos, 'r+b') as f:
            f.seek(0)
            f.write(struct.pack('iib', num, pos, lugar))

    # Métodos de lectura/escritura de registros:
    # En datos.bin, los registros comienzan después de 9 bytes; en aux.bin, después de 4 bytes.
    def _leer_registro(self, archivo, pos):
        with open(archivo, 'rb') as f:
            if archivo == self.nombre_datos:
                offset = TAM_ENCABEZADO + pos * self.tam_registro
            else:
                offset = AUX_ENCABEZADO_SIZE + pos * self.tam_registro
            f.seek(offset)    
            data = f.read(self.tam_registro-5) # registro + puntero
            record = self.RT.from_bytes(data)
            # Leer puntero
            f.seek(offset+self.RT.size)
            puntero = f.read(5) # puntero
            if len(puntero) < 5:
                raise ValueError(f"No se puede leer puntero en {archivo} en posición {pos}")
            if len(data) < self.tam_registro - 5:
                raise ValueError(f"No se puede leer registro en {archivo} en posición {pos}")
            return record + list(struct.unpack('ib', puntero))  # Devuelve tupla (registro, sig, lugar)
    
    def _leer_puntero(self, archivo, pos):
        with open(archivo, 'rb') as f:
            if archivo == self.nombre_datos:
                offset = TAM_ENCABEZADO + pos * self.tam_registro
            else:
                offset = AUX_ENCABEZADO_SIZE + pos * self.tam_registro
            f.seek(offset+self.RT.size)
            data = f.read(5) # puntero
            if len(data) < 5:
                raise ValueError(f"No se puede leer puntero en {archivo} en posición {pos}")
            return struct.unpack('ib', data)  # Devuelve tupla (sig, lugar)
         
    def _escribir_registro(self, archivo, pos, registro):
        with open(archivo, 'r+b') as f:
            if archivo == self.nombre_datos:
                offset = TAM_ENCABEZADO + pos * self.tam_registro
            else:
                offset = AUX_ENCABEZADO_SIZE + pos * self.tam_registro
            f.seek(offset)  
            f.write(self.RT.to_bytes(registro[:-2]))  # Escribir registro sin puntero
            f.seek(offset+self.RT.size)
            f.write(struct.pack('ib', registro[-2], registro[-1]))  # Escribir puntero

    def _escribir_puntero(self, archivo, pos, sig, lugar):
        with open(archivo, 'r+b') as f:
            if archivo == self.nombre_datos:
                offset = TAM_ENCABEZADO + pos * self.tam_registro
            else:
                offset = AUX_ENCABEZADO_SIZE + pos * self.tam_registro
            f.seek(offset+self.RT.size)
            f.write(struct.pack('ib', sig, lugar))
    
    # Agregar registro a aux.bin
    def _agregar_aux(self, registro):
        efectivos, totales = self._leer_encabezado_aux()
        with open(self.nombre_aux, 'r+b') as f:
            offset = AUX_ENCABEZADO_SIZE + totales * self.tam_registro
            f.seek(offset)
            f.write(self.RT.to_bytes(registro[:-2]))  # Escribir registro sin puntero
            f.seek(offset+self.RT.size)
            f.write(struct.pack('ib', registro[-2], registro[-1]))  # Escribir puntero

        # Actualizar contadores (si no es eliminado, incrementar ambos)
        nuevo_efectivos = efectivos + (0 if registro[-1] == -1 else 1)
        self._actualizar_encabezado_aux(nuevo_efectivos, totales + 1)

    def _contar_aux(self):
        _, totales =self._leer_encabezado_aux()
        return totales

    def _efectiv_aux(self):
        efectivos, _ =self._leer_encabezado_aux()
        return efectivos
    
    # Función de inserción según la lógica solicitada (ver código anterior)
    def add(self, record: list = None):
        # Lectura del encabezado de datos.bin: (número de registros, puntero_inicio, lugar_inicio)
        num_reg, ptr_inicio, lugar_inicio = self._leer_encabezado()
        
        record = self.RT.correct_format(record)  # Formato correcto

        # Agregar un 2 numeros a la lista registro
        record = record + [-1, -1]  # Inicializar sig y lugar en 0


        # LUGAR = record[-1] 
        # SIG = record[-2]

        # Caso 1: Primer registro (archivos vacíos)
        if ptr_inicio == -2:
            record[-1] = 0      # Se inserta en aux.bin
            record[-2] = -1
            pos_aux = self._contar_aux()
            self._agregar_aux(record)
            self._escribir_encabezado(0, pos_aux, 0)
            return

        # Verificar si el ID ya existe
        record_key = self.RT.get_key(record)
        _,_,_,_, reg = self.search_aux(record_key)
        if reg is not None:
            return print(f"❌ Registro con ID {record_key} ya existe.")
        # Caso 2: datos.bin vacío (todos los registros actuales están en aux.bin)
        if num_reg == 0:
            temp_ptr = ptr_inicio  # Se recorre aux.bin
            prev_ptr = None
            # Ubicar el punto de inserción recorriendo aux.bin de forma secuencial
            while temp_ptr != -1:
                reg_temp = self._leer_registro(self.nombre_aux, temp_ptr)
                record_key = self.RT.get_key(record)
                reg_temp_key = self.RT.get_key(reg_temp)
                if record_key < reg_temp_key:
                    break
                prev_ptr = temp_ptr
                temp_ptr = reg_temp[-2]

            new_pos = self._contar_aux()  # Nueva posición en aux.bin
            record[-1] = 0             # Indica que va a aux.bin
            record[-2] = temp_ptr        # El record nodo apunta al que era siguiente
            self._agregar_aux(record)

            # Actualizar la cadena: si se inserta al inicio se actualiza el encabezado
            if prev_ptr is None:
                self._escribir_encabezado(num_reg, new_pos, 0)
            else:
                reg_prev = self._leer_registro(self.nombre_aux, prev_ptr)
                reg_prev[-2] = new_pos
                reg_prev[-1] = 0
                self._escribir_registro(self.nombre_aux, prev_ptr, reg_prev)

            # Verificar si aux.bin llega a su límite y debe reconstruirse
            if self._contar_aux() >= self.K:
                self.reconstruir()
            return

        # Caso 3: datos.bin no vacío
        # Búsqueda binaria en datos.bin para hallar el posible punto de inserción
        low, high = 0, num_reg - 1
        sucesor_index = None

        while low <= high:
            mid = (low + high) // 2
            reg_mid = self._leer_registro(self.nombre_datos, mid)
            reg_mid_key = self.RT.get_key(reg_mid)
            record_key = self.RT.get_key(record)
            if reg_mid_key < record_key:
                low = mid + 1
            else:
                sucesor_index = mid
                high = mid - 1

        # Determinar el punto inicial para la búsqueda secuencial
        if sucesor_index is not None:
            # Si el registro candidato se encuentra eliminado, avanzar hasta encontrar uno válido.
            reg_sucesor = self._leer_registro(self.nombre_datos, sucesor_index)
            while reg_sucesor[-1] == -1:
                sucesor_index -= 1
                if sucesor_index < 0:
                    # Si se retrocede más allá del inicio, se inicia desde el encabezado
                    temp_ptr = ptr_inicio
                    current_lugar = lugar_inicio
                    break
                reg_sucesor = self._leer_registro(self.nombre_datos, sucesor_index)
            else:
                # Iniciar desde el nodo sucesor obtenido (sin restar 1)
                temp_ptr = sucesor_index
                current_lugar = 1
        else:
            # Si no se encontró candidato, iniciar desde el puntero del encabezado
            temp_ptr = ptr_inicio
            current_lugar = lugar_inicio

        # Búsqueda secuencial a partir del punto determinado para encontrar el lugar de inserción
        prev_ptr = None
        prev_lugar = None
        while temp_ptr != -1:
            archivo_actual = self.nombre_datos if current_lugar == 1 else self.nombre_aux
            reg_temp = self._leer_registro(archivo_actual, temp_ptr)
            reg_temp_key = self.RT.get_key(reg_temp)
            record_key = self.RT.get_key(record)
            if record_key < reg_temp_key:
                break
            prev_ptr = temp_ptr
            prev_lugar = current_lugar
            temp_ptr = reg_temp[-2]
            # Cuando avanzamos, si el registro proviene de datos.bin o aux.bin, 
            # se toma el campo 'lugar' que figura en el registro siguiente.
            current_lugar = reg_temp[-1]

        new_pos = self._contar_aux()  # Nueva posición en aux.bin
        record[-1] = 0             # Se inserta en aux.bin
        record[-2] = temp_ptr        # El record nodo apunta a lo que era siguiente en la cadena
        self._agregar_aux(record)

        if prev_ptr is None:
            # Si se inserta al inicio, actualizamos el encabezado de datos.bin para apuntar al record nodo de aux.bin.
            self._escribir_encabezado(num_reg, new_pos, 0)
        else:
            archivo_prev = self.nombre_datos if prev_lugar == 1 else self.nombre_aux
            reg_prev = self._leer_registro(archivo_prev, prev_ptr)
            reg_prev[-2] = new_pos
            reg_prev[-1] = 0
            self._escribir_registro(archivo_prev, prev_ptr, reg_prev)

        if self._contar_aux() >= self.K:
            self.reconstruir()

  # ---------------------------------------------------------------------------
    # Función de reconstrucción sin utilizar mucha RAM:
    # Se recorre la cadena enlazada (usando el puntero del encabezado) y se escribe cada
    # registro uno a uno en un archivo temporal (temp.bin). Al escribir, se actualiza el campo
    # 'lugar' (a 1, para datos.bin) y se reajusta el campo 'sig' para que la secuencia en temp.bin
    # sea consecutiva (el primero apunta al segundo, etc.). Luego se reemplaza datos.bin por temp.bin
    # y se reinicializa aux.bin (con encabezado = 0).
    def reconstruir(self):
        # Primero, se obtiene el puntero de inicio y se cuenta la cadena.
        num_reg, ptr_inicio, lugar_inicio = self._leer_encabezado()
        num_reg_aux = self._efectiv_aux()
        count = num_reg + num_reg_aux
        current_ptr = ptr_inicio
        current_lugar = lugar_inicio

        # En nuestro record archivo datos.bin, el número total de registros será 'count'.
        # Se crea temp.bin y se escribe el encabezado con (count, 0, 1).
        with open("temp.bin", "wb") as temp:
            temp.write(struct.pack('iib', count, 0, 1))
            # Segunda pasada: se recorre nuevamente la cadena y se escribe cada registro.
            current_ptr = ptr_inicio
            current_lugar = lugar_inicio
            index = 0  # Índice del registro en el record archivo.
            while current_ptr != -1:
                archivo_actual = self.nombre_datos if current_lugar == 1 else self.nombre_aux
                # Se lee el registro original.
                reg = self._leer_registro(archivo_actual, current_ptr)
                # Se guarda el puntero original para avanzar en la cadena.
                next_ptr = reg[-2]
                next_lugar = reg[-1] if next_ptr != -1 else 0
                # Se actualiza el registro para que pase a formar parte de datos.bin.
                reg[-1] = 1
                # Se reajusta el puntero para el record archivo:
                if index < count - 1:
                    reg[-2] = index + 1
                else:
                    reg[-2] = -1
                # Se escribe el registro en temp.bin.
                temp.write(self.RT.to_bytes(reg[:-2]))
                temp.write(struct.pack('ib', reg[-2], reg[-1]))  # Escribir puntero
                # Avanzar al siguiente registro de la cadena.
                current_ptr = next_ptr
                current_lugar = next_lugar
                index += 1

        # Se reemplaza el archivo datos.bin antiguo por temp.bin.
        os.remove(self.nombre_datos)
        os.rename("temp.bin", self.nombre_datos)

        # Se elimina el aux.bin y se reinicializa con su encabezado (0 registros).
        os.remove(self.nombre_aux)
        with open(self.nombre_aux, 'wb') as f:
            f.write(struct.pack('ii', 0, 0))




    # Función de búsqueda (binary + secuencial)
    # Recorre la cadena enlazada y devuelve una tupla:
    # (prev_ptr, prev_lugar, pos_actual, lugar_actual, registro)
    def search_aux(self, id_busqueda):
        num_reg, ptr_inicio, lugar_inicio = self._leer_encabezado()
        if num_reg == 0:
            return (None, None, -1, -1, None)  # No hay registros
        # Si justo el puntero del encabezado
        archivo_actual = self.nombre_datos if lugar_inicio == 1 else self.nombre_aux
        primero = self._leer_registro(archivo_actual, ptr_inicio)
        primero_id = self.RT.get_key(primero)
        if id_busqueda == primero_id:
            return (None, None, ptr_inicio, lugar_inicio, primero)
        
        # Primero, búsqueda binaria en datos.bin para encontrar posible sucesor
        low, high = 0, num_reg - 1
        sucesor_index = None

        while low <= high:
            mid = (low + high) // 2
            reg_mid = self._leer_registro(self.nombre_datos, mid)
            reg_mid_key = self.RT.get_key(reg_mid)
            # print( type(reg_mid_key), type(id_busqueda))
            if reg_mid_key < id_busqueda:
                low = mid + 1
            else:
                sucesor_index = mid
                high = mid - 1

        # Determinar desde dónde arrancar la búsqueda secuencial
        if sucesor_index is not None:
            reg_sucesor = self._leer_registro(self.nombre_datos, sucesor_index)
            while reg_sucesor[-1] == -1:  # Saltar eliminados
                sucesor_index -= 1
                if sucesor_index <= 0:
                    current_ptr = ptr_inicio
                    current_lugar = lugar_inicio
                    break
                reg_sucesor = self._leer_registro(self.nombre_datos, sucesor_index)
            else:
                current_ptr = sucesor_index-1
                current_lugar = 1  # datos.bin
        else:
            current_ptr = ptr_inicio
            current_lugar = lugar_inicio

        # Ahora búsqueda secuencial desde el punto correcto
        prev_ptr = None
        prev_lugar = None
        while current_ptr != -1:
            archivo_actual = self.nombre_datos if current_lugar == 1 else self.nombre_aux
            reg = self._leer_registro(archivo_actual, current_ptr)
            reg_id = self.RT.get_key(reg)
            if reg_id == id_busqueda:
                return (prev_ptr, prev_lugar, current_ptr, current_lugar, reg)
            if reg_id > id_busqueda:
                break
            prev_ptr = current_ptr
            prev_lugar = current_lugar
            current_ptr = reg[-2]
            current_lugar = reg[-1]

        return (prev_ptr, prev_lugar, -1, -1, None)  # No encontrado
    
    def search(self, id_busqueda):
        _, _, _, _, reg = self.search_aux(id_busqueda)        
        return reg

    # Funcion de busqueda por rango de ventas
    # Recibe 2 ID y devuelve una lista de registros que cumplen con el rango
    # Primero usa la funcion buscar para el limite inferior y apartir de ese usa los punteros hasta llegar a un ID>= limite superior
    def search_range(self, id_inferior, id_superior):
        resultado = []
        if (id_inferior>id_superior):
            print("inserte correctamente el (limite inferior, limite superior)")
            return resultado
        prev_ptr, prev_lugar, current_ptr, current_lugar, reg = self.search_aux(id_inferior)
        if reg is None:
            if prev_ptr is None:
                # leer encabezado 
                num_reg, ptr_inicio, lugar_inicio = self._leer_encabezado()
                if num_reg == 0:
                    print("No hay registros en el archivo")
                    return resultado
                # Si no se encuentra un prev, se comienza desde el encabezado
                archivo_actual = self.nombre_datos if lugar_inicio == 1 else self.nombre_aux
                reg = self._leer_registro(self.nombre_datos, ptr_inicio)
                reg_id = self.RT.get_key(reg)
                current_ptr = ptr_inicio
                current_lugar = lugar_inicio
            else: # si se encuentra el prev
                archivo_actual = self.nombre_datos if prev_lugar == 1 else self.nombre_aux
                reg = self._leer_registro(archivo_actual, prev_ptr)
                print(reg)
                reg_id = self.RT.get_key(reg)
                current_ptr = reg[-2]
                current_lugar = reg[-1]

        
        reg_id = self.RT.get_key(reg)
        while reg_id <= id_superior:
            if reg_id >= id_inferior:
                resultado.append(reg)
            archivo_actual = self.nombre_datos if current_lugar == 1 else self.nombre_aux
            reg = self._leer_registro(archivo_actual, current_ptr)
            reg_id = self.RT.get_key(reg)
            current_ptr = reg[-2]
            current_lugar = reg[-1]
            if current_ptr == -1 or current_lugar ==-1:
                return resultado
        return resultado
    

    # Función de eliminación lógica:
    # Se "desconecta" el registro de la cadena (redireccionando el previo al siguiente)
    # y se marca como eliminado cambiando su puntero a (-1, -1).
    # Además, se actualiza el contador correspondiente en el encabezado (datos.bin o aux.bin)
    def eliminar(self, id_busqueda):
        prev_ptr, prev_lugar, current_ptr, current_lugar, reg = self.search_aux(id_busqueda)
        if reg is None:
            print(f"❌ Registro con id {id_busqueda} no encontrado.")
            return False

        next_ptr = reg[-2]
        next_lugar = reg[-1] if next_ptr != -1 else 0

        # Actualiza la cadena:
        if prev_ptr is None:
            # Si el registro a eliminar es la cabeza, se actualiza el encabezado de datos.bin.
            num_reg, _, _ = self._leer_encabezado()
            self._escribir_encabezado(num_reg - (1 if current_lugar == 1 else 0),
                                       next_ptr,
                                       next_lugar)
            print(self._leer_encabezado())
        else:
            archivo_prev = self.nombre_datos if prev_lugar == 1 else self.nombre_aux
            reg_prev = self._leer_registro(archivo_prev, prev_ptr)
            reg_prev[-2] = next_ptr
            reg_prev[-1] = next_lugar if next_ptr != -1 else 0
            self._escribir_registro(archivo_prev, prev_ptr, reg_prev)

        # Se marca como eliminado: puntero y lugar a -1.
        reg[-2] = -1
        reg[-1] = -1
        archivo_actual = self.nombre_datos if current_lugar == 1 else self.nombre_aux
        self._escribir_registro(archivo_actual, current_ptr, reg)

        # Actualizar el contador en el encabezado correspondiente.
        if current_lugar == 1:
            num_reg, ptr, lugar = self._leer_encabezado()
            self._escribir_encabezado(num_reg - 1, ptr, lugar)
        else:
            efectiv,totales = self._leer_encabezado_aux()
            self._actualizar_encabezado_aux(efectiv-1, totales)

        print(f"✅ Registro con id {id_busqueda} eliminado lógicamente.")
        return True

    def mostrar(self):
        num_reg, ptr, lugar = self._leer_encabezado()
        print(f"\n📦 Mostrando registros (Inicio en posición {ptr}):\n")
        while ptr != -1:
            archivo_actual = self.nombre_datos if lugar == 1 else self.nombre_aux
            reg = self._leer_registro(archivo_actual, ptr)
            self.RT._print(reg)
            ptr = reg[-2]
            lugar = reg[-1]



