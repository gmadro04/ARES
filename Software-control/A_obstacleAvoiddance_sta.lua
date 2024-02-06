-- Put your global variables here
avoid_obstacle = false

--[[ This function is executed every time you press the 'execute'
     button ]]
function init()
   -- put your code here
end



--[[ This function is executed at each time step
     It must contain the logic of your controller ]]
function step()
	
	-- SENSE
	obstacle = false
	for i=1,4 do
		if (robot.proximity[i].value > 0.2) then
			obstacle = true
			break
		end
	end
	if (not obstacle) then
		for i=20,24 do
			if (robot.proximity[i].value > 0.2) then
				obstacle = true
				break
			end			
		end
	end

	-- THINK	
	if(not avoid_obstacle) then
		if(obstacle) then
			avoid_obstacle = true
			turning_steps = robot.random.uniform_int(4,30)
			turning_right = robot.random.bernoulli()
		end
	else
		turning_steps = turning_steps - 1
		if(turning_steps == 0) then 
			avoid_obstacle = false
		end
	end

	-- ACT
	if(not avoid_obstacle) then
		robot.wheels.set_velocity(5,5)
	else
		if(turning_right == 1) then
			robot.wheels.set_velocity(5,-5)
		else
			robot.wheels.set_velocity(-5,5)
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