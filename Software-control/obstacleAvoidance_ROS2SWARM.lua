-- Use Shift + Click to select a robot
-- When a robot is selected, its variables appear in this editor

-- Use Ctrl + Click (Cmd + Click on Mac) to move a selected robot to a different location



-- Put your global variables here

Fun = require 'Utils-functions.scan_calculation_functions'
-- Parametros de configuracion 
hardware_protection_layer_max_range = 0.2 --105mm Robot outer radius + 15mm accuracy offset+ 100mm buffer zone
hardware_protection_layer_min_range = 0.1--0.05--80 mm
hardware_protection_layer_front_attraction = 3--3--2
hardware_protection_layer_threshold = 1 --5
max_translational_velocity = 0.22
max_rotational_velocity = 2.84

-- Estableciendo parámetros para enviar
param_max_range = hardware_protection_layer_max_range
param_min_range = hardware_protection_layer_min_range
param_front_attraction = hardware_protection_layer_front_attraction
param_threshold = hardware_protection_layer_threshold
param_max_translational_velocity = max_translational_velocity
param_max_rotational_velocity = max_rotational_velocity
avoid_distance = param_max_range


SPEED = 5 -- Velocidad del robot



--[[ This function is executed every time you press the 'execute' button ]]
function init()
   -- put your code here
-- Arreglos que recibiran la informacion 
	Direccion = {} -- revibe velcidad y angulo 
	Obstacle = {} -- recibe el parametro de si es necesario o no   	esquivar inicia en falso 
	giro = 0 -- giro del robot para evitar obstaculo
end



--[[ This function is executed at each time step
     It must contain the logic of your controller ]]
function step()
   -- put your code here
-- Datos que se envian de los sensores rangos de distancia y angulos 
	current_ranges = {}
	angles = {}

	-- se escanean los datos de los ranges para enviar junto con los parametros
	for i=1,24 do
		current_ranges[i] = robot.proximity[i].value
		angles[i] = robot.proximity[i].angle
	end 

	-- Llamado de la funciuon potential field en Scan calculations functions
	Direccion, Obstacle = Fun.Potential_field(param_front_attraction,avoid_distance,param_max_rotational_velocity,param_max_translational_velocity, param_min_range, param_threshold, current_ranges,angles)

   Obstacle = not Obstacle

	--logerr("INFO Direccion= " .. Direccion[1] .. "," .. Direccion[2])
	--logerr("INFO Obstacle= " .. Obstacle)
	--logerr(Obstacle)

    -- Se saca el angulo en rad con la funcion arc.math2
	angle = math.atan2(Direccion[2],Direccion[1])
	--logerr("Angulo= " .. angle)
	-- Saco el angulo y miro que decision tomar si esta entre 0 y 180 entonces giro a la derecha, izquierda en caso contrario 
	if (angle*180)/math.pi > 0 and (angle*180)/math.pi < 180 then
		giro = 1 -- Derecha
	else 
		giro = -1 -- Izquierda
	end  

	-- Evaluacion de los datos y obstacle avoiddance
	if Obstacle then 
		if giro == 1 then
			robot.wheels.set_velocity(5,-2)
		else
			robot.wheels.set_velocity(-2,5)
		end
	else 
		robot.wheels.set_velocity(SPEED,SPEED)
	end
end



--[[ This function is executed every time you press the 'reset'
     button in the GUI. It is supposed to restore the state
     of the controller to whatever it was right after init() was
     called. The state of sensors and actuators is reset
     automatically by ARGoS. ]]
function reset()
   -- put your code here
end



--[[ This function is executed only once, when the robot is removed
     from the simulation ]]
function destroy()
   -- put your code here
end