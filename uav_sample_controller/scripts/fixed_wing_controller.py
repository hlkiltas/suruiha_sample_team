#!/usr/bin/env python
import roslib

roslib.load_manifest('uav_sample_controller')
import rospy

from geometry_msgs.msg import Twist, Pose
from suruiha_gazebo_plugins.srv import AirTraffic
from suruiha_gazebo_plugins.msg import UAVMessage
from suruiha_gazebo_plugins.msg import UAVSensorMessage
from uav_sample_controller.air_traffic_manager import AirTrafficManager
from uav_sample_controller.zephyr_controller import ZephyrController
from uav_sample_controller.task_planner import TaskPlanner
from uav_sample_controller.comm_manager import CommManager
from uav_sample_controller.sensor_manager import SensorManager


if __name__ == "__main__":
    rospy.init_node('fixed_wing_controller', anonymous=True)
    uav_name = rospy.get_param('~name')

    # connect to air traffic controller
    rospy.logdebug('waiting for /air_traffic_control service')
    rospy.wait_for_service('/air_traffic_control')
    rospy.logdebug('/air_traffic_control service is ready')
    air_traffic_service = rospy.ServiceProxy('/air_traffic_control', AirTraffic)
    air_manager = AirTrafficManager(air_traffic_service, uav_name)

    pose_topic_name = rospy.get_param('~pose')
    control_topic_name = rospy.get_param('~control')
    rospy.logdebug("topic names are set as pose_topic_name:" + pose_topic_name + " control_topic_name:" + control_topic_name)
    control_pub = rospy.Publisher(control_topic_name, Twist, queue_size=1)

    zephyr_controller = ZephyrController(control_pub, air_manager)
    rospy.Subscriber(pose_topic_name, Pose, zephyr_controller.pose_callback)

    comm_manager = CommManager(rospy, uav_name, zephyr_controller)
    sensor_manager = SensorManager(rospy)

    task_planner = TaskPlanner(zephyr_controller, sensor_manager)

    # how many times in a second the control loop is going to run
    ros_rate = rospy.Rate(20)
    while not rospy.is_shutdown():
        # air_manager.step()
        # comm_manager.step()
        task_planner.step()

        # share the latest pose of the uav with other uavs
        comm_manager.publish_pose()
        # uav_controller.step()
        ros_rate.sleep()

        # print 'current throttle:', str(throttle), ' pitch:', str(pitch), ' roll:', str(roll)
        # control_cmd = Twist()
        # control_cmd.linear.z = throttle  # for iris quadrotor
        # control_cmd.linear.x = throttle  # for zephyr fixeed wing
        # control_cmd.angular.y = pitch
        # control_cmd.angular.x = roll
        # pub.publish(control_cmd)
