import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.colorbar import Colorbar
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
"""
FUNCIONES DE PROCESAMIENTO DE DATOS
"""

""" FUNCIONES DE VISUALIZACIÓN (GRAFICAS) """

def graficar_performance(df, tam_arena,mision_id, tipo_mision, clase_soft):
    # Extraer la unidades de medida del performance según la misión
    u_medida = " "
    if mision_id == 1:
        u_medida = "# V/visitadas"
    elif mision_id == 2:
        u_medida = "# Robots-Agregados"
    elif mision_id == 3:
        u_medida == "Min Distancia-Cm2"
    elif mision_id == 4:
        u_medida = "Time step consenso"
    # Configurar el boxplot con notch
    ax = sns.boxplot(x='NumRobots', y='Performance', data=df, notch=True, width=0.35,linecolor='black')

    # Mostrar el valor de la mediana en el gráfico
    medians = df.groupby('NumRobots')['Performance'].median()
    x_vals = range(len(medians))
    for i, value in enumerate(medians):
        ax.text(x_vals[i], value, f'{value:.2f}', ha='right', va='bottom', color='black')
    # Añadir etiquetas y título
    plt.xlabel('Número de Robots')
    plt.ylabel(f'Performance ({u_medida})')
    plt.title(f'Rendimiento - MisionID: {mision_id} {tipo_mision} - Arena-Tamaño: {tam_arena} - Software: {clase_soft}')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.show()
def graficar_pruebaBinomial(data_bin):
    fig, ax = plt.subplots()
    sns.barplot(data_bin)
def graficar_metrica_escalabilidad(subset, metrica, tam_arena, mision_id, tipo_mision, clas_sof):
    robots = subset['NumRobots'].unique()
    m_metrica = np.zeros(((len(robots)-1), (len(robots)-1))) # matrix con las medianas de los datos procesados mxn

    ## Calcula la mediana del set de datos de la métrica y se lamacena en la matriz
    for i, lista in enumerate(metrica): # iterar en las listas de metrica filas
        for j in range(i,m_metrica.shape[1]): #iteración por columnas de la matriz
            sublista = metrica[i][j - i]  # Obtiene la sublista actual
            mediana = np.median(sublista)  # Calcula la mediana
            m_metrica[i, j] = mediana  # Almacena la mediana en la matriz
    m_metrica = np.flipud(m_metrica) # Función cambio de filas de la matriz la fila 1 ahora es la ultima y así sucesivamente
    if mision_id ==3:
        m_metrica = -1.0*m_metrica
    #print(m_metrica)
    
    # Configuración de la visualización
    fig, ax = plt.subplots()

    # Crear un heatmap con Seaborn
    sns.heatmap(m_metrica, annot=True, cmap='viridis', linewidths=0.5, square=True, ax=ax,
                xticklabels=robots[1:12], yticklabels=robots[0:11][::-1], cbar_kws={'label': 'Valor de la métrica'})

    # Títulos y etiquetas
    ax.set_title(f'Escalabilidad - MisionID: {mision_id} {tipo_mision} - Arena- Tamaño: {tam_arena} - Software: {clas_sof}')
    ax.set_xlabel('Tamaño del enjambre (#Robots)')
    ax.set_ylabel('Tamaño del enjambre (#Robots)')

    # Ajuste de diseño
    fig.tight_layout()
    # Ajuste de los bordes
    #plt.subplots_adjust(left=0.0, right=0.85)
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
def graficar_metrica_flexibilidad(P1,P2,P3,P4,mision_id, tipo_mision, clas_sof):
    tams = ['Pequeña-Mediana','Pequeña-Grande','Mediana-Grande'] # Tamaños arenas
    grupos = ['2,10 %', '20,40 %', '50,70 %', '80,100 %'] # grupos de robots
     
    datos = [P1, P2, P3, P4]

    #print("------", len(datos),"\n", datos[0][0])
    #print(P1[0,:])
    #if np.median(P2[2,:]) == np.median(datos[1][2]):
    #    print("SI son iguales !!!!!!!!!")
    # Matriz de datos donde se almacenaran los datos
    metrica = np.zeros((len(tams),len(grupos)))
    # llenar matriz de relación de la metrica con la mediana de los datos
    for i in range(len(grupos)): # iteración por columnas
        for j in range(len(tams)): # iteración por filas
            for x in range(len(tams)):
                metrica[j,i] = np.median(datos[i][j])
                break
    
    #print("calculo original: ",np.median(P1[0,:]),np.median(P1[1,:]),np.median(P1[2,:]))
    #print("matriz:", "\n", metrica)

    # Configuración de la visualización
    fig, ax = plt.subplots()

    # Crear un heatmap con Seaborn
    sns.heatmap(metrica, annot=True, cmap='coolwarm', linewidths=1, square=True, ax=ax,
                xticklabels=grupos, yticklabels=tams, cbar_kws={'label': 'Valor de la métrica'})

    # Títulos y etiquetas
    ax.set_title(f'Flexibilidad - MisionID: {mision_id} {tipo_mision} - Software: {clas_sof}')
    ax.set_xlabel('Densidad Robots')
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
        listas = []
        test_list = []
        # Iteramos para comparar cada grupo de robots 2-5,2-10....90-100
        for k in range(i+1,len(size_robots)):
            f_es = [] # auxilar calculo de escalabilidad
            test_bin = 0 # contador casos exito en test binomial
            # Iteramos la matriz de datos del performance, filas corresponden a la cantidad de robots y las columnas al peroformace
            for j in range(len(performance_robots[i,:])-1):
                if performance_robots[i,j] != 0: # evitar la division por 0
                    deltaP = (performance_robots[k,j]-performance_robots[i,j]) / performance_robots[i,j]
                elif performance_robots[k,j] >= performance_robots[i,j]:
                    # Aunque sea 0 el anterior si el nuevo performnace es mayor, el deltaP = 1 hubo mejora de rendimiento
                    deltaP = 1
                else: # el performance no fue mejor al anterior, no se cumple la condición 1, no escalable
                    deltaP = 0
                # Se calcula el delta N cambio de tamaño de robots
                deltaN = (size_robots[k]-size_robots[i]) / size_robots[i]
                f_es.append(deltaP/deltaN)
                if performance_robots[k,j] >= performance_robots[i,j]:
                    test_bin = test_bin + 1 # contabilizar casos exitosos 
                    # se cumple la condición 1 de la maetrica, sistema escalable
            # Se calcula el test binomial con los datos
            test_binomial = sm.stats.proportions_ztest(test_bin,len(performance_robots[i,:]),0.5)
            test_list.append(test_binomial) # alamacenamiento resultado prueba binomial
            listas.append(f_es)
        escalabilidad.append(listas) # alamcenamiento calculo de la metrica
        re_test.append(test_list) # almacenamiento teste binomial 
        """Se gurada un arreglo de listas que contienen listas
        La lista final contiene 10 listas, que van en orden descendente es decir
        la pos 0  contiene 10 listas, la pos 1 contiene 9 listas ... pos 9 1 lista
        esto debido a la forma en como operamos los grupos de robots"""
    print(re_test)
    return escalabilidad #,re_test
def metrica_flexibilidad(data):
    size_robots = data['NumRobots'].unique()  # obtener la lista de tamaños del enjambre #Robots
    tam_arena = data['Arenasize'].unique() # se extraen los tamaños de la arena
    # --- calculo de los deltX
    """
    Se toman en cuenta los perimetros del plano donde se encierra la arena
    según su tamaño, entonces:
    pequeña = 20 m - mediana = 32 m - grande =  48 m
    """
    deltaX1 = abs((32-20)/20) #Relación pequeña mediana
    deltaX2 = abs((48-20)/20) #Relación pequeña grande
    deltaX3 = abs((48-32)/32) #Relación mediana grande

    """Extraemos los datos respecto a un numero especifico de robots
    G1: 2-10, G2: 20-40, G3: 50-70, G4: 80-100
    """
    _2, _10, _20, _40, _50, _70, _80, _100 = data[data['NumRobots']==2],data[data['NumRobots']==10],data[data['NumRobots']==20],data[data['NumRobots']==40],data[data['NumRobots']==50], data[data['NumRobots']==70], data[data['NumRobots']==80], data[data['NumRobots']==100]

    Per2, Per10, Per20, Per40 = _2['Performance'].tolist(), _10['Performance'].tolist(), _20['Performance'].tolist(), _40['Performance'].tolist()
    Per50, Per70, Per80, Per100 = _50['Performance'].tolist(), _70['Performance'].tolist(), _80['Performance'].tolist(), _100['Performance'].tolist()
    G1, G2, G3, G4 = np.zeros((3,len(Per2))), np.zeros((3,len(Per2))), np.zeros((3,len(Per2))), np.zeros((3,len(Per2)))

    for i in range(len(Per2)):
        if Per2[i] != 0: # Calculo para el G1 2-10 en los tres tamaños
            d_G1P1 = (Per10[i]-Per2[i]) / Per2[i]
        elif Per10[i] > Per2[i]:
            d_G1P1 = 1
        else:
            d_G1P1 = 0
        
        if Per20[i] != 0: # Calculo para el G2 20-40 en los tres tamaños
            d_G2P1 = (Per40[i]-Per20[i]) / Per20[i]
        elif Per40[i] > Per20[i]:
            d_G2P1 = 1
        else:
            d_G2P1 = 0
        
        if Per50[i] != 0: # Calculo para el G3 50-70 en los tres tamaños
            d_G3P1 = (Per70[i]-Per50[i]) / Per50[i]
        elif Per70[i] > Per40[i]:
            d_G3P1 = 1
        else:
            d_G3P1 = 0

        if Per80[i] != 0: # Calculo para el G4 80-100 en los tres tamaños
            d_G4P1 = (Per100[i]-Per80[i]) / Per80[i]
        elif Per100[i] > Per80[i]:
            d_G4P1 = 1
        else:
            d_G4P1 = 0
        
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

    #return fle_PM, fle_PG, fle_MG
    return G1, G2, G3, G4 

"""
EJECUCIÓN DEL PROCESAMIENTO DE DATOS
"""
# Leer el archivo CSV
df = pd.read_csv('/home/gmadro/swarm_robotics/SWARM_GENERATOR/Experimentos/datos.csv')  # Cambia la ruta según tu ubicación

# Obtener los IDs únicos de las misiones
mision_ids = df['MisionID'].unique()
# Obtener el tipo de software 
tipo_sof = df['Class'].unique()
# Iteración por la clase de software 
for clas_sof in tipo_sof:
    # Filtrar datos por clase de software
    data_class = df[df['Class'] == clas_sof]
    # Iterar sobre cada MisionID
    for mision_id in mision_ids:
        # Filtrar los datos por MisionID
        mision_df = data_class[data_class['MisionID'] == mision_id]

        # Obtener las combinaciones únicas de tamaño de arena
        tamanos_arena = mision_df['Arenasize'].unique()
        tipo_mision = mision_df['Mision'].iloc[0]

        # Filtrar y graficar directamente por tamaño de arena
        for tam_arena in tamanos_arena:
            subset = mision_df[mision_df['Arenasize'] == tam_arena]

            """Graficar el boxplot de rendimiento para cada conjunto único de datos"""
            graficar_performance(subset, tam_arena, mision_id, tipo_mision, clas_sof)
            """Calcular escalabilidad"""
            #escalabilidad, esc_binomial = metrica_escalabilidad(subset)
            escalabilidad = metrica_escalabilidad(subset)
            """Graficar resultados de las metricas"""
            graficar_metrica_escalabilidad(subset, escalabilidad, tam_arena, mision_id, tipo_mision, clas_sof)
            #graficar_pruebaBinomial(esc_binomial)
        #flex_PM, flex_PG, flex_MG = metrica_flexibilidad(mision_df)
        F_1, F_2, F3, F4  = metrica_flexibilidad(mision_df)
        #graficar_metrica_flexibilidad(flex_PM,flex_PG,flex_MG,mision_id, tipo_mision)
        graficar_metrica_flexibilidad(F_1, F_2, F3, F4, mision_id, tipo_mision, clas_sof)