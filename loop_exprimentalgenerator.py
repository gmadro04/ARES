"""EN ESTE ARCHIVO SE ENCUENTRAN LAS FUNCIONES CON LAS QUE
    SE GENERAN LOS PARAMETROS QUE COMPONEN LOS EXPERIMENTOS"""
# -- LIBRERIAS A USAR
import xml.etree.ElementTree as ET
import numpy as np
import random
import math

"""FUNCIONES DE PARAMETROS BASICOS"""

def params_arena():
    # Se selecciona el tipo de arena que se va a trabajar y modificar
    arenas = ["Triangular","Cuadrada","Hexagonal","Octagonal","Dodecagono"]
    arena = random.choice(arenas)
    #arena = arenas[3]
    # tamaño de la arena
    dim_tam = random.choice(['pequena','mediana','grande'])  # Tipo de tamaño de la arena.
    # Parametros de configuración segun la arena

    if arena == "Cuadrada":
        conf_params, parametros = parametros_arena_cuadrada(dim_tam,arena)
    elif arena == "Triangular":
        conf_params, parametros = parametros_arena_triangular(dim_tam,arena)
    elif arena == "Hexagonal":
        conf_params, parametros = parametros_arena_hexagonal(dim_tam,arena)
    elif arena == "Octagonal":
        conf_params, parametros = parametros_arena_octagonal(dim_tam,arena)
    elif arena == "Dodecagono":
        conf_params, parametros = parametros_arena_dodecagono(dim_tam,arena)
    else:
        print("NO se ha seleccionado arena")

    return conf_params, parametros

def robots_timeDruation():
    # Genera un número aleatorio entre 5 y 15 utilizando una distribución uniforme
    robots = random.randrange(5, 30, 5)
    # Tiempo de suración del experimento
    time = random.choice([170,200])
    return robots,time

def framework_label (file,time,codigos):
    tree = ET.parse(file)
    root = tree.getroot()
    # Modificar la etiqueta 'framework' y sus contenidos
    framework =  root.find("framework")
    controller = root.find("controllers")
    if framework is not None:
        # Modificar atributos de 'experiment'
        experiment = framework.find("experiment")
        if experiment is not None:
            experiment.set("length", str(time))
    for params in controller.iter("params"):
        params.set("script", codigos) # pasamos el script de control
    tree.write(file)

def loops_params(file,tipo_arena,tam_arena,exp):
    tree = ET.parse(file)
    root = tree.getroot()
            # MODIFICAR PARAMETROS LOOP_FUNCTIONS
    loops = root.find("loop_functions") #
    if loops is not None:
        Eparams = loops.find("params")
        # establecer los parametros en las sub etiquetas del loop:functions
        if Eparams is not None:
            Eparams.set("num_experiment",str(exp+1))
            Eparams.set("arena",tipo_arena)
            Eparams.set("tam",tam_arena)
            Eparams.set("mision", "2") # ID del comportamiento que se esta evaluando para ejecutar la mision correspondiente
            Eparams.set("circles","0") # falso 0, verdadero 1
    tree.write(file)

"""FUNCIONES CONFIGURACION PARAMETROS SEGUN LA ARENA"""

"""
    En el disccionario de configuración "arena_conf_params" el orden es el siguiente
    La etiqueta corresponde al box dentro de arena en el archivo
    Donde:
     1. la primera columna es el atributo "id" del box
     2. la segunda columna es el atributo size del box
     3. la terceera columna es el atributo position del body
     4. la cuarta columna es el atributo orientation del body
"""
def parametros_arena_cuadrada(tamaño,tipo_arena):
    paredes = 4 # numero de paredes
    if tamaño == "pequena":
        size  = 4 # medida de la arena pequeña
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    elif tamaño ==  "mediana":
        size  = 8 # medida de la arena mediana
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    elif tamaño == "grande":
        size  = 12 # medida de la arena grande
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    else:
        print("¡¡ ERROR DE CONFIGURACION DE PARAMETROS !!")

    parametros = {
        'Tipo de arena': tipo_arena,
        'Tamaño arena': tamaño ,
        'Paredes': 4,
        'T_arena': size,
        'Pos': pos
    }
    # Parametros configuración de la arena
    arena_conf_params = {
    "Cuadrada": [
        ('1', ",".join(map(str,[0.1,box_size,0.2])), ",".join(map(str,[pos,0,0])), '0,0,0'),
        ('2', ",".join(map(str,[0.1,box_size,0.2])), ",".join(map(str,[-pos,0,0])), '0,0,0'),
        ('3', ",".join(map(str,[box_size,0.1,0.2])), ",".join(map(str,[0,-pos,0])), '0,0,0'),
        ('4', ",".join(map(str,[box_size,0.1,0.2])), ",".join(map(str,[0,pos,0])), '0,0,0')
    ]
    }

    return arena_conf_params, parametros

def parametros_arena_triangular(tamaño,tipo_arena):

    if tamaño == "pequena":
        size  = 4 # medida de la arena pequeña
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    elif tamaño ==  "mediana":
        size  = 8 # medida de la arena mediana
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    elif tamaño == "grande":
        size  = 12 # medida de la arena grande
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    else:
        print("¡¡ ERROR DE CONFIGURACION DE PARAMETROS !!")
    # En esta arena es necesario establecer los parametros L_p y R_param
    L = round(math.sqrt((2**2)+(4**2)),2)
    R_param = size/4
    # print("Razones: ",L, R_param)    # Parametros basicos
    parametros = {
        'Tipo de arena': tipo_arena,
        'Tamaño arena': tamaño,
        'Paredes': 3,
        'T_arena': size,
        'Pos': pos   
    }
    # Parametros configuración de la arena
    arena_conf_params = {
    "Triangular": [
        ('1', ",".join(map(str,[0.1,box_size,0.2])), ",".join(map(str,[-pos,0,0])),'0,0,0'),
        ('2', ",".join(map(str,[0.1,R_param*L,0.2])), ",".join(map(str,[0,pos/2,0])),'63,0,0'),
        ('3', ",".join(map(str,[0.1,R_param*L,0.2])), ",".join(map(str,[0,-pos/2,0])),'-63,0,0')
    ]

    }
    return arena_conf_params, parametros

def parametros_arena_hexagonal(tamaño,tipo_arena):
    if tamaño == "pequena":
        size  = 4 # medida de la arena pequeña
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    elif tamaño ==  "mediana":
        size  = 8 # medida de la arena mediana
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    elif tamaño == "grande":
        size  = 12 # medida de la arena grande
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    else:
        print("¡¡ ERROR DE CONFIGURACION DE PARAMETROS !!")
    # En esta arena es necesario establecer los parametros L_p y R_param
    L = round(math.sqrt((1**2)+(2**2)),2)
    R_param = size/4
    # print("Razones: ",L, R_param)    # Parametros basicos
    parametros = {
        'Tipo de arena': tipo_arena,
        'Tamaño arena': tamaño,
        'Paredes': 6,
        'T_arena': size,
        'Pos': pos
    }
    # Parametros configuración de la arena
    arena_conf_params = {
    "Hexagonal": [
        ('1', ",".join(map(str,[0.1,size/2,0.2])), ",".join(map(str,[pos,0,0])),'0,0,0'),
        ('2', ",".join(map(str,[0.1,size/2,0.2])), ",".join(map(str,[-pos,0,0])),'0,0,0'),
        ('3', ",".join(map(str,[0.1,R_param*L,0.2])), ",".join(map(str,[-pos/2,R_param*1.5,0])),'-65,0,0'),
        ('4', ",".join(map(str,[0.1,R_param*L,0.2])), ",".join(map(str,[pos/2,R_param*1.5,0])),'65,0,0'),
        ('5', ",".join(map(str,[0.1,R_param*L,0.2])), ",".join(map(str,[-pos/2,-R_param*1.5,0])),'65,0,0'),
        ('6', ",".join(map(str,[0.1,R_param*L,0.2])), ",".join(map(str,[pos/2,-R_param*1.5,0])),'-65,0,0')
    ]

    }
    return arena_conf_params, parametros

def parametros_arena_octagonal(tamaño,tipo_arena):
    if tamaño == "pequena":
        size  = 4 # medida de la arena pequeña
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    elif tamaño ==  "mediana":
        size  = 8 # medida de la arena mediana
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    elif tamaño == "grande":
        size  = 12 # medida de la arena grande
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    else:
        print("¡¡ ERROR DE CONFIGURACION DE PARAMETROS !!")
    # En esta arena es necesario establecer los parametros L_p y R_param
    L = round(math.sqrt((1**2)+(1**2)),2)
    R_param = size/4
    # print("Razones: ",L, R_param)    # Parametros basicos
    parametros = {
        'Tipo de arena': tipo_arena,
        'Tamaño arena': tamaño,
        'Paredes': 8,
        'T_arena': size,
        'Pos': pos
    }
    # Parametros configuración de la arena
    arena_conf_params = {
    "Octagonal": [
        ('1', ",".join(map(str,[0.1,size/2,0.2])), ",".join(map(str,[pos,0,0])),'0,0,0'),
        ('2', ",".join(map(str,[0.1,size/2,0.2])), ",".join(map(str,[-pos,0,0])),'0,0,0'),
        ('3', ",".join(map(str,[0.1,size/2,0.2])), ",".join(map(str,[0,pos,0])),'90,0,0'),
        ('4', ",".join(map(str,[0.1,size/2,0.2])), ",".join(map(str,[0,-pos,0])),'90,0,0'),
        ('5', ",".join(map(str,[0.1,R_param*L,0.2])), ",".join(map(str,[-R_param*1.5,-R_param*1.5,0])),'45,0,0'),
        ('6', ",".join(map(str,[0.1,R_param*L,0.2])), ",".join(map(str,[R_param*1.5,R_param*1.5,0])),'45,0,0'),
        ('7', ",".join(map(str,[0.1,R_param*L,0.2])), ",".join(map(str,[R_param*1.5,-R_param*1.5,0])),'-45,0,0'),
        ('8', ",".join(map(str,[0.1,R_param*L,0.2])), ",".join(map(str,[-R_param*1.5,R_param*1.5,0])),'-45,0,0')
    ]

    }
    return arena_conf_params, parametros

def parametros_arena_dodecagono(tamaño,tipo_arena):
    if tamaño == "pequena":
        size  = 4 # medida de la arena pequeña
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    elif tamaño ==  "mediana":
        size  = 8 # medida de la arena mediana
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    elif tamaño == "grande":
        size  = 12 # medida de la arena grande
        box_size = size # tamaño de las cajas que rodean la arena
        pos = 2+0.5*(abs(size-4)) # razon de la posición segun cambie el tamaño
    else:
        print("¡¡ ERROR DE CONFIGURACION DE PARAMETROS !!")
    # En esta arena es necesario establecer los parametros L_p y R_param
    L = round(math.sqrt((1**2)+(1**2)),2)
    R_param = size/4
    # print("Razones: ",L, R_param)    # Parametros basicos
    parametros = {
        'Tipo de arena': tipo_arena,
        'Tamaño arena': tamaño,
        'Paredes': 8,
        'T_arena': size,
        'Pos': pos
    }
    # Parametros configuración de la arena
    arena_conf_params = {
    "Dodecagono": [
        ('1', ",".join(map(str,[0.1,R_param*1.1,0.2])), ",".join(map(str,[-pos,0,0])),'0,0,0'),
        ('2', ",".join(map(str,[0.1,R_param*1.1,0.2])), ",".join(map(str,[pos,0,0])),'0,0,0'),
        ('3', ",".join(map(str,[0.1,R_param*1.1,0.2])), ",".join(map(str,[0,pos,0])),'90,0,0'),
        ('4', ",".join(map(str,[0.1,R_param*1.1,0.2])), ",".join(map(str,[0,-pos,0])),'90,0,0'),
        ('5', ",".join(map(str,[0.1,R_param*1.1,0.2])), ",".join(map(str,[-R_param*1,-R_param*1.733,0])),'60,0,0'),
        ('6', ",".join(map(str,[0.1,R_param*1.1,0.2])), ",".join(map(str,[-R_param*1.733,-R_param*1,0])),'30,0,0'),
        ('7', ",".join(map(str,[0.1,R_param*1.1,0.2])), ",".join(map(str,[R_param*1,R_param*1.733,0])),'60,0,0'),
        ('8', ",".join(map(str,[0.1,R_param*1.1,0.2])), ",".join(map(str,[R_param*1.733,R_param*1,0])),'30,0,0'),
        ('9', ",".join(map(str,[0.1,R_param*1.1,0.2])), ",".join(map(str,[-R_param*1,R_param*1.733,0])),'-60,0,0'),
        ('10', ",".join(map(str,[0.1,R_param*1.1,0.2])), ",".join(map(str,[-R_param*1.733,R_param*1,0])),'-30,0,0'),
        ('11', ",".join(map(str,[0.1,R_param*1.1,0.2])), ",".join(map(str,[R_param*1,-R_param*1.733,0])),'-60,0,0'),
        ('12', ",".join(map(str,[0.1,R_param*1.1,0.2])), ",".join(map(str,[R_param*1.733,-R_param*1,0])),'-30,0,0')
    ]

    }
    return arena_conf_params, parametros

def distribucion(file,arena_params,params):
    pos = []
    if params['Tipo de arena'] == 'Cuadrada':
        # pos = [params["Pos"],params["Pos"],0]
        pos_min = [-params["Pos"],-params["Pos"],0]
        pos_max = [params["Pos"],params["Pos"],0]
    elif params["Tipo de arena"] == "Triangular":
        # pos = [params["Pos"],params["T_arena"]/4,0]
        pos_min = [-params["Pos"],-params["T_arena"]/4,0] 
        pos_max = [0,params["T_arena"]/4,0]
    elif params['Tipo de arena'] == "Hexagonal":
        pos_min = [-params["Pos"],-params["T_arena"]/4,0]
        pos_max = [params["Pos"],params["T_arena"]/4,0]
    else:
        # pos = [params["Pos"]-1,(params['T_arena']/4)*1+1,0]
        pos_min = [-1*(params["Pos"]-1),-1*((params['T_arena']/4)*1+1),0]
        pos_max = [params["Pos"]-1,(params['T_arena']/4)*1+1,0]

    return pos_min, pos_max

""" CONFIGURACION ARENA """
"""
    En esta parte se configura la arena donde se va a ejecutar el experimento
    1. Se ajusta tanto el tamaño de la arena (plano X,Y)
    2. Se crean las paredes necesarias que encierran a los robots, según tipo de arena
    3. Finalmente se distribuyen los robots teniendo en cuenta la arena.
"""
def arena_configuracion(file,arena_params,params,robots):
    tree = ET.parse(file)
    root = tree.getroot()
    # Encuentra la etiqueta <arena>
    arena = root.find(".//arena")
    # print("# Etiquetas de arena:", len(arena)) # Cuantas tags hay en el archivo
    if arena is not None:
        # Realiza las modificaciones que desees en la etiqueta "arena" y sus subetiquetas aquí
        # nuevo_size = [params['T_arena'],params['T_arena'],1] # Configuración arena con su tamaño
        size = [15,15,1] # Tamaño de la arena, estandar
        arena.set("size", ",".join(map(str, size))) # Nuevas dimensiones de la arena  Convierte la lista a una cadena separada por comas

    # Borra las subetiquetas <box> dentro de la etiqueta <arena>
    for box in arena.findall("box"):
        arena.remove(box)

    # Crea las subetiquetas <box> según el tipo de arena
    arena_type = params['Tipo de arena']
    # Crea las subetiquetas <box> según el tipo de arena y las variables configuradas
    arena_configuration = arena_params.get(params['Tipo de arena'], [])

    for x, configuration in enumerate(arena_configuration):
        #print(x , configuration)
        box = ET.Element("box")
        box.set("id", configuration[0])
        box.set("size", configuration[1])
        box.set("movable", "false")
        body = ET.SubElement(box, "body")
        body.set("position", configuration[2])
        body.set("orientation", configuration[3])
        #arena.append(box)
        arena.insert(x,box)
    #Funcion que configura la distribución de los robots
    pos_min, pos_max = distribucion(file,arena_params,params)
    # Etiqueta cantidad de robots y distribución de robots--------------------
    distribute = arena.find("distribute")
    if distribute is not None:
        entity = distribute.find("entity")
        position = distribute.find("position")
        # Distribución de los robots en el escenario segun las posicion de las paredes que lo cierran
        # pos_min = [-pos[0],-pos[1],0]
        # pos_max = [pos[0],pos[1],0]
        if entity is not None and position is not None:
            entity.set("quantity", str(robots))
            position.set("min",",".join(map(str,pos_min)))
            position.set("max",",".join(map(str,pos_max)))

    # Guarda la configuración modificada
    tree.write(file)

    # print(f'Se ha configurado el archivo .argos para usar la arena "{arena_type}"')

def obstaculos_arena(file,obs,pos_obs,params):
    tree = ET.parse(file)
    root = tree.getroot()

    arena = root.find("arena")
    pos_min, pos_max = distribucion(file,pos_obs,params)
    # pos_min = [-pos[0],-pos[1],0]
    # pos_max = [pos[0],pos[1],0]
    #print(len(arena),"\n",arena[5])
    for distribute in arena.findall(".//distribute"):
        if "box" in ET.tostring(distribute).decode():
            etiqueta_existe = True # la etiqueta existe
            etiqueta_a_eliminar = distribute # Se identifica la etiqueta de obstaculos
        else:
            etiqueta_existe = False # No existe la etiqueta
    # print("-----SI entra -----")
    if obs and not etiqueta_existe: # Si se requiere obstaculos y la etiqueta no existe la crea
        # Crea la etiqueta '<distribute>' y agrega contenido
        #print("ESTADO1")
        distribute = ET.Element("distribute")
        position = ET.Element("position")
        position.set("method", "uniform")
        position.set("min", ",".join(map(str,pos_min)))
        position.set("max", ",".join(map(str,pos_max)))
        distribute.append(position)

        orientation = ET.Element("orientation")
        orientation.set("method", "uniform")
        orientation.set("min", "0,0,0")
        orientation.set("max", "360,0,0")
        distribute.append(orientation)

        entity = ET.Element("entity")
        entity.set("quantity", "10")
        entity.set("max_trials", "1000")
        x_box = random.uniform(0.2,0.7) # tam x del box
        y_box = random.uniform(0.2,0.7) # tam y del box
        boxes = [round(x_box,1),round(y_box,1),0.2] # datos de tam x,y,z de los boxes
        box = ET.Element("box")
        box.set("id", "o")
        #box.set("size", "0.2, 0.2, 0.2")
        box.set("size", ",".join(map(str,boxes))) # Inserto los obtaculos de tamaño aleatorio
        box.set("movable", "false")
        entity.append(box)

        distribute.append(entity)

        # Agrega la nueva '<obstaculos>' a 'arena'
        #arena.append(distribute)
        arena.insert(len(arena), distribute)
    # Si la variable externa es False y existe una subetiqueta <distribute>, elimínala
    elif not obs and arena.find(".//distribute") is not None:
        #print("ESTADO2")
        # Encuentra la etiqueta '<distribute>' dentro de '<arena>' con contenido específico y la elimina
        # para el caso se necesita eliminar los obstaculos, por lo que se diferencia por el
        # atributo "box" o "cilinder"
        etiqueta_a_eliminar = None
        for distribute in arena.findall(".//distribute"):
            # Realiza una verificación basada en el contenido único
            if "box" in ET.tostring(distribute).decode():
                etiqueta_a_eliminar = distribute
                break

        # Si se encontró la etiqueta a eliminar, elimínala
        if etiqueta_a_eliminar is not None:
            arena.remove(etiqueta_a_eliminar)
    elif not obs and not etiqueta_existe: # No se rerquiere obs y la etiqueta no existe, salta
        #print("ESTADO3")
        pass # no hace nada se salta todo
    elif obs and etiqueta_existe: # Se requieren obs y ya existe una etiqueta
        # Se borra la etiqueta anteriror y se crea una nueva
        #print("ESTADO4")
        #Borrando la etiqeuta existente
        if etiqueta_a_eliminar is not None:
            arena.remove(etiqueta_a_eliminar)
        #Ahora se crea la nueva etiqueta
        # Crea la etiqueta '<distribute>' y agrega contenido

        distribute = ET.Element("distribute")

        position = ET.Element("position")
        position.set("method", "uniform")
        position.set("min", ",".join(map(str,pos_min)))
        position.set("max", ",".join(map(str,pos_max)))
        distribute.append(position)

        orientation = ET.Element("orientation")
        orientation.set("method", "uniform")
        orientation.set("min", "0,0,0")
        orientation.set("max", "360,0,0")
        distribute.append(orientation)

        entity = ET.Element("entity")
        entity.set("quantity", "15")
        entity.set("max_trials", "100")

        box = ET.Element("box")
        box.set("id", "o")
        box.set("size", "0.2, 0.2, 0.2")
        box.set("movable", "false")
        entity.append(box)

        distribute.append(entity)

        # Agrega la nueva '<obstaculos>' a 'arena'
        #arena.append(distribute)
        arena.insert(len(arena), distribute)
    # Se guardan los cambios realizados
    tree.write(file)