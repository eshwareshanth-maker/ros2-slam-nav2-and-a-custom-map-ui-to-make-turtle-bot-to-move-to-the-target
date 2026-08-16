# ros2-slam-nav2-and-a-custom-map-ui-to-make-turtle-bot-to-move-to-the-target

Here is the complete **README.md** file for your ROS 2 Map and Nav2 Goal UI application, based on the provided source scripts and launch configuration.

---

# ROS 2 Map and Navigation Goal UI

## Overview

This project provides a custom PyQt5-based graphical user interface (GUI) for ROS 2 navigation stacks. It visualizes a live occupancy grid map (`/map`) and robot odometry (`/odom`) while enabling point-and-click goal publishing directly to the Nav2 action server (`/goal_pose`).

---

## Features

* **Live Occupancy Grid Rendering:** Subscribes to `/map` and dynamically renders free spaces, occupied obstacles, and unknown regions in real time using PyQt5 and NumPy.


* **Real-Time Robot Localization:** Tracks and overlays the robot's current position from `/odom` as a distinct marker on the map interface.


* **Interactive Goal Dispatching:** Click anywhere on the map GUI to instantly calculate world coordinates based on map resolution and origin, publishing a Nav2 `PoseStamped` goal to `/goal_pose`.


* **Integrated ROS 2 Spin Loop:** Integrates `rclpy` spinning inside a non-blocking `QTimer` event loop to maintain seamless GUI responsiveness alongside ROS callback queues.



---

## Prerequisites & Dependencies

Ensure your workspace has the following packages and dependencies installed for ROS 2 Humble:

```bash
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup
sudo apt install ros-humble-slam-toolbox
sudo apt install python3-pyqt5 python3-numpy

```

---

## File Structure & Configuration

* **`my_map.pgm` / Map Metadata (`.yaml`)**: Stores occupancy grid layout configuration parameters (resolution, origin coordinates, thresholds).


* **`MapNode`**: Core ROS 2 node handling subscriptions (`/map`, `/odom`) and publisher initialization (`/goal_pose`).


* **`MapWindow`**: PyQt5 widget handling UI sizing, custom coordinate transformations between screen pixels and world meters, mouse click event handling, and custom painting (`paintEvent`).



---

## Quick Start & Execution

1. **Launch Simulation World (e.g., TurtleBot3 Gazebo):**
```bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```[cite: 41]


```


2. **Start SLAM & Navigation Stacks:**
```bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=True
ros2 launch nav2_bringup navigation_launch.py use_sim_time:=True
```[cite: 41]


```


3. **Run the Custom Map & Goal UI Node:**
Execute your Python script containing the PyQt5 interface:
```bash
python3 map_ui.py

```
