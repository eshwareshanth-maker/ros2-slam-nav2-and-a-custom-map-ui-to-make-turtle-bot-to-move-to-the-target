#!/usr/bin/env python3

import sys
import numpy as np

import rclpy
from rclpy.node import Node

from nav_msgs.msg import (
    OccupancyGrid,
    Odometry
)

from geometry_msgs.msg import PoseStamped

from PyQt5.QtWidgets import (
    QApplication,
    QWidget
)

from PyQt5.QtGui import (
    QPainter,
    QImage,
    QColor
)

from PyQt5.QtCore import (
    Qt,
    QTimer
)


class MapNode(Node):

    def __init__(self, ui):

        super().__init__("map_goal_ui")

        self.ui = ui

        self.map_msg = None
        self.map_img = None

        self.robot_x = 0.0
        self.robot_y = 0.0

        self.goal_x = None
        self.goal_y = None

        # -----------------------------
        # SUBSCRIBE MAP
        # -----------------------------
        self.create_subscription(
            OccupancyGrid,
            "/map",
            self.map_callback,
            10
        )

        # -----------------------------
        # SUBSCRIBE ODOM
        # -----------------------------
        self.create_subscription(
            Odometry,
            "/odom",
            self.odom_callback,
            10
        )

        # -----------------------------
        # GOAL PUBLISHER
        # -----------------------------
        self.goal_pub = self.create_publisher(
            PoseStamped,
            "/goal_pose",
            10
        )

        print("Map Goal UI Started")


    # ==========================================
    # MAP CALLBACK
    # ==========================================
    def map_callback(self, msg):

        self.map_msg = msg

        w = msg.info.width
        h = msg.info.height

        if w == 0 or h == 0:
            return

        arr = np.array(
            msg.data,
            dtype=np.int16
        )

        arr = arr.reshape(h, w)

        img = np.zeros(
            (h, w),
            dtype=np.uint8
        )

        # Unknown
        img[arr == -1] = 127

        # Free
        img[arr == 0] = 255

        # Occupied
        img[arr > 50] = 0

        # Flip vertically
        img = np.flipud(img)

        self.map_img = img

        self.ui.update()


    # ==========================================
    # ODOM CALLBACK
    # ==========================================
    def odom_callback(self, msg):

        self.robot_x = (
            msg.pose.pose.position.x
        )

        self.robot_y = (
            msg.pose.pose.position.y
        )

        self.ui.update()


    # ==========================================
    # SEND NAV2 GOAL
    # ==========================================
    def send_goal(self, px, py):

        if self.map_msg is None:
            return

        info = self.map_msg.info

        py = info.height - py

        x_world = (
            info.origin.position.x
            + px * info.resolution
        )

        y_world = (
            info.origin.position.y
            + py * info.resolution
        )

        self.goal_x = x_world
        self.goal_y = y_world

        goal = PoseStamped()

        goal.header.frame_id = "map"

        goal.pose.position.x = x_world
        goal.pose.position.y = y_world

        goal.pose.orientation.w = 1.0

        self.goal_pub.publish(goal)

        print(
            "\nGOAL SENT"
        )

        print(
            "X:",
            x_world
        )

        print(
            "Y:",
            y_world
        )

        self.ui.update()


# ======================================================
# UI WINDOW
# ======================================================
class MapWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.node = None

        self.setWindowTitle(
            "ROS2 NAV2 MAP UI"
        )

        self.resize(
            900,
            900
        )


    # ==========================================
    # DRAW EVERYTHING
    # ==========================================
    def paintEvent(self, event):

        if self.node is None:
            return

        if self.node.map_img is None:
            return

        painter = QPainter(self)

        img = self.node.map_img

        h, w = img.shape

        # IMPORTANT FIX
        img = np.ascontiguousarray(img)

        qimg = QImage(
            img.tobytes(),
            w,
            h,
            w,
            QImage.Format_Grayscale8
        )

        # Draw map
        painter.drawImage(
            self.rect(),
            qimg
        )

        if self.node.map_msg is None:
            return

        info = self.node.map_msg.info

        # ==========================================
        # DRAW ROBOT
        # ==========================================
        rx = self.node.robot_x
        ry = self.node.robot_y

        mx = int(
            (
                rx
                - info.origin.position.x
            )
            / info.resolution
        )

        my = int(
            (
                ry
                - info.origin.position.y
            )
            / info.resolution
        )

        my = info.height - my

        screen_x = int(
            mx
            * self.width()
            / info.width
        )

        screen_y = int(
            my
            * self.height()
            / info.height
        )

        painter.setBrush(
            QColor(255, 0, 0)
        )

        painter.drawEllipse(
            screen_x - 6,
            screen_y - 6,
            12,
            12
        )

        # ==========================================
        # DRAW GOAL
        # ==========================================
        if self.node.goal_x is not None:

            gx = self.node.goal_x
            gy = self.node.goal_y

            gmx = int(
                (
                    gx
                    - info.origin.position.x
                )
                / info.resolution
            )

            gmy = int(
                (
                    gy
                    - info.origin.position.y
                )
                / info.resolution
            )

            gmy = info.height - gmy

            gsx = int(
                gmx
                * self.width()
                / info.width
            )

            gsy = int(
                gmy
                * self.height()
                / info.height
            )

            painter.setBrush(
                QColor(0, 255, 0)
            )

            painter.drawEllipse(
                gsx - 6,
                gsy - 6,
                12,
                12
            )


    # ==========================================
    # MOUSE CLICK
    # ==========================================
    def mousePressEvent(self, event):

        if self.node is None:
            return

        if self.node.map_msg is None:
            return

        info = self.node.map_msg.info

        mx = int(
            event.x()
            * info.width
            / self.width()
        )

        my = int(
            event.y()
            * info.height
            / self.height()
        )

        self.node.send_goal(
            mx,
            my
        )


# ======================================================
# MAIN
# ======================================================
def main():

    rclpy.init()

    app = QApplication(
        sys.argv
    )

    window = MapWindow()

    node = MapNode(window)

    window.node = node

    # ==========================================
    # ROS2 SPIN TIMER
    # ==========================================
    timer = QTimer()

    timer.timeout.connect(
        lambda:
        rclpy.spin_once(
            node,
            timeout_sec=0
        )
    )

    timer.start(50)

    window.show()

    sys.exit(
        app.exec_()
    )


if __name__ == "__main__":
    main()