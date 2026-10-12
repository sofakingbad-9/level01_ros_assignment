import launch
from launch import LaunchDescription
import launch_ros.actions
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description() -> LaunchDescription:
	lifecycle_nodes= ["map_server"]
	use_sim_time= True

	map_loc=get_package_share_directory("testbed_navigation")+"/maps/testbed_world.yaml"
	start_map_server= launch_ros.actions.Node(
		package="nav2_map_server",
		executable="map_server",
		name="map_server",
		output="screen",
		emulate_tty=True,
		parameters=[
			{'yaml_filename' : map_loc},
		],
	)
	start_lifecycle_manager = launch_ros.actions.Node(
	  package='nav2_lifecycle_manager',
	  executable='lifecycle_manager',
	  name='lifecycle_manager',
	  output='screen',
	  emulate_tty=True, 
	  parameters=[
	      {'use_sim_time': use_sim_time},
	      {'autostart': True},
	      {'node_names': lifecycle_nodes},
	  ],
	)
	
	rviz_config_dir = os.path.join(
		launch_ros.substitutions.FindPackageShare(package='testbed_navigation').find('testbed_navigation'),
		'rviz/map_loader_config.rviz')

	rviz_node = launch_ros.actions.Node(
		package='rviz2',
		executable='rviz2',
		name='rviz_node',
		parameters=[{'use_sim_time': True}],
		arguments=[rviz_config_dir]
	)

		
	
	ld= LaunchDescription()
	
	ld.add_action(start_map_server)
	ld.add_action(start_lifecycle_manager)
	ld.a
	
	return ld
	
