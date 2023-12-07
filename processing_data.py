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
    plt.xlabel('Número de Robots')
    plt.ylabel('Escalabilidad')
    plt.title(f'Escalabilidad vs Número de Robots - MisionID: {mision_id} - Arena: {nombre}')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()

# Leer el archivo CSV
df = pd.read_csv('Experimentos/datos.csv')

# Obtener los IDs únicos de las misiones
mision_ids = df['MisionID'].unique()

# Agregar la columna 'Scalability' al DataFrame original
df['Scalability'] = np.nan

# Iterar sobre cada Tipo de Arena
for tipo_arena in df['Arenatype'].unique():
    # Filtrar los datos por Tipo de Arena
    tipo_arena_df = df[df['Arenatype'] == tipo_arena]

    # Iterar sobre cada MisionID
    for mision_id in mision_ids:
        # Filtrar los datos por MisionID
        mision_df = tipo_arena_df[tipo_arena_df['MisionID'] == mision_id]

        # Obtener las combinaciones únicas de tamaño de arena
        tamanos_arena = mision_df['Arenatam'].unique()

        # Calcular y almacenar la escalabilidad para cada tamaño de arena
        for tam_arena in tamanos_arena:
            subset = mision_df[mision_df['Arenatam'] == tam_arena]

            escalabilidad = calcular_escalabilidad(subset)
            num_robots = subset['NumRobots'].tolist()

            # Almacenar valores de escalabilidad en la columna 'Scalability'
            indices = df.index[(df['Arenatype'] == tipo_arena) & (df['Arenatam'] == tam_arena) & (df['MisionID'] == mision_id)]
            df.loc[indices, 'Scalability'] = escalabilidad

            # Graficar la escalabilidad
            graficar_escalabilidad(escalabilidad, num_robots, f'{tipo_arena} - {tam_arena}', mision_id)
print(df[['Experimento', 'MisionID', 'Arenatype', 'Arenatam', 'NumRobots', 'Time', 'Performance', 'Scalability']])