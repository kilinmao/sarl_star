#! /usr/bin/env python

from logging import setLogRecordFactory
import rospy
from std_srvs.srv import Empty, EmptyResponse
from nav_msgs.msg import Odometry
from task_generator.tasks import get_predefined_task

class TaskGenerator:
    def __init__(self):
        mode = rospy.get_param("~task_mode")
        scenerios_json_path = rospy.get_param("~scenerios_json_path")
        paths = {"scenerios_json_path": scenerios_json_path}
        self.task = get_predefined_task(mode, PATHS=paths)

        # if auto_reset is set to true, the task generator will automatically reset the task
        # this can be activated only when the mode set to 'ScenerioTask'
        auto_reset = rospy.get_param("~auto_reset")
        # if the distance between the robot and goal_pos is smaller than this value, task will be reset
        self.delta_ = rospy.get_param("~delta")
        robot_odom_topic_name = rospy.get_param(
            "robot_odom_topic_name", "odom")
        auto_reset = auto_reset and mode == "ScenerioTask"
        self.curr_goal_pos_ = None
        if auto_reset:
            rospy.loginfo(
                "Task Generator is set to auto_reset mode, Task will be automatically reset as the robot approaching the goal_pos")
            self.reset_task()
            self.robot_pos_sub_ = rospy.Subscriber(
                robot_odom_topic_name, Odometry, self.check_robot_pos_callback)
        else:
            # declare new service task_generator, request are handled in callback task generate
            self.task_generator_srv_ = rospy.Service(
                'task_generator', Empty, self.reset_srv_callback)

    def reset_srv_callback(self, req):
        rospy.loginfo("Task Generator received task-reset request!")
        self.task.reset()
        return EmptyResponse()

    def reset_task(self):
        info = self.task.reset()
        if info is not None:
            self.curr_goal_pos_ = info['robot_goal_pos']
        rospy.loginfo("".join(["="]*80))
        rospy.loginfo("goal reached and task reset!")
        rospy.loginfo("".join(["="]*80))

#    def check_robot_pos_callback(self, odom_msg:Odometry):
        def check_robot_pos_callback(self, nav_msgs:Odometry):
        robot_pos = nav_msgs.pose.pose.position
        robot_x = robot_pos.x
        robot_y = robot_pos.y
        goal_x = self.curr_goal_pos_[0]
        goal_y = self.curr_goal_pos_[1]

        if (robot_x-goal_x)**2+(robot_y-goal_y)**2 < self.delta_**2:
            self.reset_task()


if __name__ == '__main__':
    rospy.init_node('task_generator')
    task_generator = TaskGenerator()
    rospy.spin()
