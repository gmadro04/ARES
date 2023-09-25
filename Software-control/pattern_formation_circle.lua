---------------------------------------------------------------------------
-- global variables
TARGET_DIST = 80 -- the target distance between robots, in cm
EPSILON = 50 -- a coefficient to increase the force of the repulsion/attraction function
WHEEL_SPEED = 5 -- max wheel speed
---------------------------------------------------------------------------

---------------------------------------------------------------------------
--Step function
function step()
	robot.colored_blob_omnidirectional_camera.enable()
	robot.range_and_bearing.set_data(1,1) -- first we send something, to make sure the other robots see us
  lj_vector = ProcessRAB_LJ() -- then we compute the angle to follow, using the other robots as input, see function code for details
	global_vector = ComputeVectorForGlobalPotential() -- we compute the global potential
	total_vector = {0,0}
	total_vector[1] = lj_vector[1] + global_vector[1] -- we sum the local and global forces
	total_vector[2] = lj_vector[2] + global_vector[2]
	target_angle = math.atan2(total_vector[2],total_vector[1]) -- compute the angle from the vector
  speeds = ComputeSpeedFromAngle(target_angle) -- we now compute the wheel speed necessary to go in the direction of the target angle
  robot.wheels.set_velocity(speeds[1],speeds[2]) -- actuate wheels to move
	robot.range_and_bearing.clear_data() -- forget about all received messages for next step
end
---------------------------------------------------------------------------

function ComputeVectorForGlobalPotential()
   global_vector = {0,0}
	if (#robot.colored_blob_omnidirectional_camera > 0) then
		potentialStrength = ComputeGlobalPotential(robot.colored_blob_omnidirectional_camera[1].distance)
  	global_vector[1] = math.cos( robot.colored_blob_omnidirectional_camera[1].angle )*potentialStrength 
  	global_vector[2] = math.sin( robot.colored_blob_omnidirectional_camera[1].angle )*potentialStrength -- sum the y component
	end
	return global_vector   
end

---------------------------------------------------------------------------
--This function computes the necessary wheel speed to go in the direction of the desired angle.
function ComputeSpeedFromAngle(angle)
    dotProduct = 0.0;
    KProp = 20;
    wheelsDistance = 0.14;

    -- if the target angle is behind the robot, we just rotate, no forward motion
    if angle > math.pi/2 or angle < -math.pi/2 then
        dotProduct = 0.0;
    else
    -- else, we compute the projection of the forward motion vector with the desired angle
        forwardVector = {math.cos(0), math.sin(0)}
        targetVector = {math.cos(angle), math.sin(angle)}
        dotProduct = forwardVector[1]*targetVector[1]+forwardVector[2]*targetVector[2]
    end

	 -- the angular velocity component is the desired angle scaled linearly
    angularVelocity = KProp * angle;
    -- the final wheel speeds are compute combining the forward and angular velocities, with different signs for the left and right wheel.
    speeds = {dotProduct * WHEEL_SPEED - angularVelocity * wheelsDistance, dotProduct * WHEEL_SPEED + angularVelocity * wheelsDistance}

    return speeds
end
---------------------------------------------------------------------------

---------------------------------------------------------------------------
-- In this function, we take all distances of the other robots and apply the lennard-jones potential.
-- We then sum all these vectors to obtain the final angle to follow in order to go to the place with the minimal potential
function ProcessRAB_LJ()

   sum_vector = {0,0}
   for i = 1,#robot.range_and_bearing do -- for each robot seen
      lj_value = ComputeLennardJones(robot.range_and_bearing[i].range) -- compute the lennard-jones value
      sum_vector[1] = sum_vector[1] + math.cos(robot.range_and_bearing[i].horizontal_bearing)*lj_value -- sum the x components of the vectors
      sum_vector[2] = sum_vector[2] + math.sin(robot.range_and_bearing[i].horizontal_bearing)*lj_value -- sum the y components of the vectors
   end
	return sum_vector
end
---------------------------------------------------------------------------

---------------------------------------------------------------------------
-- This function take the distance and compute the lennard-jones potential.
-- The parameters are defined at the top of the script
function ComputeLennardJones(distance)
   return -(4*EPSILON/distance * (math.pow(TARGET_DIST/distance,4) - math.pow(TARGET_DIST/distance,2)));
end
---------------------------------------------------------------------------

---------------------------------------------------------------------------
-- This function computes the global potential.
-- In this case the global potential is simply the distance to the center of the arena
function ComputeGlobalPotential(distance)
   return distance;
end


--nothing to init
function init()
	reset()
end

--nothing to reset
function reset()
	robot.colored_blob_omnidirectional_camera.enable()
end

--nothing to destroy
function destroy()
end