from os import environ
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.actions import ExecuteProcess
from launch.conditions import LaunchConfigurationEquals, IfCondition
from launch_ros.actions import Node

ARGUMENTS = [
    DeclareLaunchArgument('nav2', default_value='true',
        choices=['true', 'false'],
        description='Run nav2'),
    DeclareLaunchArgument('corti', default_value='true',
        choices=['true', 'false'],
        description='Run corti'),
    DeclareLaunchArgument('laser', default_value='true',
        choices=['true', 'false'],
        description='Run laser'),
    DeclareLaunchArgument('synapse_ros', default_value='true',
        choices=['true', 'false'],
        description='Run synapse_ros'),
    DeclareLaunchArgument('description', default_value='true',
        choices=['true', 'false'],
        description='Run description'),
    DeclareLaunchArgument('use_sim_time', default_value='false',
        choices=['true', 'false'],
        description='Use sim time'),
    DeclareLaunchArgument('log_level', default_value='error',
        choices=['info', 'warn', 'error'],
        description='log level'),
    DeclareLaunchArgument('cam', default_value='false',
        choices=['true', 'false'],
        description='Use camera'),
    DeclareLaunchArgument('map_yaml', default_value='basic_map.yaml',
        description='Map yaml'),
]

def generate_launch_description():
    synapse_ros = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([PathJoinSubstitution(
            [get_package_share_directory('synapse_ros'), 'launch', 'synapse_ros.launch.py'])]),
        condition=IfCondition(LaunchConfiguration('synapse_ros')),
        launch_arguments=[('host', ['192.0.2.1']),
                          ('port', '4242'),
                          ('use_sim_time', LaunchConfiguration('use_sim_time'))]
    )

    laser = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([PathJoinSubstitution(
            [get_package_share_directory('b3rb_bringup'), 'launch', 'laser.launch.py'])]),
        condition=IfCondition(LaunchConfiguration('laser')),
        launch_arguments=[
            ('stl27l', 'true'),
            ('use_sim_time', LaunchConfiguration('use_sim_time'))
            ]
    )

    # Robot description
    robot_description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([PathJoinSubstitution(
        [get_package_share_directory('b3rb_description'), 'launch', 'robot_description.launch.py'])]),
        condition=IfCondition(LaunchConfiguration('description')),
        launch_arguments=[('use_sim_time', LaunchConfiguration('use_sim_time'))])

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([PathJoinSubstitution(
        [get_package_share_directory(
        'b3rb_nav2'), 'launch', 'nav2.launch.py'])]),
        condition=IfCondition(LaunchConfiguration('nav2')),
        launch_arguments=[('use_sim_time', LaunchConfiguration('use_sim_time')),
                        ('map_yaml', LaunchConfiguration('map_yaml'))])

    corti = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([PathJoinSubstitution(
        [get_package_share_directory('corti'), 'launch', 'corti.launch.py'])]),
        condition=IfCondition(LaunchConfiguration('corti')),
        launch_arguments=[('use_sim_time', LaunchConfiguration('use_sim_time'))])

    odom_to_tf = Node(
        package='corti',
        executable='odom_to_tf',
        output='screen',
        parameters=[{
            'async': False,
            'sync_dt': 0.02,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            }],
        remappings=[
            ('/odom', '/cerebri/out/odometry')
            ])

    cam = IncludeLaunchDescription(
        XMLLaunchDescriptionSource([PathJoinSubstitution(
            [get_package_share_directory('b3rb_bringup'), 'launch', 'ov5645.launch.xml'])]),
        condition=IfCondition(LaunchConfiguration('cam')))

    # Define LaunchDescription variable
    return LaunchDescription(ARGUMENTS + [
        robot_description,
        synapse_ros,
        nav2,
        corti,
        laser,
        odom_to_tf,
        cam,
    ])
