import sys
import os
import struct
import csv
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from Utils.Registro import *

# Constantes generales
AUX_ENCABEZADO_SIZE = 8   # Tamaño del encabezado en aux.bin (8 bytes para un int)
TAM_ENCABEZADO = 9        # Encabezado de datos.bin: 4+4+1 = 9 bytes

formato = 'i30sif10sib'

class Registro:
    
    def __init__(self, id_venta, nombre, cantidad, precio, fecha, sig=-1, lugar=1):
        self.id = id_venta
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio
        self.fecha = fecha
        self.sig = sig
        self.lugar = lugar

    def to_bytes(self):
        return struct.pack(self.formato,
                           self.id,
                           self.nombre.encode('utf-8').ljust(30, b'\x00'),
                           self.cantidad,
                           self.precio,
                           self.fecha.encode('utf-8').ljust(10, b'\x00'),
                           self.sig,
                           self.lugar)

    @classmethod
    def from_bytes(cls, data):
        if len(data) != clsself.tam_registro:
            raise ValueError("Tamaño incorrecto al leer registro")
        unpacked = struct.unpack(cls.formato, data)
        return cls(unpacked[0],
                   unpacked[1].decode('utf-8').strip('\x00'),
                   unpacked[2],
                   round(unpacked[3],2),
                   unpacked[4].decode('utf-8').strip('\x00'),
                   unpacked[5],
                   unpacked[6])

class ArchivoSecuencial:
    def __init__(self, table_format , name_key: str ,
                 nombre_datos='Secuencial_Struct/datos.bin', 
                 nombre_aux='Secuencial_Struct/aux.bin', 
                 num_aux = None):
        
        self.RT = RegistroType(table_format, name_key)               # Formato de los datos
        self.format_key = table_format[name_key]                     # Formato de la clave (KEY)
        self.tam_registro = self.RT.size                             # Tamaño del registro


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
            data = f.read(self.tam_registro)
            if len(data) < self.tam_registro:
                raise ValueError(f"No se puede leer registro en {archivo} en posición {pos}")
            return self.RT.from_bytes(data)

    def _escribir_registro(self, archivo, pos, registro):
        with open(archivo, 'r+b') as f:
            if archivo == self.nombre_datos:
                offset = TAM_ENCABEZADO + pos * self.tam_registro
            else:
                offset = AUX_ENCABEZADO_SIZE + pos * self.tam_registro
            f.seek(offset)
            f.write(self.RT.to_bytes(registro))

    # Agregar registro a aux.bin
    def _agregar_aux(self, registro):
        efectivos, totales = self._leer_encabezado_aux()
        with open(self.nombre_aux, 'r+b') as f:
            offset = AUX_ENCABEZADO_SIZE + totales * self.tam_registro
            f.seek(offset)
            f.write(self.RT.to_bytes(registro))
        # Actualizar contadores (si no es eliminado, incrementar ambos)
        nuevo_efectivos = efectivos + (0 if registro.lugar == -1 else 1)
        self._actualizar_encabezado_aux(nuevo_efectivos, totales + 1)

    def _contar_aux(self):
        _, totales =self._leer_encabezado_aux()
        return totales

    def _efectiv_aux(self):
        efectivos, _ =self._leer_encabezado_aux()
        return efectivos
    
    # Función de inserción según la lógica solicitada (ver código anterior)
    def insertar(self, record):
        # Lectura del encabezado de datos.bin: (número de registros, puntero_inicio, lugar_inicio)
        num_reg, ptr_inicio, lugar_inicio = self._leer_encabezado()

        # Caso 1: Primer registro (archivos vacíos)
        if ptr_inicio == -2:
            record.lugar = 0      # Se inserta en aux.bin
            record.sig = -1
            pos_aux = self._contar_aux()
            self._agregar_aux(record)
            self._escribir_encabezado(0, pos_aux, 0)
            return

        # Verificar si el ID ya existe
        if self.buscar(record.id) is not None:
            print(f"❌ Registro con ID {record.id} ya existe.")
            return        
        # Caso 2: datos.bin vacío (todos los registros actuales están en aux.bin)
        if num_reg == 0:
            temp_ptr = ptr_inicio  # Se recorre aux.bin
            prev_ptr = None
            # Ubicar el punto de inserción recorriendo aux.bin de forma secuencial
            while temp_ptr != -1:
                reg_temp = self._leer_registro(self.nombre_aux, temp_ptr)
                if record.id < reg_temp.id:
                    break
                prev_ptr = temp_ptr
                temp_ptr = reg_temp.sig

            new_pos = self._contar_aux()  # Nueva posición en aux.bin
            record.lugar = 0             # Indica que va a aux.bin
            record.sig = temp_ptr        # El record nodo apunta al que era siguiente
            self._agregar_aux(record)

            # Actualizar la cadena: si se inserta al inicio se actualiza el encabezado
            if prev_ptr is None:
                self._escribir_encabezado(num_reg, new_pos, 0)
            else:
                reg_prev = self._leer_registro(self.nombre_aux, prev_ptr)
                reg_prev.sig = new_pos
                reg_prev.lugar = 0
                self._escribir_registro(self.nombre_aux, prev_ptr, reg_prev)

            # Verificar si aux.bin llega a su límite y debe reconstruirse
            if self._contar_aux() >= self.K:
                print("⚠️  Auxiliar lleno: se inicia reconstrucción.")
                self.reconstruir()
            return

        # Caso 3: datos.bin no vacío
        # Búsqueda binaria en datos.bin para hallar el posible punto de inserción
        low, high = 0, num_reg - 1
        sucesor_index = None

        while low <= high:
            mid = (low + high) // 2
            reg_mid = self._leer_registro(self.nombre_datos, mid)
            if reg_mid.id < record.id:
                low = mid + 1
            else:
                sucesor_index = mid
                high = mid - 1

        # Determinar el punto inicial para la búsqueda secuencial
        if sucesor_index is not None:
            # Si el registro candidato se encuentra eliminado, avanzar hasta encontrar uno válido.
            reg_sucesor = self._leer_registro(self.nombre_datos, sucesor_index)
            while reg_sucesor.lugar == -1:
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
            if record.id < reg_temp.id:
                break
            prev_ptr = temp_ptr
            prev_lugar = current_lugar
            temp_ptr = reg_temp.sig
            # Cuando avanzamos, si el registro proviene de datos.bin o aux.bin, 
            # se toma el campo 'lugar' que figura en el registro siguiente.
            current_lugar = reg_temp.lugar

        new_pos = self._contar_aux()  # Nueva posición en aux.bin
        record.lugar = 0             # Se inserta en aux.bin
        record.sig = temp_ptr        # El record nodo apunta a lo que era siguiente en la cadena
        self._agregar_aux(record)

        if prev_ptr is None:
            # Si se inserta al inicio, actualizamos el encabezado de datos.bin para apuntar al record nodo de aux.bin.
            self._escribir_encabezado(num_reg, new_pos, 0)
        else:
            archivo_prev = self.nombre_datos if prev_lugar == 1 else self.nombre_aux
            reg_prev = self._leer_registro(archivo_prev, prev_ptr)
            reg_prev.sig = new_pos
            reg_prev.lugar = 0
            self._escribir_registro(archivo_prev, prev_ptr, reg_prev)

        if self._contar_aux() >= self.K:
            print("⚠️  Auxiliar lleno: se inicia reconstrucción.")
            self.reconstruir()

  # ---------------------------------------------------------------------------
    # Función de reconstrucción sin utilizar mucha RAM:
    # Se recorre la cadena enlazada (usando el puntero del encabezado) y se escribe cada
    # registro uno a uno en un archivo temporal (temp.bin). Al escribir, se actualiza el campo
    # 'lugar' (a 1, para datos.bin) y se reajusta el campo 'sig' para que la secuencia en temp.bin
    # sea consecutiva (el primero apunta al segundo, etc.). Luego se reemplaza datos.bin por temp.bin
    # y se reinicializa aux.bin (con encabezado = 0).
    def reconstruir(self):
        print("\n🔄 Iniciando reconstrucción...")
        # Primero, se obtiene el puntero de inicio y se cuenta la cadena.
        num_reg, ptr_inicio, lugar_inicio = self._leer_encabezado()
        print("Numero de registros",num_reg)
        num_reg_aux = self._efectiv_aux()
        print("Numero de registros aux",num_reg_aux)
        count = num_reg + num_reg_aux
        current_ptr = ptr_inicio
        current_lugar = lugar_inicio
        # imprimir todo

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
                next_ptr = reg.sig
                next_lugar = reg.lugar if next_ptr != -1 else 0
                # Se actualiza el registro para que pase a formar parte de datos.bin.
                reg.lugar = 1
                # Se reajusta el puntero para el record archivo:
                if index < count - 1:
                    reg.sig = index + 1
                else:
                    reg.sig = -1
                # Se escribe el registro en temp.bin.
                temp.write(self.RT.to_bytes(reg))
                # Avanzar al siguiente registro de la cadena.
                current_ptr = next_ptr
                current_lugar = next_lugar
                index += 1

        # Se reemplaza el archivo datos.bin antiguo por temp.bin.
        os.remove(self.nombre_datos)
        os.rename("temp.bin", self.nombre_datos)
        print("✅ Reconstrucción completada. Nuevo datos.bin creado.")

        # Se elimina el aux.bin y se reinicializa con su encabezado (0 registros).
        os.remove(self.nombre_aux)
        with open(self.nombre_aux, 'wb') as f:
            f.write(struct.pack('ii', 0, 0))

        print("♻️  aux.bin reinicializado con 0 registros.\n")



    # Función de búsqueda (binary + secuencial)
    # Recorre la cadena enlazada y devuelve una tupla:
    # (prev_ptr, prev_lugar, pos_actual, lugar_actual, registro)
    def buscar(self, id_busqueda):
        num_reg, ptr_inicio, lugar_inicio = self._leer_encabezado()
        # Si justo el puntero del encabezado
        archivo_actual = self.nombre_datos if lugar_inicio == 1 else self.nombre_aux
        primero = self._leer_registro(archivo_actual, ptr_inicio)
        if id_busqueda == primero.id:
            return (None, None, ptr_inicio, lugar_inicio, primero)
        
        # Primero, búsqueda binaria en datos.bin para encontrar posible sucesor
        low, high = 0, num_reg - 1
        sucesor_index = None

        while low <= high:
            mid = (low + high) // 2
            reg_mid = self._leer_registro(self.nombre_datos, mid)
            if reg_mid.id < id_busqueda:
                low = mid + 1
            else:
                sucesor_index = mid
                high = mid - 1

        # Determinar desde dónde arrancar la búsqueda secuencial
        if sucesor_index is not None:
            reg_sucesor = self._leer_registro(self.nombre_datos, sucesor_index)
            while reg_sucesor.lugar == -1:  # Saltar eliminados
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
            if reg.id == id_busqueda:
                return (prev_ptr, prev_lugar, current_ptr, current_lugar, reg)
            if reg.id > id_busqueda:
                break
            prev_ptr = current_ptr
            prev_lugar = current_lugar
            current_ptr = reg.sig
            current_lugar = reg.lugar

        return None  # No encontrado
    

    # Funcion de busqueda por rango de ventas
    # Recibe 2 ID y devuelve una lista de registros que cumplen con el rango
    # Primero usa la funcion buscar para el limite inferior y apartir de ese usa los punteros hasta llegar a un ID>= limite superior
    def buscar_rango(self, id_inferior, id_superior):
        resultado = []
        if (id_inferior>id_superior):
            print("inserte correctamente el (limite inferior, limite superior)")
            return resultado
        _, _, current_ptr, current_lugar, reg = self.buscar(id_inferior)
        if reg is None:
            print(f"❌ Registro con id {id_inferior} no encontrado.")
            return resultado

        while reg.id <= id_superior:
            resultado.append(reg)
            archivo_actual = self.nombre_datos if current_lugar == 1 else self.nombre_aux
            reg = self._leer_registro(archivo_actual, current_ptr)
            current_ptr = reg.sig
            current_lugar = reg.lugar
            if current_ptr == -1 or current_lugar ==-1:
                return resultado
        return resultado
    

    # Función de eliminación lógica:
    # Se "desconecta" el registro de la cadena (redireccionando el previo al siguiente)
    # y se marca como eliminado cambiando su puntero a (-1, -1).
    # Además, se actualiza el contador correspondiente en el encabezado (datos.bin o aux.bin)
    def eliminar(self, id_busqueda):
        resultado = self.buscar(id_busqueda)
        if resultado is None:
            print(f"❌ Registro con id {id_busqueda} no encontrado.")
            return False
        prev_ptr, prev_lugar, current_ptr, current_lugar, reg = resultado
        print(f"prev_ptr: {prev_ptr}, prev_lugar: {prev_lugar}, current_ptr: {current_ptr}, "
              f"current_lugar: {current_lugar}, reg: {reg.__dict__}")
        next_ptr = reg.sig
        next_lugar = reg.lugar if next_ptr != -1 else 0

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
            reg_prev.sig = next_ptr
            reg_prev.lugar = next_lugar if next_ptr != -1 else 0
            self._escribir_registro(archivo_prev, prev_ptr, reg_prev)

        # Se marca como eliminado: puntero y lugar a -1.
        reg.sig = -1
        reg.lugar = -1
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
            print(f"ID: {reg.id}, Producto: {reg.nombre}, Cant: {reg.cantidad}, "
                  f"Precio: {reg.precio}, Fecha: {reg.fecha}, Sig: {reg.sig}, "
                  f"Lugar: {'datos' if reg.lugar == 1 else 'aux'}")
            ptr = reg.sig
            lugar = reg.lugar




archivo = ArchivoSecuencial()


def cargar_desde_csv(archivo_secuencial, archivo_csv='Data_test/sales_random.csv'):
    try:
        with open(archivo_csv, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)     
            for row in reader:
                if len(row) == 5:
                    try:
                        nuevo_registro = Registro(
                            id_venta=int(row[0]),
                            nombre=row[1],
                            cantidad=int(row[2]),
                            precio=float(row[3]),
                            fecha=row[4]
                        )
                        archivo_secuencial.insertar(nuevo_registro)
                        print(f"✅ Insertado ID {row[0]}")
                    except ValueError as e:
                        print(f"❌ Error en fila {row}: {e}")
                else:
                    print(f"❌ Fila omitida (format incorrecto): {row}")
                    
        print("\n🎉 Carga completada!")
    except Exception as e:
        print(f"❌ Error al cargar CSV: {e}")

def menu_principal():
    archivo = ArchivoSecuencial()
    
    while True:
        print("\n" + "="*50)
        print(" MENÚ PRINCIPAL - GESTIÓN DE VENTAS ".center(50))
        print("="*50)
        print("1. Cargar todos los registros desde sales_dataset.csv")
        print("2. Insertar un registro manualmente")
        print("3. Buscar un registro por ID")
        print("4. Eliminar un registro (lógicamente)")
        print("5. Mostrar todos los registros")
        print("6. Busqueda por rango")
        print("7. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            confirmacion = input("¿Está seguro de cargar TODOS los registros? (s/n): ")
            if confirmacion.lower() == 's':
                cargar_desde_csv(archivo)
            else:
                print("Operación cancelada")
                
        elif opcion == "2":
            try:
                print("\nIngrese los datos del record registro:")
                id_venta = int(input("ID de venta: "))
                nombre = input("Nombre del producto: ")
                cantidad = int(input("Cantidad: "))
                precio = float(input("Precio unitario: "))
                fecha = input("Fecha (YYYY-MM-DD): ")
                
                nuevo_registro = Registro(id_venta, nombre, cantidad, precio, fecha)
                archivo.insertar(nuevo_registro)
                print("✅ Registro insertado correctamente")
            except ValueError:
                print("❌ Error: Ingrese valores válidos para los campos numéricos")
                
        elif opcion == "3":
            try:
                id_busqueda = int(input("Ingrese el ID a buscar: "))
                resultado = archivo.buscar(id_busqueda)
                if resultado:
                    _, _, _, _, reg = resultado
                    print("\nRegistro encontrado:")
                    print(f"ID: {reg.id}")
                    print(f"Producto: {reg.nombre}")
                    print(f"Cantidad: {reg.cantidad}")
                    print(f"Precio: {reg.precio}")
                    print(f"Fecha: {reg.fecha}")
                else:
                    print("❌ Registro no encontrado")
            except ValueError:
                print("❌ Error: Ingrese un ID válido (número entero)")
                
        elif opcion == "4":
            try:
                id_eliminar = int(input("Ingrese el ID a eliminar: "))
                archivo.eliminar(id_eliminar)
            except ValueError:
                print("❌ Error: Ingrese un ID válido (número entero)")
                
        elif opcion == "5":
            archivo.mostrar()
            
        elif opcion == "6":
            Limite_inferior = int(input("Ingrese el límite inferior: "))
            Limite_superior = int(input("Ingrese el límite superior: "))
            try:
                resultado = archivo.buscar_rango(Limite_inferior, Limite_superior)
                if resultado:
                    print("\nRegistros encontrados en el rango:")
                    for reg in resultado:
                        print(f"ID: {reg.id}, Producto: {reg.nombre}, Cantidad: {reg.cantidad}, "
                              f"Precio: {reg.precio}, Fecha: {reg.fecha}")
                else:
                    print("❌ No se encontraron registros en el rango especificado")
            except ValueError:
                print("❌ Error: Ingrese un rango válido (números enteros)")

                
        elif opcion == "7":
            print("Saliendo del sistema...")
            break
            
        else:
            print("❌ Opción no válida. Intente nuevamente.")


if __name__ == "__main__":

    if os.path.exists('Secuencial_Struct/datos.bin'):
        os.remove('Secuencial_Struct/datos.bin')
    if os.path.exists('Secuencial_Struct/aux.bin'):
        os.remove('Secuencial_Struct/aux.bin')
    menu_principal()