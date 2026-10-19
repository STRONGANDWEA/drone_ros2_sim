import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 读URDF
    urdf_file = os.path.join(
        get_package_share_directory('drone_description'),
        'urdf', 'drone.urdf'
    )
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    # 启动Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'),
                         'launch', 'gazebo.launch.py')
        ])
    )

    # 发布robot_description和TF
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc}],
    )

    # 生成模型（从地面z=0.05开始，避免一出生就穿地）
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description',
                   '-entity', 'drone',
                   '-x', '0', '-y', '0', '-z', '0.05'],
        output='screen',
    )

    # 悬停控制器（带参数）
    hover_controller = Node(
        package='drone_control',
        executable='hover_controller',
        parameters=[{
            'target_height': 1.5,
            'mass': 1.62,
            'kp': 25.0,
            'ki': 0.0,
            'kd': 12.0,
        }],
        output='screen',
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        hover_controller,
    ])
