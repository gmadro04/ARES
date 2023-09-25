-- States, see more in step()
WALK = "WALK"
AVOID = "AVOID"
STOP = "STOP"
LEAVE = "LEAVE"
RAB_TAXIS = "RAB_TAXIS"

-- global variables
current_state = WALK -- the current state of the robot
is_obstacle_sensed = false -- is the robot sensing an obstacle?
is_black_sensed = false -- is the robot sensing black?
number_robot_sensed = 0

-- variables for obstacle avoidance
MAX_TURN_STEPS = 20 
current_turn_steps = 0

-- variables for go straight behavior
current_fwd_steps = 0

-- sleeping variables
SLEEP_STEPS = 50 -- we sleep for this number of steps
current_sleep_steps = 0
BASE_LEAVE_PROB = 0.3 -- the basic probability to stay. It should be small enough to avoid splitting the group, but big enough to achieve stability
STOP_PROB = 0.2 
LEAVE_STEPS = 20 -- when leaving we go straight for this number of steps

-- function used to copy two tables
function table.copy(t)
  local t2 = {}
  for k,v in pairs(t) do
    t2[k] = v
  end
  return t2
end

-- the main loop
function step()
   ProcessProx() -- check for obstacles
	robot.range_and_bearing.set_data(1,1) -- send something to the other robots

   -- The default behavior is to go straight.
   -- The robot changes behavior if it senses an obstacle or a black spot
   if current_state == WALK then
		robot.wheels.set_velocity(10,10)
		if is_obstacle_sensed then -- obstacle sensed
		   current_state = AVOID -- change state to avoidance
		   current_turn_steps = robot.random.uniform_int(2,MAX_TURN_STEPS) -- set the number of steps to turn on the spot
		else
			CountRAB()
			if number_robot_sensed > 2 then
				current_state = RAB_TAXIS
			end
		end
	elseif current_state == RAB_TAXIS then
			CountRAB()
			if number_robot_sensed > 2 then
				rab_vect = { x=0, y=0}
				GetRABVect(rab_vect)
				rab_vect_angle = math.atan2(rab_vect.y, rab_vect.x)
				if rab_vect_angle > 0 then
					robot.wheels.set_velocity(0,math.max(0.5,math.cos(rab_vect_angle)) * 10)
				else
					robot.wheels.set_velocity(math.max(0.5,math.cos(rab_vect_angle)) * 10,0)	
				end
			else
				current_state = WALK
			end
			if is_obstacle_sensed then -- obstacle sensed
		   		current_state = AVOID -- change state to avoidance
		   		current_turn_steps = robot.random.uniform_int(2,MAX_TURN_STEPS) -- set the number of steps to turn on the spot
			elseif number_robot_sensed > 4 and robot.random.bernoulli(STOP_PROB) then -- black area sensed, with stop with STOP_PROB probability
				current_state = STOP -- change state
			else 
				prob = BASE_LEAVE_PROB
				if number_robot_sensed ~= 0 then 
					prob = BASE_LEAVE_PROB / math.pow(number_robot_sensed,2)
				end
			
				if robot.random.uniform() > prob then -- stay
					current_state = RAB_TAXIS
				else
					--Leave, stop sending messages to the others
					robot.range_and_bearing.set_data(1,0)
					current_state = LEAVE
					current_sleep_steps = 0
				end
			end
	-- to avoid obstacles, the robot turns on itself for a random number of steps 
   -- between 2 and MAX_TURN_STEPS
   elseif current_state == AVOID then
		robot.wheels.set_velocity(-10,10)
		current_turn_steps = current_turn_steps - 1
		if current_turn_steps <= 0 then
		   current_state = WALK
		end
	-- the robot is stopped: sleep, then count the neighbors and decide whether to leave
	elseif current_state == STOP then
		robot.wheels.set_velocity(0,0)
		current_sleep_steps = current_sleep_steps + 1
		if current_sleep_steps >= SLEEP_STEPS then -- time to decide
			current_sleep_steps = 0
			-- set the probability to leave based on how many robots you see
			CountRAB() -- count the close robots
			prob = BASE_LEAVE_PROB
			if number_robot_sensed ~= 0 then 
				prob = BASE_LEAVE_PROB / math.pow(number_robot_sensed,2)
			end
			
			if robot.random.uniform() > prob then -- stay
				current_state = STOP
			else
				--Leave, stop sending messages to the others
				robot.range_and_bearing.set_data(1,0)
				current_state = LEAVE
				current_sleep_steps = 0
			end
		end
	elseif current_state == LEAVE then -- just leave without checking for ground, only for obstacles
		robot.wheels.set_velocity(10,10)
		current_fwd_steps = current_fwd_steps + 1
		if is_obstacle_sensed then
			state = AVOID
			current_turn_steps = robot.random.uniform_int(2,MAX_TURN_STEPS) -- set the number of steps to turn on the spot
		end
		if current_fwd_steps	> LEAVE_STEPS then
			current_fwd_steps = 0
			current_state = WALK
		end
   end

end

-- Sense obstacles by sorting the proximity sensor values and checking the biggest.
-- If it is bigger than a threshold, then there is an obstacle.
-- We ignore sensors on the back of the robot (abs(angle) < pi/2)
function ProcessProx()
   is_obstacle_sensed = false
   sort_prox = table.copy(robot.proximity)
   table.sort(sort_prox, function(a,b) return a.value>b.value end)
   if sort_prox[1].value > 0.05 and math.abs(sort_prox[1].angle) < math.pi/2
      then is_obstacle_sensed = true
   end
end

-- Count the number of robots sensed close to the robot
function CountRAB()
	number_robot_sensed = 0
	for i = 1, #robot.range_and_bearing do -- for each robot seen
		if robot.range_and_bearing[i].range < 150 and robot.range_and_bearing[i].data[1]== 1 then -- see if they are close enough. What happens if we don't put a distance cutoff here?
			number_robot_sensed = number_robot_sensed + 1 -- increase the counter
		end
	end
end

-- Count the number of robots sensed close to the robot
function GetRABVect(vect)
	for i = 1, #robot.range_and_bearing do -- for each robot seen
		if robot.range_and_bearing[i].range < 150 and robot.range_and_bearing[i].data[1]== 1 then -- see if they are close enough. What happens if we don't put a distance cutoff here?
			x = robot.range_and_bearing[i].range * math.cos(robot.range_and_bearing[i].horizontal_bearing)
			y = robot.range_and_bearing[i].range * math.sin(robot.range_and_bearing[i].horizontal_bearing)
			vect.x = vect.x + x
			vect.y = vect.y + y
		end
	end
end

-- init/reset/destroy
function init()
   current_state = WALK
end
function reset()
	current_state = WALK
	is_obstacle_sensed = false
	is_black_sensed = false
	current_turn_steps = 0
	number_robot_sensed = 0
	current_fwd_steps = 0
	current_sleep_steps = 0
end
function destroy()
end