-- Use Shift + Click to select a robot
-- When a robot is selected, its variables appear in this editor

-- Use Ctrl + Click (Cmd + Click on Mac) to move a selected robot to a different location



-- Put your global variables here



--[[ This function is executed every time you press the 'execute' button ]]
function init()
   -- put your code here
estado = "explorar"
end



--[[ This function is executed at each time step
     It must contain the logic of your controller ]]
function step()
   -- put your code here
	if estado == "explorar" then
		estado = explore()
	elseif estado == "parar" then
		estado = explore()
		--robot.wheels.set_velocity(0,0)
		agregar()
	elseif estado == "quedarse" then
		for i=1, 4 do 
			if robot.motor_ground[i].value == 0 then 
				explore_ground()
			else 
				robot.wheels.set_velocity(10,0)
			end
		end	
	end
end


function explore()
	value = 0
	pos = -1
	for i=1, 24 do 
		if robot.proximity[i].value > value then 
			pos = i
			value = 1
		end
	end

	if value == 0 then
		robot.wheels.set_velocity(5,5)
		
	else
		
		if pos <= 12 then 
			robot.wheels.set_velocity(5,0)
			value = 0		
		else
			robot.wheels.set_velocity(0,5)
			value = 0
		end
	end

	for i=1, 4 do 
		if robot.motor_ground[i].value == 0 then 
			estado = "parar"
		else
			estado = "explorar"
		end
	end	

	return estado
end

function agregar()
	robot.wheels.set_velocity(0,0)
	estado = "quedarse"
	return estado
end

function explore_ground()
	value = 0
	pos = -1
	for i=1, 24 do 
		if robot.proximity[i].value > value then 
			pos = i
			value = 1
		end
	end

	if value == 0 then
		robot.wheels.set_velocity(5,5)
	else
		if pos <= 12 then 
			robot.wheels.set_velocity(5,0)
			value = 0		
		else
			robot.wheels.set_velocity(0,5)
			value = 0
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
function destroy()
   -- put your code here
end