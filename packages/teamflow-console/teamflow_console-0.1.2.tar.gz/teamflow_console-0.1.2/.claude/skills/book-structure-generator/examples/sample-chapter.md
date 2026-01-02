---
title: "Chapter 2: Core Concepts - Physical AI & Humanoid Robotics"
description: "Master the fundamental concepts of Physical AI, including sensors, actuators, and control systems. Learn how these components bridge the digital and physical worlds."
sidebar_label: "Core Concepts"
sidebar_position: 2
slug: /modules/module-1/core-concepts
tags:
  - foundation
  - sensors
  - actuators
  - control-theory
image: /img/modules/module-1/chapter-2-cover.png
last_update:
  date: 2025-12-04
  author: Owais Abdullah
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import ReadDuration from '@site/src/components/ReadDuration';

<ReadDuration />

# Chapter 2: Core Concepts

Physical AI is where code meets reality. Unlike pure software AI, which lives on servers, Physical AI must interact with the messy, unpredictable physical world.

In this chapter, you will learn:
*   **The Feedback Loop:** How robots perceive, think, and act.
*   **Sensors vs. Actuators:** The nervous system and muscles of a robot.
*   **Control Systems:** The math that keeps robots from falling over.

## The Perception-Action Loop

At its heart, every robot operates on a simple loop: **Sense → Plan → Act**.

1.  **Sense:** Gather data from the environment (Camera, Lidar, IMU).
2.  **Plan:** Process data to decide on a course of action (Path planning, Object detection).
3.  **Act:** Execute the decision through motors and hydraulics.

:::info
**Latency Matters:** In a chat bot, a 500ms delay is annoying. In a walking robot, a 500ms delay means falling over. Real-time performance is critical.
:::

## Sensors: The Input Layer

Sensors are the bridge from the physical world to digital data.

### Common Sensor Types

| Sensor Type | Function | Analogous Human Sense |
| :--- | :--- | :--- |
| **Camera** | Visual data (RGB/Depth) | Sight |
| **IMU** | Acceleration & Orientation | Vestibular (Balance) |
| **Lidar** | Distance mapping | (None - distinct to machines) |
| **Microphone** | Audio input | Hearing |

### Code Example: Reading an IMU

Here is how you might read raw data from an Inertial Measurement Unit (IMU) using Python.

```python
import time
from imu_driver import IMU  # Hypothetical driver library

def read_sensor_loop():
    imu = IMU(port='/dev/ttyUSB0')
    imu.connect()
    
    print("Starting sensor loop...")
    try:
        while True:
            # Get 3-axis acceleration and gyroscope data
            accel = imu.get_acceleration() # {x, y, z}
            gyro = imu.get_gyroscope()     # {x, y, z}
            
            print(f"Accel: {accel} | Gyro: {gyro}")
            
            # Control loop frequency (e.g., 100Hz)
            time.sleep(0.01) 
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    read_sensor_loop()
```

## Actuators: The Output Layer

If sensors are the inputs, actuators are the outputs. They convert electrical energy into physical motion.

*   **DC Motors:** Continuous rotation (wheels).
*   **Servos:** Precise angular control (robot arms).
*   **Linear Actuators:** Push/pull motion.

:::warning
**Safety First:** Actuators can exert significant force. Always ensure your software limits (like max torque or velocity) are set correctly before testing on hardware.
:::

## Summary & Next Steps

We've covered the basic anatomy of a Physical AI system: inputs (sensors) and outputs (actuators), connected by a control loop.

In the next chapter, **[Chapter 3: Ecosystem](/modules/module-1/ecosystem)**, we will explore the software tools—like ROS2 and Gazebo—that allow us to build these complex systems without reinventing the wheel.
