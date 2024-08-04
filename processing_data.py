import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.colorbar import Colorbar
from matplotlib.gridspec import GridSpec
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
import pyfiglet
#----------------------------------------------------------------------------------------------
"""
FUNCIONES DE PROCESAMIENTO DE DATOS
EN ESTE SCRIB SE ENCUENTRA EL CÓDIGO QUE PROCESA LOS DATOS DE LS EXPERIMENTOS
POR CLASE DE SOFTWARE, TIPO DE MISIÓN Y TAMAÑO DE ARENA
SE OBTIENE GRÁFICAS DEL PERFORMANCE DE LA MISIÓN SIN FALLOS Y CON LOS MODOS DE FALLOS
GRÁFICAS PARA ESCALABILIDAD
GRÁFICAS PARA FLEXIBILIDAD
GRÁFICAS PARA ROBUSTEZ

PARA EJECUTARLO:

* time python3 processing_data.py -- te permite conocer el tiempo que tarda en ejecutarse 
* python3 processing_data.py -- solo ejecuta el código
"""
#----------------------------------------------------------------------------------------------
""" FUNCIONES DE VISUALIZACIÓN (GRÁFICAS) """
def graficar_performance(df, tam_arena, mision_id, tipo_mision, clase_soft, fallos):
    # Extraer la unidades de medida del performance según la misión
    u_medida = " "
    if mision_id == 1:
        u_medida = "# V/visitadas"
    elif mision_id == 2:
        u_medida = "# Robots-Agregados"
    elif mision_id == 4:
        u_medida = "Time step consenso"
    else:
        u_medida == "Min Distancia-Cm2"

    # Ajustar el tamaño de la figura
    plt.figure(figsize=(10, 10))

    # Configurar el boxplot con notch
    ax = sns.boxplot(x='NumRobots', y='Performance', data=df, notch=True, width=0.2,linecolor='black', linewidth=1.5)
    #offset = 100 if mision_id != 2 else 1
    if mision_id == 1:
        offset = 15
        # Obtener el rango de valores
        min_performance = df['Performance'].min() - offset
        max_performance = df['Performance'].max() + offset
    elif mision_id == 2:
        offset = 1
        # Obtener el rango de valores
        min_performance = df['Performance'].min() - offset
        max_performance = df['Performance'].max() + offset
    elif mision_id == 3:
        offset = 100
        # Obtener el rango de valores
        min_performance = df['Performance'].min() - offset
        max_performance = df['Performance'].max() + offset
    elif mision_id == 4:
        offset = 20
        # Obtener el rango de valores
        min_performance = df['Performance'].min() - offset
        max_performance = df['Performance'].max() + 100



    # Ajustar el rango del eje Y
    ax.set_ylim(min_performance, max_performance)

    # Titulo del plot
    titulo_plot = f'{mision_id}{clas_sof}.Rendimiento-{tipo_mision}-Arena-{tam_arena}-Fallos-{fallos}'

    # Mostrar el valor de la mediana en el gráfico
    medians = df.groupby('NumRobots')['Performance'].median()
    x_vals = range(len(medians))
    for i, value in enumerate(medians):
        ax.text(x_vals[i], value, f'{value:.2f}', ha='left', va='bottom', color='black')

    # Añadir etiquetas y título
    plt.xlabel('Número de Robots', fontsize=16)
    plt.ylabel(f'Performance ({u_medida})', fontsize=16)
    plt.title(f'Rendimiento \n Misión ({mision_id}): {tipo_mision} - Arena-Tamaño: {tam_arena} - Software: {clase_soft} - Fallos: {fallos}', pad=25, fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    # Guardar la figura
    plt.savefig(ruta+"/"+titulo_plot+".png", dpi=600, bbox_inches="tight")
    #plt.show()
    plt.close()



def graficar_metrica_escalabilidad(subset, metrica,test, tam_arena, mision_id, tipo_mision, clas_sof):
    robots = subset['NumRobots'].unique()
    m_metrica, m_binomial = np.zeros(((len(robots)-1), (len(robots)-1))), np.zeros(((len(robots)-1), (len(robots)-1)))# matrix con las medianas de los datos procesados mxn

    # Calcula la mediana del set de datos de la métrica y se almacena en la matriz
    for i, lista in enumerate(metrica): # iterar en las listas de métrica filas
        for j in range(i, m_metrica.shape[1]): # iteración por columnas de la matriz
            sublista = metrica[i][j - i]  # Obtiene la sub-lista actual
            mediana = np.median(sublista)  # Calcula la mediana
            m_metrica[i, j] = mediana  # Almacena la mediana en la matriz
            m_binomial[i,j] = test[i][j-i][0]

    m_metrica = np.flipud(m_metrica) # Función para cambiar de filas de la matriz, la fila 1 ahora es la última y así sucesivamente
    if mision_id == 3:
        m_metrica = -1.0 * m_metrica

    # Eliminar los valores por encima de la diagonal principal
    for i in range(len(robots) - 1):
        for j in range(m_metrica.shape[1] - i - 1):
            m_metrica[i, j] = np.nan

    # Configuración de la visualización
    fig, ax = plt.subplots()

    # Crear un heatmap con Seaborn
    sns.heatmap(m_metrica, annot=True, cmap='viridis', linewidths=0.5, square=True, ax=ax,
                xticklabels=robots[1:12], yticklabels=robots[0:11][::-1], cbar_kws={'orientation': 'vertical'})#, cbar_kws={'label': 'Valor de la métrica', 'orientation': 'horizontal'}

    titulo_plot = f'{mision_id}{clas_sof}.Escalabilidad-{tipo_mision}-Arena-{tam_arena}'
    # Títulos y etiquetas
    ax.set_title(f'Escalabilidad - Misión ({mision_id}): {tipo_mision} - Arena- Tamaño: {tam_arena} - Software: {clas_sof}', pad=25, fontsize=18)
    ax.set_xlabel('Tamaño del enjambre (#Robots)', fontsize=16)
    ax.set_ylabel('Tamaño del enjambre (#Robots)', fontsize=16)

    # Ajustar el tamaño de las etiquetas de los ejes
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # Ajuste de diseño
    fig.tight_layout()
    fig.set_size_inches((11, 11))
    plt.savefig(ruta+"/"+"Escalabilidad"+"/"+titulo_plot+".png", dpi=300, bbox_inches="tight")
    #plt.show()
    plt.close()

def graficar_metrica_flexibilidad(P1,P2,P3,P4,mision_id, tipo_mision, clas_sof):
    tams = ['Pequeña-Mediana','Pequeña-Grande','Mediana-Grande'] # Tamaños arenas
    grupos = ['2,10 %', '20,40 %', '50,70 %', '80,100 %'] # grupos de robots

    datos = [P1, P2, P3, P4]

    metrica = np.zeros((len(tams),len(grupos)))
    # llenar matriz de relación de la metrica con la mediana de los datos
    for i in range(len(grupos)): # iteración por columnas
        for j in range(len(tams)): # iteración por filas
            for x in range(len(tams)):
                metrica[j,i] = np.median(datos[i][j])
                break

    # Configuración de la visualización
    fig, ax = plt.subplots()

    # Crear un heatmap con Seaborn
    sns.heatmap(metrica, annot=True, cmap='coolwarm', linewidths=1, square=True, ax=ax,
                xticklabels=grupos, yticklabels=tams, cbar_kws={'label': 'Valor de la métrica'})
    titulo_plot = f'{mision_id}{clas_sof}.Flexibilidad-{tipo_mision}'
    # Títulos y etiquetas
    ax.set_title(f'Flexibilidad - Misión ({mision_id}): {tipo_mision} - Software: {clas_sof}')
    ax.set_xlabel('Densidad Robots')
    ax.set_ylabel('Tamaño Arena')

    # Ajuste de diseño
    fig.tight_layout()
    fig.set_size_inches((8, 5))
    plt.savefig(ruta+"/"+"Flexibilidad"+"/"+titulo_plot+".png", dpi=300, bbox_inches="tight")
    #plt.show()
    plt.close()
    
def graficar_metrica_robustez(subset, robustez, tam_arena, mision_id, tipo_mision, clas_sof):
    robots = subset['NumRobots'].unique()
    m_robustez = np.zeros((3, 12))  # Matriz con las medianas de los datos procesados mxn
    
    # Calcula la mediana del set de datos de la métrica y se almacena en la matriz
    for i in range(len(robustez[0])):  # Iterar en las listas de métrica por filas (3)
        for j in range(len(robustez)):  # Iteración por columnas de la matriz (12)
            mediana = np.median(robustez[j][i])  # Calcula la mediana de los datos
            m_robustez[i, j] = mediana  # Almacena el valor calculado y lo guarda en la matriz
    
    # Configuración de la visualización
    fig, ax = plt.subplots()
    
    # Crear un heatmap con Seaborn
    sns.heatmap(m_robustez, annot=True, cmap='viridis', linewidths=0.5, square=True, ax=ax,
                xticklabels=robots, yticklabels=["10%", "20%", "30%"],
                cbar_kws={'orientation': 'horizontal', 'label': 'Valor de la métrica'})
    
    titulo_plot = f'{mision_id}{clas_sof}.Robustez-{tipo_mision}-Arena-{tam_arena}'
    
    # Títulos y etiquetas
    ax.set_title(f'Robustez - Misión ({mision_id}): {tipo_mision} - Arena- Tamaño: {tam_arena} - Software: {clas_sof}', pad=25, fontsize=16)
    ax.set_xlabel('Tamaño del enjambre (#Robots)', fontsize=14)
    ax.set_ylabel('Modo de Fallo FM', fontsize=14)
    
    # Ajustar el tamaño de las etiquetas de los ejes
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    
    # Ajuste de diseño
    fig.tight_layout()
    fig.set_size_inches((8, 5))
    
    # Guardar la gráfica como archivo de imagen
    plt.savefig(ruta + "/" + "Robustez" + "/" + titulo_plot + ".png", dpi=300, bbox_inches="tight")
    plt.close()


""" FUNCIONES MANIPULACIÓN DE DATOS (CALCULO DE MÉTRICAS) """
def metrica_escalabilidad(data):
    size_robots = data['NumRobots'].unique()  # obtener la lista de tamaños del enjambre #Robots
    performance_robots = []  # lista para almacenar el performance

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
            test_bin = 0 # contador casos éxito en test binomial
            # Iteramos la matriz de datos del performance, filas corresponden a la cantidad de robots y las columnas al performance
            for j in range(len(performance_robots[i,:])-1):
                if performance_robots[i,j] != 0: # evitar la division por 0
                    deltaP = (performance_robots[k,j]-performance_robots[i,j]) / performance_robots[i,j]
                elif performance_robots[k,j] >= performance_robots[i,j]:
                    # Aunque sea 0 el anterior si el nuevo performance es mayor, el deltaP = 1 hubo mejora de rendimiento
                    deltaP = 1
                else: # el performance no fue mejor al anterior, no se cumple la condición 1, no escalable
                    deltaP = 0
                # Se calcula el delta N cambio de tamaño de robots
                deltaN = (size_robots[k]-size_robots[i]) / size_robots[i]
                f_es.append(deltaP/deltaN)
                if performance_robots[k,j] >= performance_robots[i,j]:
                    test_bin = test_bin + 1 # contabilizar casos exitosos 
                    # se cumple la condición 1 de la métrica, sistema escalable
            # Se calcula el test binomial con los datos
            test_binomial = sm.stats.proportions_ztest(test_bin,len(performance_robots[i,:]),0.5)
            test_list.append(test_binomial) # almacenamiento resultado prueba binomial
            listas.append(f_es)
        escalabilidad.append(listas) # almacenamiento calculo de la metrica
        re_test.append(test_list) # almacenamiento teste binomial 
        """Se guarda un arreglo de listas que contienen listas
        La lista final contiene 10 listas, que van en orden descendente es decir
        la pos 0  contiene 10 listas, la pos 1 contiene 9 listas ... pos 9 1 lista
        esto debido a la forma en como operamos los grupos de robots"""
    return escalabilidad ,re_test
def metrica_flexibilidad(data):
    size_robots = data['NumRobots'].unique()  # obtener la lista de tamaños del enjambre #Robots
    tam_arena = data['Arenasize'].unique() # se extraen los tamaños de la arena
    # --- calculo de los deltaX
    """
    Se toman en cuenta los perímetros del plano donde se encierra la arena
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

def metrica_robustez(data_n, data_f, modo_fallo):
    size_robots = data_n['NumRobots'].unique()  # obtener la lista de tamaños del enjambre #Robots
    per_robots = []  # lista para almacenar el performance sin fallos
    per_robots1 = []  # lista para almacenar el performance 10% fallos
    per_robots2 = []  # lista para almacenar el performance 20% fallos
    per_robots3 = []  # lista para almacenar el performance 30% fallos

    for n_robots in size_robots: # filtrar los datos por cantidad de robots
        subset = data_n[data_n['NumRobots'] == n_robots] # Sin fallos
        subset_1 =data_f.query('NumRobots == @n_robots and Faults == @modo_fallo[1]') # Con el 10% fallos
        subset_2 =data_f.query('NumRobots == @n_robots and Faults == @modo_fallo[2]') # Con el 20% fallos
        subset_3 =data_f.query('NumRobots == @n_robots and Faults == @modo_fallo[3]') # Con el 30% fallos
        # Obtener los datos del performance según la cantidad de robots actual, se almacenan de una lista
        per_robots.append(subset['Performance'].tolist())
        per_robots1.append(subset_1['Performance'].tolist())
        per_robots2.append(subset_2['Performance'].tolist())
        per_robots3.append(subset_3['Performance'].tolist())

    per_robots = np.array(per_robots) # convertimos la lista en una matriz (mxn) 12x50 filas cantidad robots, columnas performance
    per_robots1 = np.array(per_robots1)
    per_robots2 = np.array(per_robots2)
    per_robots3 = np.array(per_robots3)
    robustez = [] # lista para almacenar el calculo de la metrica
    for i in range(len(size_robots)):
        r1, r2, r3= [], [], [] # auxiliar calculo de robustez
        # Iteramos la matriz de datos del performance, filas corresponden a la cantidad de robots y las columnas al performance
        for j in range(len(per_robots[i,:])):
            # Operación con 10%, 20% y 30% 
            if per_robots[i,j] != 0: # evitar la division por 0
                deltaP1 = (per_robots1[i,j]-per_robots[i,j]) / per_robots[i,j] # calculo con 10%
                deltaP2 = (per_robots2[i,j]-per_robots[i,j]) / per_robots[i,j] # calculo con 20%
                deltaP3 = (per_robots3[i,j]-per_robots[i,j]) / per_robots[i,j] # calculo con 30%
            else:
                # Se evalúa una condición de metrica que se debe cumplir para determinar si es robusto o no el sistema
                if per_robots1[i,j] > per_robots[i,j] - 0.1*per_robots[i,j]:
                    deltaP1 = 1 # sistema robusto
                else: # el performance no fue mejor al anterior, no se cumple la condición 1, no es robusto
                    deltaP1 = 0
                # Se evalúa una condición de metrica que se debe cumplir para determinar si es robusto o no el sistema
                if per_robots2[i,j] > per_robots[i,j] - 0.2*per_robots[i,j]:
                    deltaP2 = 1 # sistema robusto
                else: # el performance no fue mejor al anterior, no se cumple la condición 1, no es robusto
                    deltaP2 = 0
                # Se evalúa una condición de metrica que se debe cumplir para determinar si es robusto o no el sistema
                if per_robots3[i,j] > per_robots[i,j] - 0.3*per_robots[i,j]:
                    deltaP3 = 1 # sistema robusto
                else: # el performance no fue mejor al anterior, no se cumple la condición 1, no es robusto
                    deltaP3 = 0
            # Se calcula el delta N teniendo en cuenta los fallos
            # Como delataN = m/N donde m es el numero de robots fallando y N el tamaño total del enjambre actual
            # Al trabajar con dos modos de fallo 20% y 30% estos valores son constantes para el calculo de cada tamaño
            deltaN1 = 0.1 # modo de fallo 1 10%
            deltaN2 = 0.2 # modo de fallo 2 20%
            deltaN3 = 0.3 # modo de fallo 3 30%
            R1,R2, R3 = deltaP1+deltaN1, deltaP2+deltaN2, deltaP3+deltaN3 # calculo de la metrica R = deltaP+deltaN
            r1.append(R1) # datos con 10%
            r2.append(R2) # Datos con 20%
            r3.append(R3) # Datos con 30%
        robustez.append([r1,r2,r3]) # almacenamiento calculo de la metrica
    """Se guarda un arreglo de listas que contienen listas"""

    return robustez
"""
EJECUCIÓN DEL PROCESAMIENTO DE DATOS
"""
# Leer el archivo CSV
df = pd.read_csv('/home/gmadro/swarm_robotics/SWARM_GENERATOR/Experimentos/datos.csv')  # Cambia la ruta según tu ubicación
f_fallo = "No"
# Obtener los IDs únicos de las misiones
mision_ids = df['MisionID'].unique()
# Obtener el tipo de software 
tipo_sof = df['Class'].unique()
# Obtener tipos de fallos
tipo_fallo = df['Faults'].unique()
""" RUTA PARA GUARDAR LOS PLOTS"""
ruta = "/home/gmadro/swarm_robotics/SWARM_GENERATOR/Plots-Experimentos"

# Iteración por la clase de software 
for clas_sof in tipo_sof:
    # Filtrar datos por clase de software y sin fallos
    #data_class = df[df['Class'] == clas_sof]
    data_class = df.query('Class == @clas_sof and Faults == @f_fallo')
    # Filtrar datos por clase software y fallos
    data_fallos = df.query('Class == @clas_sof and Faults != @f_fallo')
    # Iterar sobre cada MisionID
    for mision_id in mision_ids:
        # Filtrar los datos por MisionID
        mision_df = data_class[data_class['MisionID'] == mision_id]
        # Filtrar los datos por MisionID y Fallos
        mision_fallos = data_fallos[data_fallos['MisionID'] == mision_id]
        # Obtener las combinaciones únicas de tamaño de arena
        tamanos_arena = mision_df['Arenasize'].unique()
        tipo_mision = mision_df['Mision'].iloc[0]
        # Filtrar y graficar directamente por tamaño de arena
        for tam_arena in tamanos_arena:
            # Datos filtrados sin fallos
            subset = mision_df[mision_df['Arenasize'] == tam_arena]
            # Datos filtrados en los dos modos de fallos
            subset_f = mision_fallos[mision_fallos['Arenasize'] == tam_arena]
            """----- Graficar el boxplot de rendimiento para cada conjunto único de datos -----"""
            graficar_performance(subset, tam_arena, mision_id, tipo_mision, clas_sof, "No") # sin fallos
            graficar_performance(subset_f[subset_f['Faults'] == "Si_1"], tam_arena, mision_id, tipo_mision, clas_sof, "Si 10%") # 10% fallos
            graficar_performance(subset_f[subset_f['Faults'] == "Si_2"], tam_arena, mision_id, tipo_mision, clas_sof, "Si 20%") # 20% fallos
            graficar_performance(subset_f[subset_f['Faults'] == "Si_3"], tam_arena, mision_id, tipo_mision, clas_sof, "Si 30%") # 30% fallos
            """----- Calcular escalabilidad -----"""
            escalabilidad, esc_binomial = metrica_escalabilidad(subset)
            #escalabilidad = metrica_escalabilidad(subset)
            """----- Calcular Robustez -----"""
            robustez = metrica_robustez(subset,subset_f, tipo_fallo)
            """ /*/*/*/ Graficar resultados de las metricas /*/*/*/ """
            graficar_metrica_escalabilidad(subset, escalabilidad, esc_binomial,tam_arena, mision_id, tipo_mision, clas_sof)
            #graficar_pruebaBinomial(esc_binomial)
            graficar_metrica_robustez(subset,robustez,tam_arena,mision_id,tipo_mision,clas_sof)
        """----- Calcular Flexibilidad -----"""
        F_1, F_2, F3, F4  = metrica_flexibilidad(mision_df)
        graficar_metrica_flexibilidad(F_1, F_2, F3, F4, mision_id, tipo_mision, clas_sof)
    print(f'---- Datos procesados clase {clas_sof} ----')
print(pyfiglet.figlet_format("Todos los datos procesados",font="digital"))
