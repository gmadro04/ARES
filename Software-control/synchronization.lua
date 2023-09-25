TOP = 50 -- the limit of the counter
ALPHA = 2 -- alpha and beta are the two parameters which dictate how the increment is done
BETA = 10
IGNORE_PHASE = 10 -- once the top is reached, we signal and ignore other signals for some steps
counter = 0
number_robot_sensed = 0
TOTAL = TOP + IGNORE_PHASE -- The total time of the cycle

function init()
	counter = robot.random.uniform(TOP) -- init to a random value
end

function step()

	ProcessRAB() -- check if other robots are signaling
	counter = counter + 1

	if counter < TOP then -- still counting
		robot.range_and_bearing.set_data(1,0) -- no message sent
		if number_robot_sensed > 0 then -- if I sense somebody
			counter = counter + ALPHA * counter/BETA -- increase the counter
			if counter >= TOP then -- but not too much :)
				counter = TOP - 1
			end
		end
	end

	if counter >= TOP then -- we reached the top,
		robot.range_and_bearing.set_data(1,1) -- send a message
		robot.leds.set_all_colors("red") -- lights on
	end

	if counter >= TOTAL then -- the cycle is done
		counter = 0 -- reset the counter
		robot.leds.set_all_colors("black") -- turn off the leds 
		robot.range_and_bearing.set_data(1,0) -- send nothing
	end

end

function ProcessRAB()
	number_robot_sensed = 0
	for i = 1, #robot.range_and_bearing do -- for each robot seen
		if robot.range_and_bearing[i].data[1]==1 then
			number_robot_sensed = number_robot_sensed + 1 -- increase the counter
		end
	end
end

function reset()
	counter = robot.random.uniform(TOP)
end
function destroy()
end