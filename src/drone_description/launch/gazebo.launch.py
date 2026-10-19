import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 1. 读URDF
    urdf_file = os.path.join(
        get_package_share_directory('drone_description'),
        'urdf', 'drone.urdf'
    )
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    # 2. 启动Gazebo空世界
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('gazebo_ros'),
                'launch', 'gazebo.launch.py'
            )
        ])
    )

    # 3. 发布robot_description（让spawn_entity能读到模型）
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc}],
    )

    # 4. 把无人机模型"生"进Gazebo世界
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description',
                   '-entity', 'drone',
                   '-x', '0', '-y', '0', '-z', '5'],
        output='screen',
    )

    return LaunchDescription([gazebo, robot_state_publisher, spawn_entity])
