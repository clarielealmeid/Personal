from abstract_robot import AbstractRobot
from time import sleep


class TestRobot:
    """
    
    This class is used to test the robot_api without the need of a real robot and implements basic methods of the AbstractRobot class.
    
    """
    def __init__(self):
        self.error_number = 0

    def connect(self, connection_ip: str = "192.168.2.10"):
        print("using Test Robot")
        print(f'Connecting to robot with IP: {connection_ip}')


    def disconnect(self):
        print('Disconnecting from robot...')
        sleep(0.001)

    def check_movement(self) -> bool:
        print('Robot in motion')
        sleep(0.001)
        return True
    
    def move_cartesian(self, pose_list):
        print(f'Moving cartesian pose to position: {pose_list}')
        sleep(0.001)
        return True

    def move_joints(self, joints_list):
        print(f'Moving joints pose to position: {joints_list}')

        sleep(0.001)
        return True
    
    def close_tool(self, value):
        print(f'Closing tool in {value}')
        sleep(0.001)
        return True
    
    def open_tool(self, value):
        print(f'Opening tool in {value}')
        sleep(0.001)
        return True

    def emergency_stop(self):
        print('Applying emergency stop...')
        sleep(0.001)

    def force_error(self):
        self.error_number += 1
        print('Error detected')
        return True
    
    def clear_faults(self):
        print('Clearing faults...')
        self.error_number = 0
        sleep(0.001)
    
if __name__ == '__main__':

    robot = TestRobot()