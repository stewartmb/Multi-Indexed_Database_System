
## Clase Registro Universal
Para el manejo correcto de los registros en la base de datos, se optó por tener una clase registro "universal". En otras palabras, una clase que funciona con cualquier tipo de registro (Ya sea INT, FLOAT, BOOL, etc). La clase proporciona funcionalidades para manejar registros binarios, permitiendo la conversión entre listas de Python y bytes según un formato definido. 

### Atributos de la clase
- dict_format (dict): Diccionario que define los nombres y tipos de los campos del registro
- FORMAT (str): Cadena de formato para struct, generada a partir de dict_format
- size (int): Tamaño en bytes del registro
- key (str): Nombre del campo que actúa como clave única
- key_index (int): Índice del campo clave en el registro

### Métodos Principales

### __init__(dict_format: dict, key_name: str = None, key_index: int = None)
Constructor que inicializa el registro con un formato específico.

*Parámetros*:
- dict_format: Diccionario con nombres de campo y tipos (ej: {'id': 'i', 'nombre': '20s'})
- key_name: Nombre del campo que será clave (opcional)
- key_index: Índice del campo clave (opcional, se usa si no hay key_name)

*Excepciones*:
- ValueError: Si no se provee clave o no existe el nombre
- IndexError: Si el índice está fuera de rango

### to_bytes(register: list) -> bytes
Convierte una lista de Python a bytes según el formato.

*Parámetros*:
- register: Lista con valores en orden del dict_format

*Retorna*: Bytes empaquetados

### from_bytes(data: bytes) -> list
Convierte bytes a una lista de Python.

*Parámetros*:
- data: Bytes a desempaquetar

*Retorna*: Lista con valores convertidos

### get_key(lista: list) -> any
Obtiene el valor clave de un registro.

*Parámetros*:
- lista: Registro como lista

*Retorna*: Valor del campo clave

### Métodos Auxiliares
- _decode_value(value, type): Convierte un valor según su tipo
- _print(register: list): Imprime el registro de forma legible
- correct_format(register: list): Asegura que los valores tengan el tipo correcto
