cmake_minimum_required(VERSION 3.8)
project(drone_description)

find_package(ament_cmake REQUIRED)

# 安装 urdf、launch、rviz 目录到 install/drone_description/share/...
install(DIRECTORY urdf launch rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
