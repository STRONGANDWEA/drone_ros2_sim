import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # 找到urdf文件的路径
    urdf_file = os.path.join(
        get_package_share_directory('drone_description'),
        'urdf', 'drone.urdf'
    )
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    # 找到rviz配置文件（预先配好Fixed Frame和RobotModel，避免每次手动设置）
    rviz_config = os.path.join(
        get_package_share_directory('drone_description'),
        'rviz', 'drone.rviz'
    )

    return LaunchDescription([
        # 1. 读取URDF，发布每个link的TF（把URDF变成TF树）
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}],
        ),
        # 2. 发布关节状态（无人机都是fixed，这个节点只是占位）
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
        ),
        # 3. 打开rviz可视化（-d 加载预配置：Fixed Frame=base_link + RobotModel）
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
        ),
    ])
