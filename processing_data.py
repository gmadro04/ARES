import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # Importar seaborn para facilitar la asignación de colores
import numpy as np

"""
PROCESAMIENTO DE LOS DATOS DE LOS EXPERIMENTOS
"""
def plot_metrica_promedio(mision_df, metrica, bar_width=0.25, bar_space=0.01):
    tipos_arena = mision_df['Arenatype'].unique()
    colores_tam = {'pequena': 'blue', 'mediana': 'green', 'grande': 'orange'}
    x = np.arange(len(tipos_arena))

    for i, tam in enumerate(mision_df['Arenatam'].unique()):
        metrica_valores = []

        for tipo in tipos_arena:
            subset = mision_df[(mision_df['Arenatype'] == tipo) & (mision_df['Arenatam'] == tam)]
            promedio_metrica = subset[f'Promedio{metrica}'].iloc[0]
            metrica_valores.append(promedio_metrica)

        plt.bar(x + i * (bar_width + bar_space), metrica_valores, width=bar_width, label=f'{tam}', color=colores_tam[tam])

    plt.xlabel('Tipo de Arena')
    plt.ylabel(f'Promedio de {metrica}')
    plt.title(f'Promedio de {metrica} - Mision ID: {mision_id}')
    plt.xticks(x + (bar_width + bar_space) * (len(mision_df['Arenatam'].unique()) - 1) / 2, tipos_arena)
    plt.legend(title='Tamaño de Arena')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()

def calcular_flexibilidad(arena):
    flexibilidad = [0]
    deltaP = 0
    deltaX = 0
    for i in range(len(arena)-1):
        if arena['Performance'].iloc[i] != 0:
            deltaP = (arena['Performance'].iloc[i+1] - arena['Performance'].iloc[0]) / arena['Performance'].iloc[0]
        else:
            deltaP = 0
        deltaX = (arena['NumRobots'].iloc[i+1] - arena['NumRobots'].iloc[0]) / arena['NumRobots'].iloc[0]
        M_F = (deltaP / deltaX) +1 
        flexibilidad.append(M_F)
    return flexibilidad

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
# Función para graficar propiedades
def graficar_propiedades(data_metrica, num_robots, nombre, mision_id, name_metrica,color):
    plt.bar(num_robots, data_metrica, width=2,label=f'Mision ID {mision_id} - Arena {nombre}', color = color)
    plt.xlabel('Número de Robots')
    plt.ylabel(f'{name_metrica}')
    plt.title(f'{name_metrica} resultados - MisionID: {mision_id} - Arena: {nombre}')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()

# Leer el archivo CSV
df = pd.read_csv('Experimentos/datos.csv')
# Crear un DataFrame para almacenar el promedio de las metricas
metricas_promedio_data = []

# Obtener los IDs únicos de las misiones
mision_ids = df['MisionID'].unique()

# Agregar la columna 'Scalability' 'Flexibility' al DataFrame original
df['Scalability'] = np.nan
df['Flexibility'] = np.nan

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
            #print(subset)
            escalabilidad = calcular_escalabilidad(subset)
            flexibilidad = calcular_flexibilidad(subset)
            num_robots = subset['NumRobots'].tolist()

            # Almacenar valores de escalabilidad en la columna 'Scalability'
            indices = df.index[(df['Arenatype'] == tipo_arena) & (df['Arenatam'] == tam_arena) & (df['MisionID'] == mision_id)]
            df.loc[indices, 'Scalability'] = escalabilidad
            df.loc[indices, 'Flexibility'] = flexibilidad

            # Calcular el promedio de escalabilidad,flexibilidad y almacenar en el DataFrame de métricas promedio
            promedio_escalabilidad = np.nanmean(escalabilidad)  # Calcular el promedio ignorando NaN
            promedio_flexibilidad = np.nanmean(flexibilidad)
            metricas_promedio_data.append({
                'MisionID': mision_id,
                'Arenatype': tipo_arena,
                'Arenatam': tam_arena,
                'PromedioEscalabilidad': promedio_escalabilidad,
                'PromedioFlexibilidad': promedio_flexibilidad
            })
            # Graficar las metricas (Sin promedios, data original)
            #graficar_escalabilidad(escalabilidad, num_robots, f'{tipo_arena} - {tam_arena}', mision_id)
            graficar_propiedades(escalabilidad, num_robots, f'{tipo_arena} - {tam_arena}', mision_id,'Escalabilidad', 'blue')
            graficar_propiedades(flexibilidad, num_robots, f'{tipo_arena} - {tam_arena}', mision_id,'Flexibilidad', 'green')
# Crear el DataFrame de métricas promedio
metricas_promedio_df = pd.DataFrame(metricas_promedio_data)

# Mostrar los resultados
print(df[['Experimento', 'MisionID', 'Arenatype', 'Arenatam', 'NumRobots', 'Time', 'Performance', 'Scalability','Flexibility']])
print(metricas_promedio_df)

# Obtener IDs únicos de las misiones
mision_ids = metricas_promedio_df['MisionID'].unique()

# Iterar sobre cada MisionID
for mision_id in mision_ids:
    # Filtrar datos por MisionID
    mision_df = metricas_promedio_df[metricas_promedio_df['MisionID'] == mision_id]
    # Llamar a la función para graficar escalabilidad
    #plot_metrica_promedio(mision_df, 'Escalabilidad')
    # Llamar a la función para graficar flexibilidad
    #plot_metrica_promedio(mision_df, 'Flexibilidad')
