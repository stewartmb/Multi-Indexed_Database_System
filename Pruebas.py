import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Cargar el CSV
df = pd.read_csv("csv_time_insert100000.csv")

# Filtrar solo columnas numéricas
df = df.select_dtypes(include='number')

# Calcular métricas estadísticas
maximos = df.max()
minimos = df.min()
promedios = df.mean()
desviaciones = df.std()

# Consolidar las estadísticas en un DataFrame
estadisticas_busqueda = pd.DataFrame({
    "Máximo": maximos,
    "Mínimo": minimos,
    "Promedio": promedios,
    "Desviación estándar": desviaciones
})

# Mostrar resultados
print("Estadísticas de inserción para 100k datos:")
print(estadisticas_busqueda.round(4))

# Gráfico de barras del tiempo promedio con desviación estándar
plt.figure(figsize=(12, 6))
plt.bar(estadisticas_busqueda.index, estadisticas_busqueda["Promedio"], 
        yerr=estadisticas_busqueda["Desviación estándar"], 
        capsize=5, color='skyblue', edgecolor='black')

plt.yscale('log')  # Escala logarítmica en el eje y
plt.ylabel("Tiempo promedio de inserción (ms) [escala logarítmica]")
plt.xlabel("Índice")
plt.title("Tiempo promedio de inserción por índice (100k datos)")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.grid(axis='y', which='both', linestyle='--', linewidth=0.5)

# Mostrar el gráfico
plt.show()