#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Wrench, Vector3


class HoverController(Node):
    def __init__(self):
        super().__init__('hover_controller')

        # ===== 参数（第6课）：运行中可以改 =====
        self.declare_parameter('target_height', 1.5)   # 目标悬停高度（米）
        self.declare_parameter('mass', 1.0)            # 无人机质量（千克）
        self.declare_parameter('kp', 25.0)             # PID比例增益
        self.declare_parameter('ki', 0.0)              # PID积分增益
        self.declare_parameter('kd', 12.0)             # PID微分增益

        # ===== 内部状态 =====
        self.current_z = 0.0
        self.last_error = 0.0
        self.integral = 0.0
        self.dt = 0.02  # 控制周期20ms（50Hz）

        # ===== 订阅：拿当前高度（第4课 话题）=====
        self.create_subscription(Odometry, '/odom', self.odom_cb, 10)

        # ===== 施力：发布 Wrench 到 /drone/force（gazebo_ros_force 插件持续施力）=====
        self.force_pub = self.create_publisher(Wrench, '/drone/force', 10)

        # ===== 定时器：50Hz 控制循环（第2课 节点零件）=====
        self.create_timer(self.dt, self.control_loop)
        self.get_logger().info('悬停控制器已启动，目标高度 %.1f 米' %
                               self.get_parameter('target_height').value)

    def odom_cb(self, msg):
        """收到odom就更新当前高度"""
        self.current_z = msg.pose.pose.position.z

    def control_loop(self):
        """50Hz执行：算PID → 施力"""
        target = self.get_parameter('target_height').value
        mass = self.get_parameter('mass').value
        kp = self.get_parameter('kp').value
        ki = self.get_parameter('ki').value
        kd = self.get_parameter('kd').value

        # PID计算
        error = target - self.current_z
        self.integral += error * self.dt
        derivative = (error - self.last_error) / self.dt
        self.last_error = error

        # 推力 = 重力补偿 + PID修正
        thrust = mass * 9.81 + kp * error + ki * self.integral + kd * derivative
        thrust = max(0.0, thrust)  # 推力不能为负（不能往下推自己）

        # 发布推力到插件话题（插件在每个仿真步持续施加）
        msg = Wrench()
        msg.force = Vector3(x=0.0, y=0.0, z=thrust)
        msg.torque = Vector3(x=0.0, y=0.0, z=0.0)
        self.force_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = HoverController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
