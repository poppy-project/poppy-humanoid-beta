import os
import time

import pypot.primitive

TORQUE_MIN = 20
TORQUE_MAX = 95
MAX_ERROR = 10

class ProtectPoppy(pypot.primitive.LoopPrimitive):
    def __init__(self, poppy_robot, freq=20):
        pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, freq)
        self.poppy_robot = poppy_robot

    def update(self):
        for m in self.poppy_robot.motors:
            self.adjust_torque(m)

    def adjust_torque(self, motor):
        target = motor.goal_position
        pos = motor.present_position
        dist = abs(target - pos)

        if dist > MAX_ERROR:
            motor.torque_limit = TORQUE_MAX
        else:
            motor.torque_limit = TORQUE_MIN + dist/MAX_ERROR * (TORQUE_MAX - TORQUE_MIN)


    def teardown(self):
        for m in self.poppy_robot.motors:
            m.torque_limit = TORQUE_MAX
