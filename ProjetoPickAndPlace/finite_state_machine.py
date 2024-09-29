from transitions import Machine
import random
import bank_movements
from test_robot import TestRobot

class MachineRobot:
    states = ['idle', 'pick', 'error', 'retry', 'place', 'finished', 'abort']

    transitions = [
        {'trigger': 'start', 'source': 'idle', 'dest': 'pick'},
        {'trigger': 'fail', 'source': 'pick', 'dest': 'error'},
        {'trigger': 'retry_pick', 'source': 'error', 'dest': 'retry'},
        {'trigger': 'retry_decision', 'source': 'retry', 'dest': 'pick', 'conditions': 'can_retry', 'unless': 'should_abort'},
        {'trigger': 'abort_retry', 'source': 'retry', 'dest': 'abort', 'conditions': 'should_abort'},
        {'trigger': 'success', 'source': 'pick', 'dest': 'place'},
        {'trigger': 'place_success', 'source': 'place', 'dest': 'finished'},
        {'trigger': 'reset', 'source': '*', 'dest': 'idle'}
    ]

    def __init__(self, robot: TestRobot):
        self.attempt = 0
        self.max_attempts = 3
        self.robot = robot
        self.gripper_status = 0  # 0 = gripper aberto, 1 = gripper fechado
        self.machine = Machine(model=self, states=MachineRobot.states, transitions=MachineRobot.transitions, initial='idle')
        
    def can_retry(self) -> bool:
        return self.attempt < self.max_attempts

    def should_abort(self) -> bool:
        return self.attempt >= self.max_attempts

    def start(self): 
        print('Starting...')
        self.robot.connect()
        self.robot.move_joints(bank_movements.BANK_MOVEMENTS_2['home_joint'])
        self.robot.open_tool(2.0)
        self.attempt = 0

    def pick_obj(self):
        print(f'{self.attempt} Attempting to pick the object')

        if self.gripper_status == 1:
            self.robot.open_tool(2.0)
            self.gripper_status = 0
    
        self.robot.move_joints(bank_movements.BANK_MOVEMENTS_2['quadrant_1'])
        self.robot.move_cartesian(bank_movements.BANK_MOVEMENTS_2['front_medicine_1'])
        self.robot.move_cartesian(bank_movements.BANK_MOVEMENTS_2['medicine_1'])
        self.robot.move_cartesian(bank_movements.BANK_MOVEMENTS_2['medicine_1_recoil'])
        self.robot.close_tool(1.0)
        self.gripper_status = 1
    
        # Simula sucesso ou falha
        if self.success_pick():
            print("Sucesso ao pegar o objeto.")
            self.success()
        else:
            print("Falha ao pegar o objeto.")
            self.fail()

    def place_obj(self):
        print('Attempting to place the object')
        self.robot.move_joints(bank_movements.BANK_MOVEMENTS_2['after_recoil'])
        self.robot.move_joints(bank_movements.BANK_MOVEMENTS_2['drop_safe_1'])
        self.robot.move_joints(bank_movements.BANK_MOVEMENTS_2['drop_1'])
        self.robot.open_tool(2.0)
        self.gripper_status = 0
        self.place_success()

    def success_pick(self) -> bool:
        self.success = random.choice([True, False])
        if self.success:
            return True
        else:
            self.attempt += 1
            return False
        
    def retry_decision(self):
        if self.can_retry():
            print(f'Retrying for the {self.attempt} time')
            self.retry_pick()
        else:
            print('Max attempts reached. Aborting..')
            self.abort_retry()

    def finish(self):
        print('Operation finished successfully. Robot disconnected')
        self.robot.disconnect()

    def abort(self):
        print('Operation aborted. Robot disconnected')
        self.robot.disconnect()

while True:
    robot = MachineRobot(TestRobot())
    robot.start()
    
    while True:
        input('Press any key to change state.')
        if robot.state == 'idle':
            robot.start()
            robot.machine.trigger('start')
        elif robot.state == 'pick':
            robot.pick_obj()
        elif robot.state == 'error':
            robot.retry_decision()
        elif robot.state == 'retry':
            robot.retry_decision()
        elif robot.state == 'place':
            robot.place_obj()
        elif robot.state == 'finished':
            robot.finish()
            break
        elif robot.state == 'abort':
            robot.abort()
            break
        input('Press any key to restart.')
        robot.machine.reset()
