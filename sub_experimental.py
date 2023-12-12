import xml.etree.ElementTree as ET
import os
import subprocess as sb
import loop_exprimentalgenerator as loop
import numpy as np
import random
import pandas as pd
import time


""" RUTAS DE LOS DIRECTORIOS """
# Nombre del archivo XML
dir = "/home/gmadro/swarm_robotics/SWARM_GENERATOR" # ruta del archivo a modificar
# Ruta software de control
codigos = "/home/gmadro/swarm_robotics/SWARM_GENERATOR/Software-control/aggregation_spots.lua"
# obstacleAvoiddance_vec.lua, obstacleAvoidance_Gmadro.lua, aggregation_spots.lua
# color_selection_det.lua, synchronization.lua, aggregation_0_rb_taxis.lua,color_selection_prob.lua
# color_selection_det.lua
"""ARCHIVO DEL EXPERIMENTO"""
file = dir+"/"+"experimento.argos" # cargamos el archivo .argos
#cargamos los datos desde fichero
tree = ET.parse(file)
#cargamos el elemento raiz
root = tree.getroot()

def modificar_archivo(file,exp,arenas,tams):
    """ Configuración parametros básicos """
    arena_params, parametros = loop.params_arena(arenas,tams)    # Tamaño de la arena grande,mediana,pequeña y configuracion de atributos
    # Obstaculos = random.choice([True, False]) 
    Obstaculos = False  # Obstaculos en el escenario si o no, según la eleccion tipo de distribución y tipo de obstaculo
    #robots , time = loop.robots_timeDruation()   # Numero de robots y duraricion del experimento
    if exp >= 1:
        robots = exp*(incremento_robots + num_robots_inicial)
    else:
        robots = num_robots_inicial
    time = loop.robots_timeDruation()
    """ CONFIGURACION ARCHIVO """
    loop.framework_label(file, time, codigos) #Configuración software de control y tiempo ejecucion
    # Configuración de arena
    loop.arena_configuracion(file,arena_params, params=parametros, robots=robots)
    # Configuración obstaculos en la arena
    loop.obstaculos_arena(file=file,obs=Obstaculos,pos_obs=parametros["Pos"],params=parametros)
    # configuración parametros loop_functions
    loop.loops_params(file=file,tipo_arena=parametros["Tipo de arena"],tam_arena=parametros["Tamaño arena"],
                      exp=exp,obstaculos=Obstaculos, robots=robots)
    # Parametros simulación.
    print("----------------------------------------------------")
    simulacion = pd.DataFrame([parametros["Tipo de arena"], parametros["Tamaño arena"],robots,time],index=["TIPO DE ARENA:","TAMAÑO:","# ROBOTS:","T_EXPERIMENTO:"])
    print("************ ",parametros['Tipo de arena'], "************")
    print(simulacion)




# Configuración de la cantidad de ejecuciones
num_robots_inicial = 5
incremento_robots = 5
num_experimentos = 10 # Puedes cambiar esto al número deseado de ejecuciones

for arena in range(5): # Ejecución por tipos de arena T,C,H6,O8,P12
    for tam in range(3): # Ejecución por tamaño de arena P,M,G
        # Ejecuta el experimento múltiples veces
        for exp in range(num_experimentos):
            # Modifica el archivo antes de cada ejecución
            modificar_archivo(file,exp,arena,tam)

            # EJECUCIÓN DEL EXPERIMENTO
            ejecucion = ["argos3" ,"-c", file]
            sb.run(ejecucion)

            # Esperar un tiempo suficiente para que ARGoS3 cargue antes de simular
            time.sleep(2)
            # Puedes imprimir alguna información después de cada ejecución si lo deseas
            print(f"Experimento {exp + 1} ejecutado")

print("Todas las ejecuciones completadas.")
