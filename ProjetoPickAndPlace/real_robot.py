import sys
import os
import time
import threading
from kortex_api.autogen.messages import Base_pb2
from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from abstract_robot import AbstractRobot
from connect_robot import RobotConnection
from time import sleep


class RealRobot(AbstractRobot):
    
    def __init__(self):
        self.error_number = 0
        self.device = None
        self.base = None
        self.action = None
        self.force_error = False
        self.attempts = 0

    def connect(self, connection_ip: str = "192.168.2.10"):
        self.device = RobotConnection.create_tcp_connection(connection_ip)
        self.device.connect()
        self.request_devices_services()

    def disconnect(self):
        if self.device is None:
            return
        self.device.disconnect()

    def request_devices_services(self) -> None:
        """
        Creates a connection to request services from the following devices:
        Base, BaseCyclic, Gripper, DeviceConfig

        Returns:
            None
        """
        self.base = self.device.get_base_client()
        self.base_cyclic = self.device.get_base_cyclic_client()
        self.gripper = self.device.get_gripper_cyclic_client()
        self.device_config = self.device.get_device_config_client()

    def check_movement(self) -> bool:
        """
        Sends the action request to robot's base to execute the movement.

        """
        e = threading.Event()
        self.trajectory_info = []
        self.action_finished = True
        notification_handle = self.base.OnNotificationActionTopic(
            self.check_for_end_or_abort(e),
            Base_pb2.NotificationOptions()
        )

        try:
            self.base.ExecuteAction(self.action)
        except (Exception,) as e:
            print("Detection move executing action exception", e)
            return False

        finished = e.wait(RealRobot.TIMEOUT)

        self.action_finished &= finished

        try:
            self.base.Unsubscribe(notification_handle)
        except (Exception,) as e:
            print("Couldn't unsubscribe the base - ", e)

        if not self.action_finished:
            return False

        self.action_finished &= self.check_action_end_reason()

        return True

    def move_cartesian(self, pose_list: list[float]) -> bool:

        self.action = Base_pb2.Action()
        self.action.name = "Example Cartesian action movement"
        self.action.application_data = ""

        cartesian_pose = self.action.reach_pose.target_pose
        cartesian_pose.x = pose_list[0]  # [meters]
        cartesian_pose.y = pose_list[1]  # [meters]
        cartesian_pose.z = pose_list[2]  # [meters]
        cartesian_pose.theta_x = pose_list[3]  # [degrees]
        cartesian_pose.theta_y = pose_list[4]  # [degrees]
        cartesian_pose.theta_z = pose_list[5]  # [degrees]

        finished = self.check_movement()

        return finished

    
    def move_joints(self, joints_list: list[float]) -> bool:
        self.action = Base_pb2.Action()
        self.action.name = "Angular action movement"
        self.action.application_data = ""
        
        for joint_id in range(len(joints_list)):
            joint_angle = self.action.reach_joint_angles.joint_angles.joint_angles.add()
            joint_angle.joint_identifier = joint_id
            joint_angle.value = joints_list[joint_id]
           
            
        finished = self.check_movement()

        return finished
   
    def close_tool(self, value):
        # Create the GripperCommand we will send
        gripper_command = Base_pb2.GripperCommand()
        finger = gripper_command.gripper.finger.add() 
        gripper_command.mode = Base_pb2.GRIPPER_POSITION
        finger.finger_identifier = 1
        finger.value = 1
        self.base.SendGripperCommand(gripper_command)

    
    def open_tool(self, value):
        # Create the GripperCommand we will send
        gripper_command = Base_pb2.GripperCommand()
        finger = gripper_command.gripper.finger.add()
        gripper_command.mode = Base_pb2.GRIPPER_POSITION
        finger.finger_identifier = 1
        finger.value = 0
        self.base.SendGripperCommand(gripper_command)

    
    def emergency_stop(self):
        self.base.ApplyEmergencyStop()

    def force_error(self):
        if self.force_error == False:
            self.force_error = True
        
        return self.force_error
 
    def clear_faults(self):
        self.base.ClearFaults()
        if self.force_error == True:
            self.force_error = False

    
if __name__ == '__main__':

    robot = RealRobot()