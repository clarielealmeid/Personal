from abc import ABC, abstractmethod


class AbstractRobot(ABC):
    """
    This class is an abstract class for the robot. It contains all the methods that the robot should implement.
    This class exists to create a common interface for the robot, so that the robot can be changed without changing
    the rest of the code. Other classes should inherit from this class and implement the methods. These methods are the
    most common methods that the robot should implement.
    """

    @abstractmethod
    def connect(self):
        ...

    @abstractmethod
    def disconnect(self):
        ...

    @abstractmethod
    def request_devices_services(self):
        ...

    @abstractmethod
    def check_movement(self):
        ...

    @abstractmethod
    def move_cartesian(self, pose_list):
        ...

    @abstractmethod
    def move_joints(self, joints_list):
        ...

    @abstractmethod
    def close_tool(self, value):
        ...

    @abstractmethod
    def open_tool(self, value):
        ...

    @abstractmethod
    def emergency_stop(self):
        ...

    @abstractmethod
    def force_error(self):
        ...
        
    @abstractmethod
    def clear_faults(self):
        ...


    