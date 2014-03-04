import time
import itertools

import pypot.primitive


class InitRobot(pypot.primitive.Primitive):
    def setup(self):
        return
        
        print 'InitRobot setup', self

        print("initialisation")

        self.robot.compliant = False

        self.robot.power_max()

        # Change PID of Dynamixel MX motors
        for m in filter(lambda m: hasattr(m, 'pid'), self.robot.motors):
            m.pid = (4, 2, 0)

        # Reduce max torque to keep motor temperature low
        for m in self.robot.motors:
            m.torque_limit = 90

        for m in self.robot.torso:
            m.pid = (6, 2, 0)

        time.sleep(1)


class StandPosition(InitRobot):
    def run(self):
        print 'StandPosition run', self

        # Goto to position 0 on all motors
        self.robot.goto_position(dict(zip((m.name for m in self.robot.motors),
                                            itertools.repeat(0))),
                                            2)
        time.sleep(1)
        # Specified some motor positions to keep the robot balanced
        self.robot.goto_position({'r_hip_z': -2,
                                'l_hip_z': 2,
                                'r_hip_x': -2,
                                'l_hip_x': 2,
                                'l_shoulder_x': 10,
                                'r_shoulder_x': -10,
                                'l_shoulder_y': 10,
                                'r_shoulder_y': 10,
                                'l_elbow_y': -20,
                                'r_elbow_y': -20,
                                'l_ankle_y': -0,
                                'r_ankle_y': -0,
                                'abs_y': -3,
                                'head_y': 0,
                                'head_z':0},
                                3,
                                wait=True)

    def teardown(self):
        # Restore the motor speed
        self.robot.power_max()

        # Reduce max torque to keep motor temperature low
        for m in self.robot.motors:
            m.torque_limit = 70


class SitPosition(pypot.primitive.Primitive):
    def run(self):
        self.robot.l_hip_y.goto_position(-35, 2)
        self.robot.r_hip_y.goto_position(-35, 2)
        self.robot.l_knee_y.goto_position(125, 2)
        self.robot.r_knee_y.goto_position(125, 2, wait=True)

        for m in self.robot.torso:
            m.goal_position = 0

        self.robot.abs_y.goal_position = 0

        motor_list = [self.robot.l_knee_y, self.robot.l_ankle_y, self.robot.r_knee_y, self.robot.r_ankle_y]

        for m in motor_list:
            m.compliant = True

        time.sleep(2)

