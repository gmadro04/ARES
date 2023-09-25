-- Put your global variables here

--[[ This function is executed every time you press the 'execute'
     button ]]
function init()
   -- put your code here
end


--[[ This function is executed at each time step
     It must contain the logic of your controller ]]
function step()
	-- We treat each proximity reading as a vector. The value represents the length
	-- and the angle gives the angle corresponding to the reading, wrt the robot's coordinate system
	-- First, we sum all the vectors.
	accumul = { x=0, y=0 }
	for i = 1, 24 do 
		-- we calculate the x and y components given length and angle
		vec = {
			x = robot.proximity[i].value * math.cos(robot.proximity[i].angle),
			y = robot.proximity[i].value * math.sin(robot.proximity[i].angle)
		}
		-- we sum the vectors into a variable called accumul
		accumul.x = accumul.x + vec.x
		accumul.y = accumul.y + vec.y
	end
	-- we get length and angle of the final sum vector
	length = math.sqrt(accumul.x * accumul.x + accumul.y * accumul.y)
	angle = math.atan2(accumul.y, accumul.x)

	
	if length > 0.2 then
		-- If the angle is greater than 0 the resulting obstacle is on the left. Otherwise it is on the right
		-- We turn with a speed that depends on the angle. The closer the obstacle to the x axis
		-- of the robot, the quicker the turn
		if angle > 0 then
			robot.wheels.set_velocity(math.max(0.5,math.cos(angle)) * 5,0)
		else
			robot.wheels.set_velocity(0, math.max(0.5,math.cos(angle)) * 5)	
		end
	else 
			-- No obstacle. We go straight
			robot.wheels.set_velocity(5,5)
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