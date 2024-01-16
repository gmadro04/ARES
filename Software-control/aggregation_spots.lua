--[[Aggregation with two spots

The goal of this exercise is to let the robot collectively decide between two black spots and aggregate.
The robots do random walk until the find the black spot, then they stop. With a certain probability they can
start moving again, based on the number of robots sensed. If a robot senses many robots then the probability
to leave is lower than if it senses few robots.
If a robots decides whether to leave every step, the other robots will not have time to go in its same spot.
For this reason a robot "sleeps" for a certain period before deciding whether to leave. 

The values for the number of steps to sleep and the base probability are very important to achieve aggregation.
The behavior could be correct, but it could not work if these values are not set carefully.
]]
-- States, see more in step()
WALK = "WALK"
AVOID = "AVOID"
GO_FWD = "GO_FWD"
STOP = "STOP"
LEAVE = "LEAVE"

-- global variables
current_state = WALK -- the current state of the robot
is_obstacle_sensed = false -- is the robot sensing an obstacle?
is_black_sensed = false -- is the robot sensing black?
number_robot_sensed = 0

-- variables for obstacle avoidance
MAX_TURN_STEPS = 20 
current_turn_steps = 0

-- variables for go straight behavior
FWD_STEPS = 60
current_fwd_steps = 0

-- sleeping variables
SLEEP_STEPS = 200 -- we sleep for this number of steps
current_sleep_steps = 0
BASE_LEAVE_PROB = 0.18 -- the basic probability to stay. It should be small enough to avoid splitting the group, but big enough to achieve stability
LEAVE_STEPS = 50 -- when leaving we go straight for this number of steps

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
	ProcessGround() -- check for black spots	

   -- The default behavior is to go straight.
   -- The robot changes behavior if it senses an obstacle or a black spot
   if current_state == WALK then
		robot.wheels.set_velocity(10,10)
		if is_obstacle_sensed then -- obstacle sensed
		   current_state = AVOID -- change state to avoidance
		   current_turn_steps = math.random(MAX_TURN_STEPS) -- set the number of steps to turn on the spot
		elseif is_black_sensed then -- black area sensed
			current_state = GO_FWD -- change state
			current_fwd_steps = FWD_STEPS -- set the number of steps to go straight
		end
	-- to avoid obstacles, the robot turns on itself for a random number of steps 
   -- between 0 and MAX_TURN_STEPS
   elseif current_state == AVOID then
		robot.wheels.set_velocity(-10,10)
		current_turn_steps = current_turn_steps - 1
		if current_turn_steps <= 0 then
		   current_state = WALK
		end
	-- if the robot is on a black area, it tries to go straight for a bit more in order to avoid
   -- stopping on the border and prevent other robots to enter the spot.
   -- It stops if i) it has gone far enough, ii) it sensed another robot, iii) it is going out on the white
	elseif current_state == GO_FWD then
		current_fwd_steps = current_fwd_steps - 1
		robot.wheels.set_velocity(10,10)
		if current_fwd_steps <= 0 or is_obstacle_sensed or not(is_black_sensed) then
		   current_state = STOP
		end
	-- the robot is stopped: sleep, then count the neighbors and decide whether to leave
	elseif current_state == STOP then
		robot.wheels.set_velocity(0,0)
		robot.range_and_bearing.set_data(1,1) -- send something to the other robots
		current_sleep_steps = current_sleep_steps + 1
		if current_sleep_steps == SLEEP_STEPS then -- time to decide
			current_sleep_steps = 0
			-- set the probability to leave based on how many robots you see
			CountRAB() -- count the close robots	
			prob = BASE_LEAVE_PROB * (number_robot_sensed+1) -- +1 is for this robot
			if robot.random.uniform() < prob then -- stay
				current_state = STOP
			else
				--Leave, stop sending messages to the others
				robot.range_and_bearing.set_data(1,0)
				current_state = LEAVE
			end
		end
	elseif current_state == LEAVE then -- just leave without checking for ground, only for obstacles
		robot.wheels.set_velocity(10,10)
		current_fwd_steps = current_fwd_steps + 1
		if is_obstacle_sensed then
			state = AVOID
			current_turn_steps = math.random(MAX_TURN_STEPS) -- set the number of steps to turn on the spot
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

-- Sense the black spot. If at least one sensor is sensing black, we return true
function ProcessGround()
	is_black_sensed = false
	sort_ground = table.copy(robot.motor_ground)
   table.sort(sort_ground, function(a,b) return a.value<b.value end)
	if sort_ground[1].value == 0 then
		is_black_sensed = true
	end
end

-- Count the number of robots sensed close to the robot
function CountRAB()
	number_robot_sensed = 0
	for i = 1, #robot.range_and_bearing do -- for each robot seen
		if robot.range_and_bearing[i].range < 150 and robot.range_and_bearing[i].data[1]==1 then -- see if they are close enough. What happens if we don't put a distance cutoff here?
			number_robot_sensed = number_robot_sensed + 1 -- increase the counter
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