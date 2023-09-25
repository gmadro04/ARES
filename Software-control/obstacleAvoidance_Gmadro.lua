-- Use Shift + Click to select a robot
-- When a robot is selected, its variables appear in this editor

-- Use Ctrl + Click (Cmd + Click on Mac) to move a selected robot to a different location



-- Put your global variables here

vel = 5-- velocidad del robot, se puede modificar de 2-10 (recomnedable)

--[[ This function is executed every time you press the 'execute' button ]]
function init()
   -- put your code here
end



--[[ This function is executed at each time step
     It must contain the logic of your controller ]]
function step()
   -- Movimineto aleatoreo GMadro04
-- variables para controlar el indice del sensor que toma la medida y que controla la evación de obstaculos
obstaculo = 0 -- control de obstaculo
data = -1 -- valor del sensor medido 

-- Ciclo para sensar si hay obstaculos 
for i=1,24 do
-- Si hay un obstaculo se guarada el en la variable data el indice del sensor que tomo la medida
  	if 0.2 < robot.proximity[i].value then
    	data = i --valor sensor que tomo la medida 
		obstaculo = 1 -- Hay obstaculo 
	end
end


if obstaculo == 0 then 
-- No hay obstaculos
	robot.wheels.set_velocity(vel,vel)
else
-- Hay obstaculo, se debe esquivar según donde se encuentre el objeto
	if data <= 12 then 
		-- Hay obstaculo entre 0-180 grados, girar derecha
		robot.wheels.set_velocity(vel,0)
		obstaculo = 0
	else 
	-- Hay obstaculo entre 0-180 grados, girar izquierda
		robot.wheels.set_velocity(0,vel)
		obstaculo = 0
	end
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