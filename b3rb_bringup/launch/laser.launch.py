import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchContext, LaunchDescription, SomeSubstitutionsType, Substitution
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition, LaunchConfigurationEquals
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('stl27l', default_value='true',
                          choices=['true', 'false'],
                          description='Run STL27L.'),
    DeclareLaunchArgument('use_sim_time', default_value='false',
                          choices=['true', 'false'],
                          description='use_sim_time')
]


def generate_launch_description():

    stl27l_node = Node(
        package='ldlidar_stl_ros2',
        executable='ldlidar_stl_ros2_node',
        output='screen',
        parameters=[
            {'product_name': 'LDLiDAR_STL27L'},
            {'topic_name': 'scan'},
            {'frame_id': 'lidar_link'},
            {'port_name': '/dev/ttymxc2'},
            {'port_baudrate': 921600},
            {'laser_scan_dir': True},
            {'enable_angle_crop_func': False},
            {'enable_box_crop_func': True},
            {'angle_crop_min': 175.0},
            {'angle_crop_max': 210.0},
            {'x_crop_min': -0.30},
            {'x_crop_max': 0.20},
            {'y_crop_min': -0.09},
            {'y_crop_max': 0.09},
            {'bins': 360},
            {'range_min': 0.03},
            {'range_max': 5.0},
            {'pub_rate': 2.0}
            ],
        condition=IfCondition(LaunchConfiguration("stl27l"))
    )

    # Define LaunchDescription variable
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(stl27l_node)
    return ld

