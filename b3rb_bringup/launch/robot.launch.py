from os import environ
import netifaces as ni
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.actions import ExecuteProcess
from launch.conditions import LaunchConfigurationEquals, IfCondition
from launch_ros.actions import Node

ip = ni.ifaddresses('mlan0')[ni.AF_INET][0]['addr']
print('mlan0: {:s}:4242'.format(ip))

ARGUMENTS = [
    DeclareLaunchArgument('sync', default_value='true',
        choices=['true', 'false'],
        description='Run async or sync SLAM'),
    DeclareLaunchArgument('localization', default_value='slam',
        choices=['off', 'localization', 'slam'],
        description='Whether to run localization or SLAM'),
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
    DeclareLaunchArgument('cam',
        default_value='true',
        choices=['true', 'false'],
        description='Use camera'),
    DeclareLaunchArgument('foxglove',
        default_value='false',
        choices=['true', 'false'],
        description='use foxglove websocket'),
    DeclareLaunchArgument('address', default_value='{:s}'.format(ip),
        description='ip address for foxglove'),
    DeclareLaunchArgument('capabilities', default_value='[clientPublish,services,connectionGraph,assets]',
        description='capabilities for foxglove'),
    DeclareLaunchArgument('topic_whitelist',
        default_value=['["/camera/image_raw/compressed","/camera/camera_info","/cerebri/out/status","/cerebri/out/nav_sat_fix","/global_costmap/costmap","/map","global_costmap/published_footprint","/plan","/robot_description","/tf"]'],
        description='topic_whitelist for foxglove'),
    DeclareLaunchArgument('service_whitelist',
        default_value=['[""]'],
        description='service_whitelist for foxglove'),
    DeclareLaunchArgument('param_whitelist',
        default_value=['[""]'],
        description='param_whitelist for foxglove'),
    DeclareLaunchArgument('send_buffer_limit',
        default_value='10000000',
        description='send_buffer_limit for foxglove in bytes'),
    DeclareLaunchArgument('num_threads',
        default_value='0',
        description='num_threads for foxglove per core'),
    DeclareLaunchArgument('use_compression',
        default_value='false',
        description='use_compression for foxglove'),
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
        launch_arguments=[('use_sim_time', LaunchConfiguration('use_sim_time'))])

    corti = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([PathJoinSubstitution(
        [get_package_share_directory('corti'), 'launch', 'corti.launch.py'])]),
        condition=IfCondition(LaunchConfiguration('corti')),
        launch_arguments=[('use_sim_time', LaunchConfiguration('use_sim_time'))])

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([PathJoinSubstitution(
        [get_package_share_directory(
        'b3rb_nav2'), 'launch', 'slam.launch.py'])]),
        condition=LaunchConfigurationEquals('localization', 'slam'),
        launch_arguments=[('use_sim_time', LaunchConfiguration('use_sim_time')),
            ('sync', LaunchConfiguration('sync'))])

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([PathJoinSubstitution(
        [get_package_share_directory(
        'b3rb_nav2'), 'launch', 'localization.launch.py'])]),
        condition=LaunchConfigurationEquals('localization', 'localization'),
        launch_arguments=[('use_sim_time', LaunchConfiguration('use_sim_time')),
            ('map', PathJoinSubstitution([get_package_share_directory(
                'b3rb_nav2'), 'maps', LaunchConfiguration('map_yaml')]))])

    odom_to_tf = Node(
        condition=IfCondition(LaunchConfiguration('corti')),
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

    foxglove_websockets = IncludeLaunchDescription(
        XMLLaunchDescriptionSource([PathJoinSubstitution(
            [get_package_share_directory('foxglove_bridge'), 'launch', 'foxglove_bridge_launch.xml'])]),
        condition=IfCondition(LaunchConfiguration('foxglove')),
        launch_arguments=[('address', LaunchConfiguration('address')),
                        ('capabilities', LaunchConfiguration('capabilities')),
                        ('topic_whitelist', LaunchConfiguration('topic_whitelist')),
                        ('service_whitelist', LaunchConfiguration('service_whitelist')),
                        ('param_whitelist', LaunchConfiguration('param_whitelist')),
                        ('send_buffer_limit', LaunchConfiguration('send_buffer_limit')),
                        ('num_threads', LaunchConfiguration('num_threads')),
                        ('use_compression', LaunchConfiguration('use_compression')),
                        ('use_sim_time', LaunchConfiguration('use_sim_time'))])

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
        foxglove_websockets,
        slam,
        laser,
        localization,
        odom_to_tf,
        cam,
    ])
