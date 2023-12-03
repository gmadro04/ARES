import pandas as pd 
import matplotlib.pyplot as plt
"""
PROCESAMIENTO DE LOS DATOS DE LOS EXPERIMENTOS
"""

import pandas as pd 
import matplotlib.pyplot as plt

def calcular_escalabilidad(arena):
    escalabilidad = []
    deltaP = 0
    deltaN = 0
    escalabilidad.append(0)

    for i in range(len(arena)-1):
        deltaP = (arena['Performance'].iloc[i+1] - arena['Performance'].iloc[i]) / arena['Performance'].iloc[i]
        deltaN = (arena['NumRobots'].iloc[i+1] - arena['NumRobots'].iloc[i]) / arena['NumRobots'].iloc[i]
        M_S = deltaP / deltaN
        escalabilidad.append(M_S)

    return escalabilidad

def graficar_escalabilidad(escalabilidad, nombre, num_robots):
    plt.bar(num_robots, escalabilidad, label=nombre)

# Cargar el archivo CSV con los datos de la simulación
df = pd.read_csv('Experimentos/datos.csv')

# Ordenar los datos por el número de robots
#df.sort_values(by=['NumRobots'], inplace=True)

# Extraer datos por tipo de arena y tamaño
grupos_arena = df.groupby(['Arenatype', 'Arenatam','MisionID'])

# Crear variables para cada combinación de tipo de arena y tamaño
arena_datos = {}
for nombre, grupo in grupos_arena:
    arena_datos[nombre] = grupo
    #print(arena_datos[nombre])

# Calcular la escalabilidad para cada combinación de tipo de arena y tamaño
escalabilidad_arena = {}
num_robots_arena = {}
for nombre, datos in grupos_arena:
    escalabilidad_arena[nombre] = calcular_escalabilidad(datos)
    num_robots_arena[nombre] = datos['NumRobots'].tolist()

# Mostrar los resultados
for nombre, escalabilidad in escalabilidad_arena.items():
    mision_id = datos['MisionID'].iloc[0]  # Obtener el valor de MisionID

    #print(f"Escalabilidad mision ID {mision_id} Arena {nombre}:")
    #print(escalabilidad)

    ## Graficar los resultados como diagramas de barras independientes
    num_robots = num_robots_arena[nombre]
    graficar_escalabilidad(escalabilidad, nombre, num_robots)
    plt.grid(True)
    plt.legend()
    plt.xlabel('Número de Robots')
    plt.ylabel('Escalabilidad')
    plt.title(f'Escalabilidad vs Número de Robots - MisionID: {mision_id} - Arena:{nombre}')
    plt.show()
#
## Extraer datos por tipo de arena 
#arena_triangular = df[df['Arenatype'] == 'Triangular']
#arena_cuadrada = df[df['Arenatype'] == 'Cuadrada']
#
#arena_triangular_pequeña = arena_triangular[arena_triangular['Arenatam']=='pequena']
#arena_triangular_mediana = arena_triangular[arena_triangular['Arenatam']=='mediana']
#
## Iterar sobre experimentos y calcular la escalabilidad
#escalabilidad = []
#deltaP = 0
#deltaN = 0
#escalabilidad.append(0)
#for i in range(len(df)-1):
#    deltaP = (df['Performance'][i+1] - df['Performance'][i]) / df['Performance'][i]
#    deltaN = (df['NumRobots'][i+1] - df['NumRobots'][i]) / df['NumRobots'][i]
#    M_S = deltaP/deltaN
#    escalabilidad.append(M_S)
#
## Agregar la lista de escalabilidad al DataFrame
#df['Scalability'] = escalabilidad
#
## Imprimir o mostrar los resultados
#print(df[['Experimento', 'MisionID', 'Arenatype', 'Arenatam', 'NumRobots', 'Time', 'Performance', 'Scalability']])

