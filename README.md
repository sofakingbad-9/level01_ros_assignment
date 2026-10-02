# Level-1 ROS Assignment
Name:Adithya Shriram
phn: +91 9043780186
email: adithyashriram06@gmail.com
## Overview

This project implements autonomous navigation for a simulated mobile robot using ROS 2 Humble, Gazebo Classic and Nav2.

The goal was to set up the complete navigation pipeline, including localization, mapping, LiDAR processing, global and local costmaps, path planning, path following and recovery behaviors.

The robot uses a simulated LiDAR for obstacle detection and AMCL for localization. Nav2 is used to generate and follow paths to a goal given through RViz.

## Navigation Pipeline

The overall flow of the system is:

Gazebo LiDAR -> PointCloud2 -> pointcloud_to_laserscan -> LaserScan -> Nav2 costmaps

The global costmap uses the map from the map server along with the LiDAR data to represent the environment.

The planner uses the global costmap to generate a path from the robot's current position to the goal.

The local costmap uses the robot's local surroundings to account for nearby obstacles while following the path.

The controller generates velocity commands which are sent to the Gazebo differential drive plugin through /cmd_vel.

The main navigation flow is:

RViz goal -> BT Navigator -> Planner Server -> Controller Server -> /cmd_vel -> Gazebo

AMCL is responsible for localization and provides the map to odom transform. The robot's odometry provides the odom to base_footprint transform.

The TF chain used by the navigation system is:

map -> odom -> base_footprint -> lidar_link_1

## Main Components

### AMCL

AMCL is used for localization against the static map.

The main frames are:

global frame: map
odom frame: odom
robot base frame: base_footprint

AMCL uses the LaserScan data from /scan2 for localization.

### Map Server

The map server loads the occupancy grid from the map YAML file.

The map YAML references the corresponding PGM image containing the occupancy information.

The /map topic uses transient local QoS so that nodes joining after the map has been published can still receive the map.

### LiDAR

The simulated LiDAR is configured in Gazebo and publishes a PointCloud2 message on:

/ray/pointcloud2 (which was first intentionally kept as /scan)

Nav2's obstacle layer requires LaserScan data in this configuration, so the PointCloud2 is converted using pointcloud_to_laserscan.

The resulting topic is:

/scan2 

The obstacle layers in both the global and local costmaps use /scan2.

### Global Costmap

The global costmap operates in the map frame.

It uses:

global_frame: map
robot_base_frame: base_footprint

The global costmap contains a static layer, obstacle layer and inflation layer.

The static layer uses the map from the map server.

The obstacle layer uses the LiDAR data from /scan2.

The inflation layer adds a safety region around obstacles.

### Local Costmap

The local costmap operates in the odom frame and uses a rolling window around the robot.

It uses:

global_frame: odom
robot_base_frame: base_footprint

The local costmap contains an obstacle layer and inflation layer.

The obstacle layer uses /scan2 to detect nearby obstacles.

### Planner Server

The global planner uses the NavFn planner:

nav2_navfn_planner/NavfnPlanner

The planner uses the global costmap to generate a path to the requested goal.

### Controller Server

The controller uses DWB:

dwb_core::DWBLocalPlanner

The controller follows the global path while taking the local costmap into account.

It publishes velocity commands on:

/cmd_vel

These commands are received by the Gazebo differential drive plugin and used to move the robot.

### Behavior Server

The Behavior Server provides basic navigation behaviors used by the behavior tree.

The configured behaviors include:

Spin
BackUp
DriveOnHeading
Wait

These behaviors are used when the navigation system needs to perform actions such as rotating in place, reversing or waiting.

### BT Navigator

The BT Navigator manages the overall navigation process.

When a goal is given in RViz, the BT Navigator coordinates the planner and controller and can also call recovery behaviors from the Behavior Server.

The Behavior Server needs to be available before the BT Navigator is activated because the behavior tree can depend on action servers such as /spin.

## Launch Configuration

Instead of relying completely on the default Nav2 bringup launch files, the required Nav2 nodes were explicitly launched and configured.

The launch file starts the required components including:

map_server
AMCL
planner_server
controller_server
global_costmap
local_costmap
behavior_server
bt_navigator
pointcloud_to_laserscan
lifecycle_manager

The lifecycle manager is used to configure and activate the lifecycle nodes.

The order of the lifecycle nodes is important. The Behavior Server is started before the BT Navigator so that the required behavior action servers are available when the BT Navigator is configured.

## Parameter Configuration

The Nav2 parameters are stored in:

config/nav2_params.yaml

The parameter file contains separate sections for the different Nav2 nodes.

For example:

planner_server:
  ros__parameters:
    ...

controller_server:
  ros__parameters:
    ...

global_costmap:
  global_costmap:
    ros__parameters:
      ...

local_costmap:
  local_costmap:
    ros__parameters:
      ...

The parameter file is accessed using the package share directory.

The configuration files also need to be installed by the package's CMakeLists.txt so that they are available in the installed package.

One issue encountered during development was that the config directory was not being installed. This meant that the launch file was looking for the parameter file in the install directory but the file was not actually there.

After adding the config directory to the CMake installation rules and rebuilding the workspace, the parameter file was loaded correctly.

## Intentional Issues in the Assignment

The assignment contained several intentionally introduced configuration issues. These were identified and fixed during the setup.

### Missing ament_package()

The testbed_description package was missing:

ament_package()

from its CMakeLists.txt.

This prevented the package from being correctly registered as an ament package.

Adding ament_package() to the CMakeLists.txt fixed the issue.

### Incorrect Map PGM Path

The map YAML file contained an incorrect path to the PGM image.

Because of this, the map server could not correctly load the map.

The path was corrected so that the YAML file pointed to the correct PGM file.

### Map QoS

The /map topic uses transient local QoS.

This is important because the map is published by the map server and nodes such as AMCL may start after the map has already been published.

The map QoS configuration was corrected to use transient local durability so that the map could be received correctly.

### Incorrect LiDAR Topic

The original LiDAR configuration and the navigation configuration did not match.

The simulated LiDAR was publishing PointCloud2 data on:

/ray/pointcloud2

while the navigation stack was expecting LaserScan data.

A pointcloud_to_laserscan node was therefore added.

The resulting data flow is:

/ray/pointcloud2 -> pointcloud_to_laserscan -> /scan2

The Nav2 obstacle layers and AMCL were then configured to use /scan2.

### RViz LaserScan QoS

The RViz LaserScan display had an incompatible QoS configuration for the LaserScan topic.

This prevented RViz from correctly receiving the scan data.

The QoS settings were changed to match the LaserScan publisher.

## Challenges Faced

One of the main challenges was getting all of the Nav2 components to work together rather than debugging them individually.

lifecycle nodes gave me a lot of trouble, with parameter issues, nodes being unconfigured and inactive etc.

There were several issues involving configuration files, package installation, TF and timestamps, QoS settings and Nav2 plugin names.

The planner initially failed to load because the configured NavFn plugin name was different from the plugin name available in the installed Nav2 version.

The configured plugin was:

nav2_navfn_planner::NavfnPlanner

but the installed plugin was:

nav2_navfn_planner/NavfnPlanner

Changing the plugin name allowed the planner to load.

There were also TF timestamp warnings involving the LiDAR and costmaps. The TF chain itself was verified as:

map -> odom -> base_footprint

The costmaps were eventually able to receive the required transforms and sensor data.

Another issue occurred when starting the BT Navigator. It reported that the spin action server was not available.

This was caused by the required behavior server not being available before the BT Navigator was initialized. The behavior server was added to the launch configuration and placed before the BT Navigator in the lifecycle manager's node list.



## Final Result

The final system successfully integrates Gazebo, AMCL, Nav2, LiDAR processing, global and local costmaps, global planning, local control and recovery behaviors.

The robot can receive a goal from RViz, localize itself on the map, generate a path to the goal and use the controller to produce velocity commands for the simulated differential-drive robot.



