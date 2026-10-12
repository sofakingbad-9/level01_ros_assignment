import launch
import os
from launch.actions import TimerAction
from launch import LaunchDescription
import launch_ros.actions
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch.substitutions import LaunchConfiguration

def generate_launch_description() -> LaunchDescription:
	lifecycle_nodes= ["map_server","amcl"]
	use_sim_time= True
	pkg_testbed_nav = get_package_share_directory('testbed_navigation')
	
	bringup = IncludeLaunchDescription(
		PythonLaunchDescriptionSource(
		  os.path.join(pkg_testbed_nav, 'launch', 'testbed_full_bringup.launch.py'),
		)
	) 


	
	map_loc=get_package_share_directory("testbed_navigation")+"/maps/testbed_world.yaml"
	amcl_params=get_package_share_directory("testbed_navigation")+"/config/amcl.yaml"
	pointcloud_conv=get_package_share_directory("testbed_navigation")+"/config/pointcloud_conv.yaml"
	start_map_server= launch_ros.actions.Node(
		package="nav2_map_server",
		executable="map_server",
		name="map_server",
		output="screen",
		emulate_tty=True,
		respawn=False,
		respawn_delay=2.0,
		parameters=[
			{'yaml_filename' : map_loc},
		],
	)
	start_lifecycle_manager = TimerAction(
    period=2.0,
    actions=[
				launch_ros.actions.Node(
				package='nav2_lifecycle_manager',
				executable='lifecycle_manager',
				name='lifecycle_manager',
				output='screen',
				emulate_tty=True, 
				respawn=False,
				respawn_delay=2.0,
				
				parameters=[
					  {'use_sim_time': use_sim_time},
					  {'autostart': True},
					  {'node_names': lifecycle_nodes},
					  {'bond_timeout': 0.0},
				],
			)
		]
	)
	
	amcl_launch= launch_ros.actions.Node(
		package='nav2_amcl',
		executable= 'amcl',
		name= 'amcl',
		output="screen",
		emulate_tty=True,
		respawn=False,
		respawn_delay=2.0,
		parameters=[{
			'use_sim_time': use_sim_time,
		  'base_frame_id': "base_footprint",
			'global_frame_id': "map",
		  'laser_model_type': "likelihood_field",
		  'odom_frame_id': "odom",
		  'robot_model_type': "nav2_amcl::DifferentialMotionModel",
		  'scan_topic': "scan2",
		  'set_initial_pose': True,
			'initial_pose':{
		    'x': 0.0,
		    'y': 0.0,
		    'z': 0.0,
		    'yaw': 0.0,
		   },
		 }],
	)
	
	pcl2_to_scan= launch_ros.actions.Node(
		package="pointcloud_to_laserscan",
		executable="pointcloud_to_laserscan_node",
		name="pointcloud_to_laserscan",
		remappings=[('cloud_in', '/ray/pointcloud2'),('scan', '/scan2')],
			
		parameters=[{
			
				'min_height': 0.0,
				'max_height': 1.0,
				'angle_min': -1.5708,  # -M_PI/2
				'angle_max': 1.5708,  # M_PI/2
				'angle_increment': 0.0087,  # M_PI/360.0
				'scan_time': 0.3333,
				'range_min': 0.45,
				'range_max': 20.0,
				'use_inf': True,
				'inf_epsilon': 1.0,
				'use_sim_time': True,
		}],
	)
	
	
	ld= LaunchDescription()
	
	ld.add_action(bringup)
	ld.add_action(start_map_server)
	ld.add_action(amcl_launch)
	ld.add_action(start_lifecycle_manager)
	ld.add_action(pcl2_to_scan)
	
	return ld
	
