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


|*| Software de control -> Se dividen en dos categorias  1-> A y 2-> B
Puedes seleccionar entre uno y el otro para llevar a cabo tu experimento
---------- Comportamiento categoria A ----------
* A_obstacleAvoiddance_sta.lua
* A_aggregation_0_rb_taxis.lua
* A_pattern_formation_flocking.lua
* A_color_selection_det.lua
---------- Comportamiento categoria B ----------
* B_aggregation_spots.lua
* B_color_selection_prob.lua
* B_obstacleAvoiddance_vec.lua
* B_pattern_formation.lua
|*| Mision a evaluar -> Cada comportamiento se evalua en una misión especifica
Obstacle_avoid_dance -- Mision exploración
Agreggation -- Mision agregación
Pattern_Formation -- Mision formación de patrones
Mision ID --> Toma un valor para poder evaluar la mision a ejecutar
* Mision ID = 1 -> Mision exploración
* Mision ID = 2 -> Mision agregación
* Mision ID = 3 -> Mision marcha en formación
* Mision ID = 4 -> Mision toma de decisiones colectiva

! IMPORTANTE !
LOS UNICOS PARAMETROS QUE DEBES MODIFICAR MANUALMENTE SON:
--> variables "Fallos" : Especifica si deseas trabajar con fallos o no
--> variable "tipo_control" : Especifica la categoria del software de control que estas evaluando
--> Variable "misionID" : Especifica el tipo de mision que vas a evaluar, debe ser coherente con el software de control correpondiente a la mision
"""

""" RUTAS DE LOS DIRECTORIOS Y CONFIGURACIONES"""
# ----------------- CONFIGURACIÓN DE FALLOS, TIPO DE SOFTWWARE DE CONTROL Y MISION A EJECUTAR
# -------------------------- Puedes trabajar con el enjmabre sin fallos o con fallos
# EL PORCENTAJE DE FALLOS DEL TOTAL DEL ENJAMBRE ES 30%
Fallos = "No" # MOdifica esta variable según tu evaluación
tipo_control = "B" # Especifica que categoria de comportamiento estas evaluando
# ------------------------- Mision ID
misionID = 1 # Configura el id de la mision a evaluar 1,2,3,4
if misionID == 1:
    mision = 'Exploración'
elif misionID == 2:
    mision = 'Agregación'
elif misionID == 3:
    mision = 'Marcha en Formación'
else:
    mision = 'Decisión Colectiva'
# ------------------------- Ruta del archivo "file".argos del experimento (XML)
dir = "/home/gmadro/swarm_robotics/SWARM_GENERATOR" # ruta del archivo a modificar
# --------------------------Ruta software de control
codigos = "/home/gmadro/swarm_robotics/SWARM_GENERATOR/Software-control/B_color_selection_prob.lua"
# ----------------------------------------------------------------------------------
"""LECTURA ARCHIVO DEL EXPERIMENTO"""
file = dir+"/"+"experimento.argos" # cargamos el archivo .argos
#cargamos los datos desde fichero
tree = ET.parse(file)
#cargamos el elemento raiz
root = tree.getroot()

def modificar_archivo(file,exp,arenas,tams,semilla):
    """ Configuración parametros básicos """
    arena_params, parametros = loop.params_arena(arenas,tams)    # Tamaño de la arena grande,mediana,pequeña y configuracion de atributos
    Obstaculos = False  # Obstaculos en el escenario si o no, según la eleccion tipo de distribución y tipo de obstaculo
    # Numero de robots y tiempo de duración del experimento
    #robots =  exp*(incremento_robots + num_robots_inicial) if exp >=1  else num_robots_inicial
    robots = t_robots[exp]
    time = 240 # Duración experimento en seg
    """ CONFIGURACION ARCHIVO """
    loop.framework_label(file, time, codigos, Fallos, semilla) #Configuración software de control y tiempo ejecucion
    # Configuración de arena
    loop.arena_configuracion(file,arena_params, params=parametros, robots=robots)
    # Configuración obstaculos en la arena
    loop.obstaculos_arena(file=file,obs=Obstaculos,pos_obs=parametros["Pos"],params=parametros)
    # configuración parametros loop_functions
    loop.loops_params(file=file,tipo_arena=parametros["Tipo de arena"],tam_arena=parametros["Tamaño arena"],
                    exp=exp,obstaculos=Obstaculos, robots=robots, m_ID=misionID, E_fallos=Fallos, T_Control = tipo_control)
    # Parametros simulación.
    simulacion = pd.DataFrame([parametros["Tamaño arena"],robots,str(misionID)+"-"+mision,time,Fallos],
                                index=["TAMAÑO:","# ROBOTS:","TIPO MISION:","T_EXPERIMENTO:","FALLOS:"])
    print(pyfiglet.figlet_format("Arena" + parametros['Tipo de arena']))
    print(simulacion)

# Configuración de la cantidad de ejecuciones
num_robots_inicial = 2
incremento_robots = 5
num_experimentos = 12 # Puedes cambiar esto al número deseado de ejecuciones (exp=12, robots= 2,5...100)
t_robots = [2,5,10,20,30,40,50,60,70,80,90,100] # Tamaño del enjambre con el que se trabajn los experimentos
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
                # Puedes imprimir alguna información después de cada ejecución si lo deseas
                print(pyfiglet.figlet_format( f"Experimento {exp + 1} ejecutado", font="digital"))
    print("Todas las ejecuciones completadas.")
else:
    # Leer el archivo CSV
    df = pd.read_csv('/home/gmadro/swarm_robotics/SWARM_GENERATOR/Experimentos/datos.csv')  # Cambia la ruta según tu ubicación
    arenas = df['Arenatype'].unique()
    tams = df['Arenasize'].unique()

    for c_arena,arena in enumerate(arenas): # Ejecución por tipos de arena T,C,H6,O8,P12 range(5)
        contador = 0

        filtro = df[df["Arenatype"] == arena]
        for c_tam,tam in enumerate(tams): # Ejecución por tamaño de arena P,M,G range(3)
            # Ejecuta el experimento múltiples veces con fallos en los robots
            filtro2 = filtro[filtro["Arenasize"] == tam]
            semillas = filtro2['Seed']
            print(len(semillas))
            for exp in range(num_experimentos):
                for i in range(10): # 10 ejecuciones por cada tamaño de enjambre
                    iteración = contador + i
                    semilla = semillas[iteración]
                    # Modifica el archivo antes de cada ejecución
                    modificar_archivo(file,exp,c_arena,c_tam,semilla)
                    # EJECUCIÓN DEL EXPERIMENTO
                    ejecucion = ["argos3" ,"-c", file]
                    sb.run(ejecucion)
                    # Esperar un tiempo suficiente para que ARGoS3 cargue antes de simular
                    time.sleep(1)
                    if i == 9:
                        contador = iteración + 1
                # Puedes imprimir alguna información después de cada ejecución si lo deseas
                print(pyfiglet.figlet_format( f"Experimento {exp + 1} ejecutado", font="digital"))
    print("Todas las ejecuciones completadas.")
