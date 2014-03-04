import os
import time
import numpy

import pypot.primitive
import pypot.primitive.move as move
from pypot.primitive.utils import Sinus

from poppytools.primitive.basic import StandPosition
from poppytools.primitive.safe import ProtectPoppy
from poppytools.primitive.interaction import SmartCompliance
from poppytools.primitive.walking import WalkingGaitFromCPGFile

GROUND_CHOREGRAPHY_MOVES = ['intro',
        'passage_plage',
        'mvt_sable',
        'passage_dos',
        'mvt_petitpied',
        'mvt_retournement',
        'passage_4pattes',
        '4patte_chute']

class InitScenography(pypot.primitive.Primitive):
    def __init__(self, poppy_robot):
        pypot.primitive.Primitive.__init__(self, poppy_robot)

    def run(self):
        self.poppy_robot.attach_primitive(ProtectPoppy(self.poppy_robot), 'torque_protection')
        self.poppy_robot.attach_primitive(SmartCompliance(self.poppy_robot,self.poppy_robot.motors,50),'smart_compliance')
        self.poppy_robot.attach_primitive(SmartCompliance(self.poppy_robot,self.poppy_robot.arms,50), 'arms_compliance')
        self.poppy_robot.attach_primitive(StandPosition(self.poppy_robot), 'stand')


class InitMove(pypot.primitive.Primitive):
    def __init__(self, poppy_robot, mvt, duration=2):
        pypot.primitive.Primitive.__init__(self, poppy_robot)

        self.poppy_robot = poppy_robot
        self.mvt = mvt
        self.duration = duration

    def run(self):
        self.poppy_robot.goto_position(self.mvt.get_frame(0), self.duration)
        time.sleep(self.duration)

    def teardown(self):
        for m in self.poppy_robot.motors:
            m.moving_speed = 0


class GroundMotionScene(pypot.primitive.Primitive):
    def __init__(self, poppy_robot, move_list=GROUND_CHOREGRAPHY_MOVES, move_path='moves'):
        pypot.primitive.Primitive.__init__(self, poppy_robot)

        self.poppy_robot = poppy_robot
        self.move_list = move_list
        self.move_path = move_path

    def setup(self):
        self.poppy_robot.torque_protection.start()

    def run(self):
        for mvt_name in self.move_list:
            if not(self.should_stop()):
                mvt = self.load_move(mvt_name)
                self.init_motion(mvt)
                self.run_motion(mvt)

    def teardown(self):
        self.poppy_robot.torque_protection.stop()
        self.poppy_robot.torque_protection.wait_to_stop()
        self.poppy_robot.smart_compliance.start()

    def init_motion(self, mvt):
        init = InitMove(self.poppy_robot, mvt, duration=1.5)
        init.start()
        init.wait_to_stop()
        del init

    def run_motion(self,mvt):
        mvt_player = move.MovePlayer(self.poppy_robot, mvt)
        mvt_player.start()
        mvt_player.wait_to_stop()
        del mvt_player

    def load_move(self, mvt_name):
        filename = os.path.join(self.move_path, mvt_name +'.json')

        with open(filename, 'r') as f:
            mvt = move.Move.load(f)

        return mvt


class Spasmes(pypot.primitive.Primitive):
    def __init__(self, poppy_robot, duration, period=4):
        pypot.primitive.Primitive.__init__(self, poppy_robot)

        self.poppy_robot = poppy_robot
        self.duration = duration
        self.period = period


    def setup(self):
        self.poppy_robot.torque_limit_security.stop()
        self.poppy_robot.torque_limit_security.wait_to_stop()

    def run(self):
        while not(self._should_stop()):
            self.create_spasme()
            time.sleep(self.period)

    def create_spasme(self):
        self.poppy_robot.smart_compliance.stop()
        self.poppy_robot.smart_compliance.wait_to_stop()

        for m in self.poppy_robot.motors:
            m.compliant = False

        for m in self.poppy_robot.motors:
            m.torque_limit = 80

        for m in self.poppy_robot.r_arm + self.poppy_robot.l_arm + self.poppy_robot.head:
            pos = m.present_position + numpy.random.choice([-1,1]) * numpy.random.randint(10,30)
            m.goto_position(pos, self.duration/2)

        for m in self.poppy_robot.l_leg_sagitall + self.poppy_robot.r_leg_sagitall:
            pos = m.present_position + numpy.random.choice([-1,1]) * numpy.random.randint(10,50)
            m.goto_position(pos, self.duration/2)

        time.sleep(self.duration)

        self.poppy_robot.smart_compliance.start()

    def teardown(self):
        self.poppy_robot.smart_compliance.start()
        for m in self.motors:
            m.moving_speed = 0


class WalkingScene(pypot.primitive.LoopPrimitive):
    def __init__(self, poppy_robot, freq=40):
        pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, freq)

        self.poppy_robot = poppy_robot

    def setup(self):
        self.walk = WalkingGaitFromCPGFile(self.poppy_robot, cycle_period=3.5, gain=1.5)
        self.body_motion = [
                            Sinus(self.poppy_robot, 40, [self.poppy_robot.l_shoulder_y,], amp=10, freq=0.2),
                            Sinus(self.poppy_robot, 40, [self.poppy_robot.r_shoulder_y,], amp=10, freq=0.2, phase=180),
                            Sinus(self.poppy_robot, 40, [self.poppy_robot.head_z,], amp=10, freq=0.1),
                            Sinus(self.poppy_robot, 40, [self.poppy_robot.head_y,], amp=15, freq=0.12),
                            ]

        for m in self.poppy_robot.motors:
            m.compliant = False
            m.torque_limit = 80
            m.moving_speed = 0

        self.poppy_robot.torque_protection.start()
        self.poppy_robot.walk.start()
        for motion in self.body_motion:
            motion.start()

    def update(self):
        pass

    def teardown(self):
        self.walk.stop()
        self.walk.wait_to_stop()
        del self.walk

        for motion in self.body_motion:
            motion.stop()
            motion.wait_to_stop()
            del motion

        self.sit_posision()


    def sit_posision(self):
        self.robot.l_hip_y.goal_position = -35
        self.robot.r_hip_y.goal_position = -35

        for m in self.poppy_robot.torso + self.poppy_robot.arms:
            m.goal_position = 0

        motor_list = [self.robot.l_knee_y, self.robot.l_ankle_y, self.robot.r_knee_y, self.robot.r_ankle_y]

        for m in motor_list:
            m.compliant = True



MOVES_LEFT = 'ma_left_'
MOVES_RIGHT = 'ml_right_'

class LeapMotion(pypot.primitive.Primitive):
    def __init__(self, poppy_robot, move_path='moves'):
        pypot.primitive.Primitive.__init__(self, poppy_robot)

        self.poppy_robot = poppy_robot
        self.move_path = move_path

    def setup(self):
        self.poppy_robot.torque_protection.start()

    def run(self):

        while not(self.should_stop()):

            if numpy.random.randint(1,4) == 3:
                self.zero_posture()
                continue

            left = self.get_motion(MOVES_LEFT + str(numpy.random.randint(1,10)))
            right = self.get_motion(MOVES_RIGHT + str(numpy.random.randint(1,10)))

            left.start()
            right.start()

            left.wait_to_stop()
            right.wait_to_stop()


    def get_motion(self,mvt_name):
        mvt = self.load_move(mvt_name)
        self.init_motion(mvt)
        return move.MovePlayer(self.poppy_robot, mvt)

    def teardown(self):
        self.zero_posture()
        self.poppy_robot.torque_protection.stop()
        self.poppy_robot.torque_protection.wait_to_stop()

    def zero_posture(self):
        for m in self.poppy_robot.arms:
            m.goto_position(0,2)

        time.sleep(3)

        for m in self.poppy_robot.arms:
            m.moving_speed = 0

    def init_motion(self, mvt):
        init = InitMove(self.poppy_robot, mvt, duration=1)
        init.start()
        init.wait_to_stop()
        del init

    def load_move(self, mvt_name):
        filename = os.path.join(self.move_path, mvt_name +'.json')
        with open(filename, 'r') as f:
            mvt = move.Move.load(f)
        return mvt


class TangoScene(pypot.primitive.LoopPrimitive):
    def __init__(self, poppy_robot, freq=40):
        self.pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, freq)

        self.poppy_robot = poppy_robot
        self._mode = 'COMPLIANT'


    def setup(self):
        self.poppy_robot.stand.start()
        self.poppy_robot.torque_protection.stop()
        self.poppy_robot.torque_protection.wait_to_stop()
        self.poppy_robot.stand.wait_to_stop()

        self.poppy_robot.arms_compliance.start()

        for m in self.poppy_robot.torso:
            m.torque_limit = 60

    def update(self):
        pass

    def switch_mode(self):
        if self._mode == 'COMPLIANT':
            new_val = 90
        else:
            new_val = 0

        for m in self.poppy_robot.legs:
            m.torque_limit = new_val


    def teardown(self):
        self.poppy_robot.arms_compliance.stop()
        self.poppy_robot.arms_compliance.wait_to_stop()

        self.poppy_robot.smart_compliance.start()




