# drone_ros2_sim

ROS 2 Humble 四旋翼无人机仿真：URDF 建模 + Gazebo 物理仿真 + PID 悬停控制。

![Gazebo](https://img.shields.io/badge/Gazebo-Classic%2011-orange)
![ROS2](https://img.shields.io/badge/ROS2-Humble-blue)
![Python](https://img.shields.io/badge/Python-3.10-green)

## 功能

- **drone_description**：四旋翼 URDF 模型（机身、四个机臂、四个电机、前视摄像头）
  - p3d 里程计插件：发布 `/odom`（50Hz）给控制器提供实时高度
  - `libgazebo_ros_force` 施力插件：订阅 `/drone/force` 话题，每帧把推力施加到机身
  - 预配置 RViz 文件，一条命令打开可视化
- **drone_control**：PID 悬停控制器
  - 订阅 `/odom` 读当前高度，发布 `geometry_msgs/Wrench` 到 `/drone/force`
  - 参数可调：`target_height`（目标高度）、`mass`（质量补偿）、`kp/ki/kd`（PID 增益）

无人机生成后自动起飞并悬停在目标高度（默认 1.5m）。

## 环境要求

| 软件 | 版本 |
|---|---|
| Ubuntu | 22.04 (jammy) |
| ROS 2 | Humble |
| Gazebo | Classic 11（随 ros-humble-gazebo-ros-pkgs 安装） |

安装 Gazebo 接口包：

```bash
sudo apt install ros-humble-gazebo-ros-pkgs
```

## 编译

```bash
cd ~/ros_ws
colcon build --packages-select drone_description drone_control
source install/setup.bash
```

## 运行

### 1. 完整仿真（Gazebo + 悬停控制）

```bash
ros2 launch drone_control drone_sim.launch.py
```

无人机在地面生成（z=0.05），约 1 秒后起飞，PID 闭环把高度稳定在 1.5m。

验证：

```bash
ros2 topic echo /odom --once      # 查看当前位置，z 应 ≈ 1.5
ros2 topic hz /drone/force        # 推力话题约 50Hz
```

### 2. 只看模型（RViz）

```bash
ros2 launch drone_description display.launch.py
```

### 3. 只进 Gazebo（不带控制器，无人机因重力落地）

```bash
ros2 launch drone_description gazebo.launch.py
```

## 悬停参数调节

参数在 `drone_control/launch/drone_sim.launch.py` 中：

| 参数 | 默认值 | 说明 |
|---|---|---|
| `target_height` | 1.5 | 目标悬停高度（m） |
| `mass` | 1.62 | 无人机总质量（kg），与 URDF 一致 |
| `kp` | 25.0 | 比例增益（越大越"硬"） |
| `ki` | 0.0 | 积分增益（消除稳态误差） |
| `kd` | 12.0 | 微分增益（抑制振荡） |

运行中可动态修改：

```bash
ros2 param set /hover_controller target_height 2.0
ros2 param set /hover_controller kp 30.0
```

## 技术要点（为什么这样施力）

ROS 1 教程常用的 `gazebo_msgs/ApplyBodyWrench`（`/apply_body_wrench` 服务）在 **ROS 2 Humble 的 gazebo_ros 中并未实现**——服务列表里能看到名字但永远连不上；而新 API `/apply_link_wrench` 服务实测在本环境也"收请求但不施力"。

因此本项目改用**话题施力**方案：在 URDF 中挂载 `libgazebo_ros_force.so` 模型插件，控制器把推力以 `geometry_msgs/Wrench` 发布到 `/drone/force`，插件在每个物理步直接施加，稳定可靠。

## 目录结构

```
src/
├── drone_description/          # 无人机描述包
│   ├── urdf/drone.urdf         # URDF 模型 + gazebo 插件
│   ├── launch/                 # display.launch.py / gazebo.launch.py
│   └── rviz/drone.rviz         # RViz 预配置
└── drone_control/              # 控制包
    ├── drone_control/hover_controller.py   # PID 悬停控制器
    └── launch/drone_sim.launch.py          # 综合仿真入口
```

## 常见问题

- **模型一直躺地上不起飞**：确认启动的是 `drone_sim.launch.py`（带控制器），且 `/drone/force` 有 50Hz 数据（`ros2 topic hz /drone/force`）。
- **悬停高度偏低**：`mass` 参数必须等于 URDF 实际总质量（当前 1.62kg），否则纯 P 控制会有稳态误差。
- **`/odom` 无数据**：确认 URDF 中的 p3d 插件存在且 drone_description 已重新编译。
