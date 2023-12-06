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

def graficar_escalabilidad(escalabilidad, nombre, num_robots):
    plt.bar(num_robots, escalabilidad, label=nombre)

"""CODIGO DE PROCESAMIENTO DE DATOS"""
# Cargar el archivo CSV con los datos de la simulación
df = pd.read_csv('Experimentos/datos.csv')
# Variables para almacenar datos
# Crear un DataFrame para almacenar el promedio de escalabilidad
promedio_escalabilidad_data = []


# Ordenar los datos por el número de ID mision 
#df.sort_values(by=['MisionID'], inplace=True)

# Extraer datos por tipo de arena y tamaño
grupos_arena = df.groupby(['Arenatype', 'Arenatam','MisionID'])

# Crear variables para cada combinación de tipo de arena y tamaño
arena_datos = {}
for nombre, grupo in grupos_arena:
    arena_datos[nombre] = grupo
    print(arena_datos[nombre])

# Calcular la escalabilidad para cada combinación de tipo de arena y tamaño 
escalabilidad_arena = {}
num_robots_arena = {}
for nombre, datos in grupos_arena:
    # Calcular la escalabilidad
    escalabilidad = calcular_escalabilidad(datos)

    # Agregar la columna 'Scalability' a los datos originales
    datos['Scalability'] = escalabilidad

    # Almacenar los resultados
    escalabilidad_arena[nombre] = escalabilidad
    num_robots_arena[nombre] = datos['NumRobots'].tolist()

    # Calcular el promedio de escalabilidad y agregar a la lista
    promedio_escalabilidad = sum(escalabilidad) / len(escalabilidad)
    promedio_escalabilidad_data.append({
        'MisionID': nombre[2],  # Acceder directamente al MisionID desde la tupla
        'Arenatype': nombre[0],
        'Arenatam': nombre[1],
        'PromedioEscalabilidad': promedio_escalabilidad
    })



# Mostrar los resultados
for nombre, escalabilidad in escalabilidad_arena.items():
    mision_id = datos['MisionID'].iloc[0]  # Obtener el valor de MisionID
    # Obtener índices para actualizar
    indices = df.index[(df['Arenatype'] == nombre[0]) & (df['Arenatam'] == nombre[1]) & (df['MisionID'] == nombre[2])]
    
    # Actualizar los valores de escalabilidad para escribiliros en el fram original
    df.loc[indices, 'Scalability'] = escalabilidad
    #Imprimiri valores de escalabilidad realacionados por misión y el numero de robots
    #print(f"\nDatos originales para Mision ID {mision_id}, Arena {nombre}:")
    #print(datos[['Experimento', 'MisionID', 'Arenatype', 'Arenatam', 'NumRobots', 'Time', 'Performance', 'Scalability']])

    ## Graficar los resultados como diagramas de barras independientes
    num_robots = num_robots_arena[nombre]
    graficar_escalabilidad(escalabilidad, nombre, num_robots)
    plt.grid(True)
    plt.legend()
    plt.xlabel('Número de Robots')
    plt.ylabel('Escalabilidad')
    plt.title(f'Escalabilidad vs Número de Robots - MisionID: {mision_id} - Arena:{nombre}')
    plt.show()

##print(df[['Experimento', 'MisionID', 'Arenatype', 'Arenatam', 'NumRobots', 'Time', 'Performance', 'Scalability']])
#promedio_escalabilidad_df = pd.DataFrame(promedio_escalabilidad_data)
#print(promedio_escalabilidad_df)
#
## Gráfica de barras
#tipos_arena = promedio_escalabilidad_df['Arenatype'].unique()
## Asignar colores específicos a cada tamaño de arena
#colores_tam = {'pequena': 'blue', 'mediana': 'green', 'grande': 'orange'}
#
#fig, ax = plt.subplots()
#
#bar_width = 0.2  # Ancho de las barras
#bar_space = 0.1  # Espacio entre barras del mismo grupo
#group_space = 0.3  # Espacio entre grupos de barras
#
## Calcular la cantidad total de tamaños de arena y el ancho total que ocuparán
#num_tam_arena = len(promedio_escalabilidad_df['Arenatam'].unique())
#total_group_width = num_tam_arena * (bar_width + bar_space)
#total_width = len(promedio_escalabilidad_df['Arenatype'].unique()) * total_group_width
#
#for i, tipo in enumerate(promedio_escalabilidad_df['Arenatype'].unique()):
#    for j, tam in enumerate(promedio_escalabilidad_df['Arenatam'].unique()):
#        subset = promedio_escalabilidad_df[(promedio_escalabilidad_df['Arenatype'] == tipo) & (promedio_escalabilidad_df['Arenatam'] == tam)]
#        promedio = subset['PromedioEscalabilidad'].iloc[0]
#        group_offset = i * total_group_width
#        bar_offset = group_offset + j * (bar_width + bar_space)
#        ax.bar(bar_offset, promedio, width=bar_width, label=f'{tam}' if i == 0 else "", color=colores_tam[tam])
#        ax.text(bar_offset + bar_width / 2, promedio + 0.05, f'{promedio:.2f}', ha='center', va='bottom')
#
## Configuración de los ejes y la leyenda
#ax.set_xticks(np.arange(len(promedio_escalabilidad_df['Arenatype'].unique())) * total_group_width + total_group_width / 2)
#ax.set_xticklabels(promedio_escalabilidad_df['Arenatype'].unique())
#ax.legend(title='Tamaño de Arena')
#ax.set_xlabel('Tipo de Arena')
#ax.set_ylabel('Promedio de Escalabilidad')
#ax.set_title(f'Escalabilidad Mision ID {promedio_escalabilidad_df["MisionID"].unique()[0]}')
## Activar la grilla
#ax.grid(True, linestyle='--', alpha=0.7)
#
#plt.show()

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

