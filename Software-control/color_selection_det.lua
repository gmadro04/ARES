-- Put your global variables here
MY_COLOR="green"

current_turn_steps = 0
avoiding_obs = false
MAX_TURN_STEPS = 40


--[[ This function is executed every time you press the 'execute'
     button ]]
function init()
	reset()
end

-- function used to copy two tables
function table.copy(t)
  local t2 = {}
  for k,v in pairs(t) do
    t2[k] = v
  end
  return t2
end



--[[ This function is executed at each time step
     It must contain the logic of your controller ]]
function step()
	robot.leds.set_all_colors(MY_COLOR)
	walk()

	count_red = 0	
	count_green = 0
	count_blue = 0

	if(MY_COLOR == "red") then 
		count_red = count_red + 1
	elseif(MY_COLOR == "green" ) then
		count_green = count_green + 1
	else
		count_blue = count_blue + 1
	end
	
	num_neighbors = #robot.range_and_bearing

	for i = 1, #robot.range_and_bearing do -- for each robot seen
		if robot.range_and_bearing[i].data[1] == 1 then 
			count_red = count_red + 1
		end
		if robot.range_and_bearing[i].data[1] == 2 then
			count_green = count_green + 1
		end
		if robot.range_and_bearing[i].data[1] == 3 then
			count_blue = count_blue + 1
		end
	end
	
	majority = math.max(count_red, count_green, count_blue)
	if((majority == count_red and majority == count_green) or (majority == count_red and majority == count_blue) or (majority == count_blue and majority == count_green)) then
		-- nothing to do
	else
		if(count_red == majority) then
			MY_COLOR = "red"
		elseif(count_green == majority) then
			MY_COLOR = "green"
		else
			MY_COLOR = "blue"
		end
	end

	if(MY_COLOR == "red") then 
		robot.range_and_bearing.set_data(1,1)
	elseif(MY_COLOR == "green" ) then
		robot.range_and_bearing.set_data(1,2)
	else
		robot.range_and_bearing.set_data(1,3)
	end

end

function walk()
   is_obstacle_sensed = false
   sort_prox = table.copy(robot.proximity)
   table.sort(sort_prox, function(a,b) return a.value>b.value end)
   if sort_prox[1].value > 0.05 and math.abs(sort_prox[1].angle) < math.pi/2
      then is_obstacle_sensed = true
   end
	if not avoiding_obs then
		robot.wheels.set_velocity(10,10)
		if is_obstacle_sensed then -- obstacle sensed
		   avoiding_obs = true -- change state to avoidance
		   current_turn_steps = robot.random.uniform_int(2,MAX_TURN_STEPS) -- set the number of steps to turn on the spot
			-- to avoid obstacles, the robot turns on itself for a random number of steps 
   			-- between 2 and MAX_TURN_STEPS
   		end	
   else
		robot.wheels.set_velocity(-10,10)
		current_turn_steps = current_turn_steps - 1
		if current_turn_steps <= 0 then
		   avoiding_obs = false
		end
	end	
end


--[[ This function is executed every time you press the 'reset'
     button in the GUI. It is supposed to restore the state
     of the controller to whatever it was right after init() was
     called. The state of sensors and actuators is reset
     automatically by ARGoS. ]]
function reset()
	rnd = robot.random.uniform()
	if(rnd < 0.333) then
		MY_COLOR = "red"
		robot.range_and_bearing.set_data(1,1)
	elseif(rnd < 0.666) then
		MY_COLOR = "green"
		robot.range_and_bearing.set_data(1,2)
	else
		MY_COLOR = "blue"
		robot.range_and_bearing.set_data(1,3)
	end
	robot.leds.set_all_colors(MY_COLOR)
end



--[[ This function is executed only once, when the robot is removed
     from the simulation ]]
function destroy()
   -- put your code here
end