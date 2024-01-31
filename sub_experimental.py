import xml.etree.ElementTree as ET
import os
import subprocess as sb
import loop_exprimentalgenerator as loop
import numpy as np
import random
import pandas as pd
import time
import pyfiglet

"""
   ______       _____    ____  __  ___
  / ___/ |     / /   |  / __ \/  |/  /
  \__ \| | /| / / /| | / /_/ / /|_/ /
 ___/ /| |/ |/ / ___ |/ _, _/ /  / /
/____/ |__/|__/_/  |_/_/ |_/_/  /_/
   _____________   ____________  ___  __________  ____
  / ____/ ____/ | / / ____/ __ \/   |/_  __/ __ \/ __ \
 / / __/ __/ /  |/ / __/ / /_/ / /| | / / / / / / /_/ /
/ /_/ / /___/ /|  / /___/ _, _/ ___ |/ / / /_/ / _, _/
\____/_____/_/ |_/_____/_/ |_/_/  |_/_/  \____/_/ |_|

"""

""" RUTAS DE LOS DIRECTORIOS """
# Nombre del archivo XML
dir = "/home/gmadro/swarm_robotics/SWARM_GENERATOR" # ruta del archivo a modificar
# Ruta software de control
codigos = "/home/gmadro/swarm_robotics/SWARM_GENERATOR/Software-control/aggregation_0_rb_taxis.lua"
misionID = 2 # Configura el id de la mision a evaluar
if misionID == 1:
    mision = 'Exploración'
elif misionID == 2:
    mision = 'Agregación'
elif misionID == 3:
    mision = 'Marcha en Formación'
else:
    mision = 'Decisión Colectiva'
"""Path del software de control a evaluar
Mision ID --> Toma un valor para poder evaluar la mision a ejecutar
* Mision ID = 1 -> Mision exploración
* Mision ID = 2 -> Mision agregación
* Mision ID = 3 -> Mision marcha en formación
* Mision ID = 4 -> Mision toma de decisiones colectiva
"""
# obstacleAvoiddance_vec.lua, obstacleAvoiddance_sta.lua
# aggregation_spots.lua, aggregation_0_rb_taxis.lua
# pattern_formation.lua, pattern_formation_flocking.lua
# color_selection_prob.lua, color_selection_det.lua

"""ARCHIVO DEL EXPERIMENTO"""
file = dir+"/"+"experimento.argos" # cargamos el archivo .argos
#cargamos los datos desde fichero
tree = ET.parse(file)
#cargamos el elemento raiz
root = tree.getroot()

def modificar_archivo(file,exp,arenas,tams):
    """ Configuración parametros básicos """
    arena_params, parametros = loop.params_arena(arenas,tams)    # Tamaño de la arena grande,mediana,pequeña y configuracion de atributos
    Obstaculos = False  # Obstaculos en el escenario si o no, según la eleccion tipo de distribución y tipo de obstaculo
    # Numero de robots y tiempo de duración del experimento
    robots =  exp*(incremento_robots + num_robots_inicial) if exp >=1  else num_robots_inicial
    time = 240 # Duración experimento en seg
    """ CONFIGURACION ARCHIVO """
    loop.framework_label(file, time, codigos) #Configuración software de control y tiempo ejecucion
    # Configuración de arena
    loop.arena_configuracion(file,arena_params, params=parametros, robots=robots)
    # Configuración obstaculos en la arena
    loop.obstaculos_arena(file=file,obs=Obstaculos,pos_obs=parametros["Pos"],params=parametros)
    # configuración parametros loop_functions
    loop.loops_params(file=file,tipo_arena=parametros["Tipo de arena"],tam_arena=parametros["Tamaño arena"],
                      exp=exp,obstaculos=Obstaculos, robots=robots, m_ID=misionID)
    # Parametros simulación.
    simulacion = pd.DataFrame([parametros["Tipo de arena"], parametros["Tamaño arena"],robots,str(misionID)+"-"+mision,time],
                              index=["TIPO DE ARENA:","TAMAÑO:","# ROBOTS:","TIPO MISION:","T_EXPERIMENTO:"])
    print(pyfiglet.figlet_format("Arena" + parametros['Tipo de arena']))
    print(simulacion)

# Configuración de la cantidad de ejecuciones
num_robots_inicial = 5
incremento_robots = 5
num_experimentos = 11 # Puedes cambiar esto al número deseado de ejecuciones

for arena in range(5): # Ejecución por tipos de arena T,C,H6,O8,P12 range(5)
    for tam in range(3): # Ejecución por tamaño de arena P,M,G range(3)
        # Ejecuta el experimento múltiples veces
        for exp in range(num_experimentos):
            for i in range(10): # 10 ejecuciones por cada tamaño de enjambre
                # Modifica el archivo antes de cada ejecución
                modificar_archivo(file,exp,arena,tam)
                # EJECUCIÓN DEL EXPERIMENTO
                ejecucion = ["argos3" ,"-c", file]
                sb.run(ejecucion)
                # Esperar un tiempo suficiente para que ARGoS3 cargue antes de simular
                time.sleep(1)
            # Puedes imprimir alguna información después de cada ejecución si lo deseas
            print(pyfiglet.figlet_format( f"Experimento {exp + 1} ejecutado", font="digital"))

print("Todas las ejecuciones completadas.")
