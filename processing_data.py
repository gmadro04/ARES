import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.colorbar import Colorbar
import numpy as np
import scipy.stats as stats
"""
FUNCIONES DE PROCESAMIENTO DE DATOS
"""

""" FUNCIONES DE VISUALIZACIÓN (GRAFICAS) """
def graficar_performance(df, tam_arena,mision_id, tipo_mision):
    # Configurar el boxplot con notch
    ax = sns.boxplot(x='NumRobots', y='Performance', data=df, notch=True, width=0.35,linecolor='black')

    # Mostrar el valor de la mediana en el gráfico
    medians = df.groupby('NumRobots')['Performance'].median()
    x_vals = range(len(medians))
    for i, value in enumerate(medians):
        ax.text(x_vals[i], value, f'{value:.2f}', ha='right', va='bottom', color='black')

    # Añadir etiquetas y título
    plt.xlabel('Número de Robots')
    plt.ylabel('Performance')
    plt.title(f'Rendimiento - MisionID: {mision_id} ({tipo_mision}) - Arena-Tamaño: {tam_arena}')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()
#sns.heatmap(m_metrica,annot=True,linewidths=0.5)
def graficar_pruebaBinomial(data_bin):
    fig, ax = plt.subplots()
    sns.barplot(data_bin)
def graficar_metrica_escalabilidad(subset, metrica, tam_arena, mision_id, tipo_mision):
    robots = subset['NumRobots'].unique()
    m_metrica = np.zeros((len(robots), len(robots)))
    if mision_id ==3:
        metrica = -1*metrica

    # Calcula la mediana del set de datos de la métrica
    medianas = np.array([np.median(sublist) for sublist in metrica])

    # Llena la matriz con los datos de la mediana en los grupos correspondientes
    for i in range(len(robots) - 1):
        m_metrica[i, i + 1] = medianas[i]

    # Configuración de la visualización
    fig, ax = plt.subplots()

    # Crear un heatmap con Seaborn
    sns.heatmap(m_metrica, annot=True, cmap='viridis', linewidths=0.5, square=True, ax=ax,
                xticklabels=robots, yticklabels=robots[0:10], cbar_kws={'label': 'Valor de la métrica'})

    # Títulos y etiquetas
    ax.set_title(f'Escalabilidad - MisionID: {mision_id} ({tipo_mision}) - Arena- Tamaño: {tam_arena}')
    ax.set_xlabel('Tamaño del enjambre (#Robots)')
    ax.set_ylabel('Tamaño del enjambre (#Robots)')

    # Ajuste de diseño
    fig.tight_layout()
    # Ajuste de los bordes
    plt.subplots_adjust(left=0.0, right=0.85)
    plt.show()
def graficar_metrica_flexibilidad1(PM,PG,MG,mision_id, tipo_mision):
    tams = ['Pequeña','Mediana','Grande'] # Tamaños arenas
    # Medianas de los datos calculados en flexibilidad
    mediana_PM = np.median(np.array(PM))
    mediana_PG = np.median(np.array(PG))
    mediana_MG = np.median(np.array(MG))
    # Matriz de datos donde se almacenaran los datos
    metrica = np.zeros((2,2))
    # llenar matriz de relación
    metrica[0,0] = mediana_PM
    metrica[0,1] = mediana_PG
    metrica[1,1] = mediana_MG

    # Configuración de la visualización
    fig, ax = plt.subplots()

    # Crear un heatmap con Seaborn
    sns.heatmap(metrica, annot=True, cmap='viridis', linewidths=1, square=True, ax=ax,
                xticklabels=tams[1:], yticklabels=tams[:2], cbar_kws={'label': 'Valor de la métrica'})

    # Títulos y etiquetas
    ax.set_title(f'Flexibilidad - MisionID: {mision_id} ({tipo_mision})')
    ax.set_xlabel('Tamaño Arena')
    ax.set_ylabel('Tamaño Arena')

    # Ajuste de diseño
    fig.tight_layout()
    plt.show()
def graficar_metrica_flexibilidad(P1,P2,P3,P4,P5,mision_id, tipo_mision):
    tams = ['Pequeña-Mediana','Pequeña-Grande','Mediana-Grande'] # Tamaños arenas
    grupos = ['5-20', '20-40', '40-60', '60-80', '80-100'] # grupos de robots
     
    datos = [P1, P2, P3, P4, P5]

    if np.median(P2[2,:]) == np.median(datos[1][2]):
        print("SI son iguales !!!!!!!!!")
    # Matriz de datos donde se almacenaran los datos
    metrica = np.zeros((len(tams),len(grupos)))
    # llenar matriz de relación de la metrica con la mediana de los datos
    for i in range(len(grupos)): # iteración por columnas
        for j in range(len(tams)): # iteración por filas
            for x in range(len(tams)):
                metrica[j,i] = np.median(datos[i][j])
                break
    
    print("calculo original: ",np.median(P1[0,:]),np.median(P1[1,:]),np.median(P1[2,:]))
    print("matriz:", "\n", metrica)

    # Configuración de la visualización
    fig, ax = plt.subplots()

    # Crear un heatmap con Seaborn
    sns.heatmap(metrica, annot=True, cmap='viridis', linewidths=1, square=True, ax=ax,
                xticklabels=grupos, yticklabels=tams, cbar_kws={'label': 'Valor de la métrica'})

    # Títulos y etiquetas
    ax.set_title(f'Flexibilidad - MisionID: {mision_id} ({tipo_mision})')
    ax.set_xlabel('Robots')
    ax.set_ylabel('Tamaño Arena')

    # Ajuste de diseño
    fig.tight_layout()
    plt.show()

""" FUNCIONES MANIPULACIÓN DE DATOS (CALCULO DE METRICAS) """
def metrica_escalabilidad(data):
    size_robots = data['NumRobots'].unique()  # obtener la lista de tamaños del enjambre #Robots
    performance_robots = []  # lista para alamecenar el performance

    for n_robots in size_robots: # filtrar los datos por cantidad de robots
        subset = data[data['NumRobots'] == n_robots]
        # Obtener los datos del performance según la cantidad de robots actual, se almacenan de una lista
        performance_robots.append(subset['Performance'].tolist())

    performance_robots = np.array(performance_robots) # convertimos la lista en una matriz (mxn)
    escalabilidad = [] # lista para almacenar el calculo de la metrica
    re_test = []
    for i in range(len(size_robots)-1):
        f_es = [] # auxilar calculo de escalabilidad
        test_bin = 0 # contador casos exito en test binomial
        # Iteramos la matriz de datos del performance, filas corresponden a la cantidad de robots y las columnas al peroformace
        for j in range(len(performance_robots[i,:])-1):
            if performance_robots[i,j] != 0: # evitar la division por 0
                deltaP = (performance_robots[i+1,j]-performance_robots[i,j]) / performance_robots[i,j]
            elif performance_robots[i+1,j] >= performance_robots[i,j]:
                # Aunque sea 0 el anterior si el nuevo performnace es mayor, el deltaP = 1 hubo mejora de rendimiento
                deltaP = 1
            else: # el performance no fue mejor al anterior, no se cumple la condición 1, no escalable
                deltaP = 0
            # Se calcula el delta N cambio de tamaño de robots
            deltaN = (size_robots[i+1]-size_robots[i]) / size_robots[i]
            f_es.append(deltaP/deltaN)

            if performance_robots[i+1,j] >= performance_robots[i,j]:
                test_bin = test_bin + 1 # contabilizar casos exitosos 
                # se cumple la condición 1 de la maetrica, sistema escalable
        # Se calcula el test binomial con los datos
        test_binomial = stats.binom_test(test_bin,len(performance_robots[i,:]),alternative='two-sided')
        re_test.append(test_binomial) # alamacenamiento resultado prueba binomial
        escalabilidad.append(f_es) # alamcenamiento calculo de la metrica

        #print("Grupo robots testeado: ", f'{size_robots[i]}-{size_robots[i+1]}',"\n", "Resultado binomial -> ", test_binomial)
    # Convertir las listas en arrays y matrices
    re_test = np.array(re_test)
    escalabilidad = np.array(escalabilidad)

    return escalabilidad,re_test
def metrica_flexibilidad(data):
    size_robots = data['NumRobots'].unique()  # obtener la lista de tamaños del enjambre #Robots
    tam_arena = data['Arenasize'].unique() # se extraen los tamaños de la arena

    # lista para alamecenar el performance
    per_small = []
    per_med = []
    per_big = []
    # --- calculo de los deltX
    """
    Se toman en cuenta los perimetros del plano donde se encierra la arena
    según su tamaño, entonces:
    pequeña = 20 m - mediana = 32 m - grande =  48 m
    """
    deltaX1 = (32-20)/20 #Relación pequeña mediana
    deltaX2 = (48-20)/20 #Relación pequeña grande
    deltaX3 = (48-32)/32 #Relación mediana grande

    # Extraer los datos por el tamaño de arena
    small = data[data['Arenasize'] == 'pequena']
    med = data[data['Arenasize'] == 'mediana']
    big = data[data['Arenasize'] == 'grande']
    for num in size_robots: # filtrar el performance por el numero de robots
        subset =  small[small['NumRobots'] == num] # datos arena pequeña
        subset1 = med[med['NumRobots'] == num] # datos arena mediana
        subset2 = big[big['NumRobots'] == num] # datos arena pequena
        per_small.append(subset['Performance'].tolist())
        per_med.append(subset1['Performance'].tolist())
        per_big.append(subset2['Performance'].tolist())
    # convertir las listas en matriz nxm
    per_small = np.array(per_small)
    per_med = np.array(per_med)
    per_big = np.array(per_med)

    # calculo de la metrica
    fle_PM, fle_PG, fle_MG = [], [], [] # Definir listas que guradan los datos
    for i in range(len(size_robots)): # iteración para comparar la flexibilidad
        for j in range(len(per_small[0,:])):
            # Se trabajan las tres relaciones PM, PG, MG en el mismo for
            if per_small[i,j] != 0: # -----Arena Pequeñan-Mediana
                deltaP1 = (per_med[i,j] - per_small[i,j]) / per_small[i,j]
            elif per_med[i,j] > per_small[i,j]:
                deltaP1 = 1 # el performance es mayor, se asigna un valor de 1
            else:
                deltaP1 = 0 # el performance no mejoró delta=0
            if per_small[i,j] != 0: # -----Arena Pequeña-Grande
                deltaP2 = (per_big[i,j] - per_small[i,j]) / per_small[i,j]
            elif per_big[i,j] > per_small[i,j]:
                deltaP2 = 1 # el performance es mayor, se asigna un valor de 1
            else:
                deltaP2 = 0 # el performance no mejoró delta=0
            if per_small[i,j] != 0: # -----Mediana-Grande
                deltaP3 = (per_big[i,j] - per_med[i,j]) / per_med[i,j]
            elif per_big[i,j] > per_med[i,j]:
                deltaP3 = 1 # el performance es mayor, se asigna un valor de 1
            else:
                deltaP3 = 0 # el performance no mejoró delta=0

            # Se proceden a llenar la lista de los datos con el calculo
            # F = (DeltaP / DeltaX) +1
            fle_PM.append((deltaP1/deltaX1)+1) # Pequeña-Mediana
            fle_PG.append((deltaP2/deltaX2)+1) # Pequeña-Grande
            fle_MG.append((deltaP3/deltaX3)+1) # Mediana-Grande
    # Retornar las listas con los calculos

    """Extraemos los datos respecto a un numero especifico de robots
    G1: 5-20, G2: 20-40, G3: 40-60, G4: 60-80, G5: 80-100
    """
    _5, _20, _40, _60, _80, _100 = data[data['NumRobots']==5],data[data['NumRobots']==20],data[data['NumRobots']==40],data[data['NumRobots']==60],data[data['NumRobots']==80], data[data['NumRobots']==100]

    Per5, Per20, Per40 = _5['Performance'].tolist(), _20['Performance'].tolist(), _40['Performance'].tolist()
    Per60, Per80, Per100 = _60['Performance'].tolist(), _80['Performance'].tolist(), _100['Performance'].tolist()
    G1, G2, G3, G4, G5= np.zeros((3,len(Per5))), np.zeros((3,len(Per5))), np.zeros((3,len(Per5))), np.zeros((3,len(Per5))), np.zeros((3,len(Per5)))

    for i in range(len(Per5)):
        if Per5[i] != 0: # Calculo para el G1 5-20 en los tres tamaños
            d_G1P1 = (Per20[i]-Per5[i]) / Per5[i]
        elif Per20[i] > Per5[i]:
            d_G1P1 = 1
        else:
            d_G1P1 = 0

        if Per20[i] != 0: # Calculo para el G2 20-40 en los tres tamaños
            d_G2P1 = (Per40[i]-Per20[i]) / Per20[i]
        elif Per40[i] > Per20[i]:
            d_G2P1 = 1
        else:
            d_G2P1 = 0

        if Per40[i] != 0: # Calculo para el G3 40-60 en los tres tamaños
            d_G3P1 = (Per60[i]-Per40[i]) / Per40[i]
        elif Per60[i] > Per40[i]:
            d_G3P1 = 1
        else:
            d_G3P1 = 0

        if Per60[i] != 0: # Calculo para el G4 60-80 en los tres tamaños
            d_G4P1 = (Per80[i]-Per60[i]) / Per60[i]
        elif Per80[i] > Per60[i]:
            d_G4P1 = 1
        else:
            d_G4P1 = 0

        if Per80[i] != 0: # Calculo para el G5 80-100 en los tres tamaños
            d_G5P1 = (Per100[i]-Per80[i]) / Per80[i]
        elif Per100[i] > Per80[i]:
            d_G5P1 = 1
        else:
            d_G5P1 = 0

        # Almacenamiento de los datos en las matrices
        G1[0,i]=(d_G1P1/deltaX1) +1
        G1[1,i] = (d_G1P1/deltaX2) +1
        G1[2,i] = (d_G1P1/deltaX3) +1

        G2[0,i]=(d_G2P1/deltaX1) +1
        G2[1,i] = (d_G2P1/deltaX2) +1
        G2[2,i] = (d_G2P1/deltaX3) +1

        G3[0,i]=(d_G3P1/deltaX1) +1
        G3[1,i] = (d_G3P1/deltaX2) +1
        G3[2,i] = (d_G3P1/deltaX3) +1

        G4[0,i]=(d_G4P1/deltaX1) +1
        G4[1,i] = (d_G4P1/deltaX2) +1
        G4[2,i] = (d_G4P1/deltaX3) +1

        G5[0,i]=(d_G5P1/deltaX1) +1
        G5[1,i] = (d_G5P1/deltaX2) +1
        G5[2,i] = (d_G5P1/deltaX3) +1

    #return fle_PM, fle_PG, fle_MG
    return G1, G2, G3, G4, G5

"""
EJECUCIÓN DEL PROCESAMIENTO DE DATOS
"""
# Leer el archivo CSV
df = pd.read_csv('/home/gmadro/swarm_robotics/SWARM_GENERATOR/Experimentos/datos.csv')  # Cambia la ruta según tu ubicación

# Obtener los IDs únicos de las misiones
mision_ids = df['MisionID'].unique()

# Iterar sobre cada MisionID
for mision_id in mision_ids:
    # Filtrar los datos por MisionID
    mision_df = df[df['MisionID'] == mision_id]

    # Obtener las combinaciones únicas de tamaño de arena
    tamanos_arena = mision_df['Arenasize'].unique()
    tipo_mision = mision_df['Mision'].iloc[0]

    # Filtrar y graficar directamente por tamaño de arena
    for tam_arena in tamanos_arena:
        subset = mision_df[mision_df['Arenasize'] == tam_arena]
        # Invertir los valores de rendimiento si es MisionID 3
        if mision_id == 3:
            subset['Performance'] = -1*subset['Performance']

        """Graficar el boxplot de rendimiento para cada conjunto único de datos"""
        graficar_performance(subset, tam_arena, mision_id, tipo_mision)
        """Calcular escalabilidad"""
        escalabilidad, esc_binomial = metrica_escalabilidad(subset)
        """Graficar resultados de las metricas"""
        graficar_metrica_escalabilidad(subset, escalabilidad, tam_arena, mision_id, tipo_mision)
        #graficar_pruebaBinomial(esc_binomial)
    #flex_PM, flex_PG, flex_MG = metrica_flexibilidad(mision_df)
    F_1, F_2, F3, F4, F5 = metrica_flexibilidad(mision_df)
    #graficar_metrica_flexibilidad(flex_PM,flex_PG,flex_MG,mision_id, tipo_mision)
    graficar_metrica_flexibilidad(F_1, F_2, F3, F4, F5, mision_id, tipo_mision)