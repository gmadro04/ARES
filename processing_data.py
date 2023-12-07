import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns  # Importar seaborn para facilitar la asignación de colores
import numpy as np

"""
PROCESAMIENTO DE LOS DATOS DE LOS EXPERIMENTOS
"""

def calcular_flexibilidad(arena):
    flexibilidad = []
    deltaP = 0
    deltaX = 0
    for i in range(len(arena)-1):
        deltaP = (arena['Performance'].iloc[i+1] - arena['Performance'].iloc[i]) / arena['Performance'].iloc[i]
        deltaX = 0.1
        M_F = (deltaP / deltaX) +1 
        flexibilidad.append(M_F)

def calcular_escalabilidad(arena):
    escalabilidad = []
    deltaP = 0
    deltaN = 0
    escalabilidad.append(0)

    for i in range(len(arena)-1):
        if arena['Performance'].iloc[i] != 0:
            deltaP = (arena['Performance'].iloc[i+1] - arena['Performance'].iloc[i]) / arena['Performance'].iloc[i]
        else:
            # Si el denominador es cero, asignar un valor adecuado (por ejemplo, NaN)
            deltaP = 0
        #deltaP = (arena['Performance'].iloc[i+1] - arena['Performance'].iloc[i]) / arena['Performance'].iloc[i]
        deltaN = (arena['NumRobots'].iloc[i+1] - arena['NumRobots'].iloc[i]) / arena['NumRobots'].iloc[i]
        M_S = deltaP / deltaN
        escalabilidad.append(M_S)

    return escalabilidad

# Función para graficar la escalabilidad
def graficar_escalabilidad(escalabilidad, num_robots, nombre, mision_id):
    plt.bar(num_robots, escalabilidad, label=f'Mision ID {mision_id} - Arena {nombre}')

# Leer el archivo CSV
df = pd.read_csv('Experimentos/datos.csv')

# Obtener los IDs únicos de las misiones
mision_ids = df['MisionID'].unique()

# Iterar sobre cada MisionID
for mision_id in mision_ids:
    # Filtrar los datos por MisionID
    mision_df = df[df['MisionID'] == mision_id]

    # Obtener las combinaciones únicas de tipo de arena y tamaño
    combinaciones_arena = mision_df[['Arenatype', 'Arenatam']].drop_duplicates()

    # Graficar la escalabilidad para cada combinación de tipo de arena y tamaño
    for index, row in combinaciones_arena.iterrows():
        tipo_arena = row['Arenatype']
        tam_arena = row['Arenatam']
        subset = mision_df[(mision_df['Arenatype'] == tipo_arena) & (mision_df['Arenatam'] == tam_arena)]

        escalabilidad = calcular_escalabilidad(subset)
        num_robots = subset['NumRobots'].tolist()

        graficar_escalabilidad(escalabilidad, num_robots, f'{tipo_arena} - {tam_arena}', mision_id)

# Configuración de la leyenda y etiquetas
plt.legend()
plt.xlabel('Número de Robots')
plt.ylabel('Escalabilidad')
plt.title('Escalabilidad vs Número de Robots para cada MisionID y Arena')
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()