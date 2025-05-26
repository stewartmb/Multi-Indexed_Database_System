import csv
import random
from datetime import datetime, timedelta


def generate_email(name):
    """Genera un email simple basado en el nombre"""
    name_part = name.lower().replace(' ', '.')[:20]
    return f"{name_part}@example.com"

def generate_random_data(output_file, num_records , start_date):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = [
            'timestamp',
            'random_int',
            'name',
            'email',
            'date',
            'price',
            'latitude',
            'longitude',
            'is_active',
            'category'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        print(f"Generando {num_records} registros en {output_file}...")
        
        for i in range(num_records):
            name = f"User_{random.randint(1, 10000)}"
            email = generate_email(name)
            date = (start_date + timedelta(days=random.randint(0, 1095))).date()  # 3 años de rango
            
            record = {
                'timestamp': (start_date + timedelta(minutes=i)).isoformat(),
                'random_int': random.randint(1, 100000),
                'name': name,
                'email': email,
                'date': date.isoformat(),
                'price': round(random.uniform(1.0, 10000.0), 2),
                'latitude': round(random.uniform(-90, 90), 6),
                'longitude': round(random.uniform(-180, 180), 6),
                'is_active': random.choice([1, 0]),
                'category': random.choice(['Peru', 'Chile', 'Argentina', 'Brasil', 'Colombia', 'Mexico', 'Ecuador', 'Bolivia', 'Uruguay', 'Paraguay', 'Venezuela', 'Cuba', 'Puerto Rico', 'Honduras', 'Nicaragua', 'Costa Rica', 'Panama', 'El Salvador', 'Guatemala', 'Dominican Republic', 'Jamaica', 'Trinidad',' Tobago','Estados Unidos', 'Canada', 'Belgium', 'Francia', 'Alemania', 'Italia', 'España', 'Portugal', 'Reino Unido', 'Suiza', 'Suecia', 'Noruega', 'Dinamarca', 'Finlandia', 'Polonia', 'Rusia', 'Ucrania', 'Grecia', 'Turquía', 'África del Sur', 'Egipto', 'Nigeria', 'Kenya'])
            }
            
            writer.writerow(record)
            
            # Mostrar progreso cada 100,000 registros
            if (i + 1) % 10000 == 0:
                print(f"Registros generados: {i + 1}")

    print(f"\nArchivo CSV generado exitosamente: {output_file}")
# Código para generar un archivo CSV con datos aleatorios`


# Configuración
NUM_RECORDS = [10000, 50000, 100000]
START_DATE = datetime(2020, 1, 1)

for num in NUM_RECORDS:
    output_file = f'Data_test/test_data_full{num}.csv'
    generate_random_data(output_file, num, START_DATE)
    print(f"Archivo {output_file} generado con {num} registros.")