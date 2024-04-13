import xml.etree.ElementTree as ET
import os
import subprocess as sb
import loop_exprimentalgenerator as loop
import numpy as np
import random
import pandas as pd
import time
import pyfiglet

"""______       _____    ____  __  ___
  / ___/ |     / /   |  / __ \/  |/  /
  \__ \| | /| / / /| | / /_/ / /|_/ /
 ___/ /| |/ |/ / ___ |/ _, _/ /  / /
/____/ |__/|__/_/  |_/_/ |_/_/  /_/
   _____________   ____________  ___  __________  ____
  / ____/ ____/ | / / ____/ __ \/   |/_  __/ __ \/ __ \
 / / __/ __/ /  |/ / __/ / /_/ / /| | / / / / / / /_/ /
/ /_/ / /___/ /|  / /___/ _, _/ ___ |/ / / /_/ / _, _/
\____/_____/_/ |_/_____/_/ |_/_/  |_/_/  \____/_/ |_|


! IMPORTANTE !
LOS ÚNICOS PARÁMETROS QUE DEBES MODIFICAR MANUALMENTE SON:
--> variables "Fallos" : Especifica si deseas trabajar con fallos o no
--> variable "tipo_control" : Especifica la categoría del software de control que estas evaluando
--> Variable "misionID" : Especifica el tipo de misión que vas a evaluar, debe ser coherente con el software de control correspondiente a la misión
--> Variables "códigos" : Debes especificar el software de control a evaluar según la misión y la clase en la ruta de esta variables
---------------------------------------------------------------------------------------------------------------------------------------------------
|*| Misión a evaluar ---> Cada comportamiento colectivo (software de control) se evalúa en una misión especifica
°° Obstacle_avoid_dance -- Misión exploración
°° Aggregation -- Misión agregación
°° Pattern_Formation -- Misión formación de patrones
Misión ID ---> Toma un valor para poder evaluar la misión a ejecutar
* Misión ID = 1 -> Misión exploración
* Misión ID = 2 -> Misión agregación
* Misión ID = 3 -> Misión marcha en formación
* Misión ID = 4 -> Misión toma de decisiones colectiva

|*| Software de control -> Se dividen en dos categorías  1-> A y 2-> B
Puedes seleccionar entre uno y el otro para llevar a cabo tu experimento
---------- Comportamiento categoría A ----------
* A_obstacleAvoiddance_sta.lua
* A_aggregation_0_rb_taxis.lua
* A_pattern_formation_flocking.lua
* A_color_selection_det.lua
---------- Comportamiento categoría B ----------
* B_obstacleAvoiddance_vec.lua
* B_aggregation_spots.lua
* B_pattern_formation.lua
* B_color_selection_prob.lua
"""

""" RUTAS DE LOS DIRECTORIOS Y CONFIGURACIONES"""
# ##############################################################################################
""" ¡¡ AQUÍ SE DEBEN CONFIGURAR MANUALMENTE LOS PARÁMETROS 
CON LOS QUE SE DESEAN REALIZAR LOS EXPERIMENTOS !! """
# ----------------- CONFIGURACIÓN DE FALLOS, TIPO DE SOFTWARE DE CONTROL Y MISIÓN A EJECUTAR
# -------------------------- Puedes trabajar con el enjambre sin fallos o con fallos
# EL PORCENTAJE DE FALLOS DEL TOTAL DEL ENJAMBRE ES 10% 20% 30%
Fallos = "No" # Modifica esta variable según tu evaluación "Si, No"
tipo_control = "A" # "A-B" Especifica que categoría de comportamiento estas evaluando
# ------------------------- Misión ID
misionID = 1 # Configura el id de la misión a evaluar 1,2,3,4
if misionID == 1:
    mision = 'Exploración'
elif misionID == 2:
    mision = 'Agregación'
elif misionID == 3:
    mision = 'Marcha en Formación'
else:
    mision = 'Decisión Colectiva'
# ----------------------------------------------------------------------------------
""" CONFIGURA EL SOFTWARE DE CONTROL SEGÚN LA MISIÓN Y LA CLASE DE SOFTWARE 
    PARA LLEVAR A CABO LOS EXPERIMENTOS 
    
    ---------- Comportamiento categoría A ----------
    * A_obstacleAvoiddance_sta.lua
    * A_aggregation_0_rb_taxis.lua
    * A_pattern_formation_flocking.lua
    * A_color_selection_det.lua
    ---------- Comportamiento categoría B ----------
    * B_obstacleAvoiddance_vec.lua
    * B_aggregation_spots.lua
    * B_pattern_formation.lua
    * B_color_selection_prob.lua
    
    EJEMPLO 
    codigos = "/home/gmadro/swarm_robotics/SWARM_GENERATOR/Software-control/"AQUÍ DEBE IR EL NOMBRE DEL SOFTWARE DE CONTROL"
    
    codigos = "/home/gmadro/swarm_robotics/SWARM_GENERATOR/Software-control/softwareControl.lua
"""
# --------------------------Ruta software de control
codigos = "/home/gmadro/swarm_robotics/SWARM_GENERATOR/Software-control/A_obstacleAvoiddance_sta.lua"
# ----------------------------------------------------------------------------------
# ##############################################################################################

""" DE AQUÍ EN ADELANTE NADA POR MODIFICAR """
# ------------------------- Ruta del archivo "file".argos del experimento (XML)
dir = "/home/gmadro/swarm_robotics/SWARM_GENERATOR" # ruta del archivo a modificar
# ----------------------------------------------------------------------------------
"""LECTURA ARCHIVO DEL EXPERIMENTO"""
file = dir+"/"+"experimento.argos" # cargamos el archivo .argos
#cargamos los datos desde fichero
tree = ET.parse(file)
#cargamos el elemento raíz
root = tree.getroot()
# ----------------------------------------------------------------------------------
"""FUNCIÓN CONFIGURACIÓN PARÁMETROS EXPERIMENTO"""
def modificar_archivo(file,exp,arenas,tams,semilla):
    """ Configuración parámetros básicos """
    arena_params, parametros = loop.params_arena(arenas,tams)    # Tamaño de la arena grande,mediana,pequeña y configuración de atributos
    Obstaculos = False  # Obstáculos en el escenario si o no, según la elección tipo de distribución y tipo de obstáculo
    # Numero de robots y tiempo de duración del experimento
    #robots =  exp*(incremento_robots + num_robots_inicial) if exp >=1  else num_robots_inicial
    robots = t_robots[exp]
    time = 240 # Duración experimento en seg
    """ CONFIGURACIÓN ARCHIVO """
    loop.framework_label(file, time, codigos, Fallos, semilla) #Configuración software de control y tiempo ejecución
    # Configuración de arena
    loop.arena_configuracion(file,arena_params, params=parametros, robots=robots)
    # Configuración obstáculos en la arena
    loop.obstaculos_arena(file=file,obs=Obstaculos,pos_obs=parametros["Pos"],params=parametros)
    # configuración parámetros loop_functions
    loop.loops_params(file=file,tipo_arena=parametros["Tipo de arena"],tam_arena=parametros["Tamaño arena"],
                    exp=exp,obstaculos=Obstaculos, robots=robots, m_ID=misionID, E_fallos=Fallos, T_Control = tipo_control)
    # Parámetros simulación.
    simulacion = pd.DataFrame([parametros["Tamaño arena"],robots,str(misionID)+"-"+mision,time,Fallos, tipo_control],
                                index=["TAMAÑO:","# ROBOTS:","TIPO MISION:","T_EXPERIMENTO:","FALLOS:", "CLASE SOFTWARE"])
    print(pyfiglet.figlet_format("Arena" + parametros['Tipo de arena']))
    print(simulacion)
# ----------------------------------------------------------------------------------
"""EJECUCIÓN SWARM GENERATOR"""
# Configuración de la cantidad de ejecuciones
num_robots_inicial = 2
incremento_robots = 5
num_experimentos = 12 # Puedes cambiar esto al número deseado de ejecuciones (exp=12, robots= 2,5...100)
t_robots = [2,5,10,20,30,40,50,60,70,80,90,100] # Tamaño del enjambre con el que se trabajan los experimentos
# ----------------------------------------------------------------------------------
if Fallos == "No":
    for arena in range(5): # Ejecución por tipos de arena T,C,H6,O8,P12 range(5)
        for tam in range(3): # Ejecución por tamaño de arena P,M,G range(3)
            # Ejecuta el experimento múltiples veces
            for exp in range(num_experimentos):
                for i in range(10): # 10 ejecuciones por cada tamaño de enjambre
                    # Modifica el archivo antes de cada ejecución
                    modificar_archivo(file,exp,arena,tam,semilla=0)
                    # EJECUCIÓN DEL EXPERIMENTO
                    ejecucion = ["argos3" ,"-c", file]
                    sb.run(ejecucion)
                    # Esperar un tiempo suficiente para que ARGoS3 cargue antes de simular
                    time.sleep(1)
                # imprimir alguna información después de cada ejecución
                print(pyfiglet.figlet_format( f"Experimento {exp + 1} ejecutado", font="digital"))
    print("Todas las ejecuciones completadas.")
else:
    # Leer el archivo CSV
    df = pd.read_csv('/home/gmadro/swarm_robotics/SWARM_GENERATOR/Experimentos/datos.csv')  # Cambia la ruta según tu ubicación
    arenas = df['Arenatype'].unique() # Extraer tipos de arena
    tams = df['Arenasize'].unique() # Extraer tamaños de arena
    frame = df.query('Class == @tipo_control and MisionID == @misionID') # Filtrar por clase Software y misionID
    fallos = ["Si_1","Si_2", "Si_3"]# Se simularan dos clases de fallos S1-> 10%, S2-> 20%, S3-> 30%
    for i in fallos:
        Fallos =  i
        for c_arena,arena in enumerate(arenas): # Ejecución por tipos de arena T,C,H6,O8,P12 range(5)
            filtro = frame[frame["Arenatype"] == arena] # filtro datos por tipo de arena
            for c_tam,tam in enumerate(tams): # Ejecución por tamaño de arena P,M,G range(3)
                # Ejecuta el experimento múltiples veces con fallos en los robots
                contador = 0
                filtro2 = filtro[filtro["Arenasize"] == tam] # filtro datos por tamaño de arena
                semillas = filtro2['Seed'].to_list() # se extrae los valores de las semillas correspondientes
                for exp in range(num_experimentos):
                    for i in range(10): # 10 ejecuciones por cada tamaño de enjambre
                        iteración = contador + i
                        # Modifica el archivo antes de cada ejecución
                        modificar_archivo(file,exp,c_arena,c_tam,semillas[iteración])
                        # EJECUCIÓN DEL EXPERIMENTO
                        ejecucion = ["argos3" ,"-c", file]
                        sb.run(ejecucion)
                        # Esperar un tiempo suficiente para que ARGoS3 cargue antes de simular
                        time.sleep(1)
                        if i == 9:
                            contador = iteración + 1
                    # Imprimir información después de cada ejecución
                    print(pyfiglet.figlet_format( f"Experimento {exp + 1} ejecutado", font="digital"))
        print("Todas las ejecuciones completadas.")
