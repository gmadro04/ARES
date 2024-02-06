--[[ PATTERN FORMATION

     o -- o
    / \  / \ 
  o -- o -- o
   \ /  \ /
    o -- o

The goal of this exercise is to let the robot move in order to form an hexagonal pattern.
In order to do this the robots try to position themselves in order to minimize a potential 
field computed using the Lennard-Jones potential. 
Simplifying a lot, the Lennard-Jones potential is a model for the interaction between atoms: 
- if two atoms are too close, they will be subject to a repulsion force, pushing them away one from the other; 
- if they are too far away, they will be subject to an attraction force, pushing them close one to the other; 
- if they are at the right distance, they will be subject to no force, leaving them there; 
This force can be used to let robots move to a position in which the distance between all robots is equal.

The trick is that a robot computes the virtual force "created" by that the other robots seen.

]]
---------------------------------------------------------------------------
-- global variables
TARGET_DIST = 80 -- the target distance between robots, in cm
EPSILON = 50 -- a coefficient to increase the force of the repulsion/attraction function
WHEEL_SPEED = 5 -- max wheel speed
---------------------------------------------------------------------------

---------------------------------------------------------------------------
--Step function
function step()
	 robot.range_and_bearing.set_data(1,1) -- first we send something, to make sure the other robots see us
    target_angle = ProcessRAB_LJ() -- then we compute the angle to follow, using the other robots as input, see function code for details
    speeds = ComputeSpeedFromAngle(target_angle) -- we now compute the wheel speed necessary to go in the direction of the target angle
    robot.wheels.set_velocity(speeds[1],speeds[2]) -- actuate wheels to move
	 robot.range_and_bearing.clear_data() -- forget about all received messages for next step
end
---------------------------------------------------------------------------

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
   desired_angle = math.atan2(sum_vector[2],sum_vector[1]) -- compute the angle from the vector
   --log( "angle: "..desired_angle.." length^2: "..(math.pow(sum_vector[1],2)+math.pow(sum_vector[2],2)) )
   return desired_angle
end
---------------------------------------------------------------------------

---------------------------------------------------------------------------
-- This function take the distance and compute the lennard-jones potential.
-- The parameters are defined at the top of the script
function ComputeLennardJones(distance)
   return -(4*EPSILON/distance * (math.pow(TARGET_DIST/distance,4) - math.pow(TARGET_DIST/distance,2)));
end
---------------------------------------------------------------------------

--nothing to init
function init()
end

--nothing to reset
function reset()
end

--nothing to destroy
function destroy()
end
