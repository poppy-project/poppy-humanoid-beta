import os
import time
import numpy

import pypot.primitive
import pypot.primitive.move as move
from pypot.primitive.utils import Sinus

from poppytools.primitive.basic import StandPosition, SitPosition
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
        self.poppy_robot = poppy_robot

    def run(self):
        self.poppy_robot.attach_primitive(ProtectPoppy(self.poppy_robot), 'torque_protection')
        self.poppy_robot.attach_primitive(SmartCompliance(self.poppy_robot,self.poppy_robot.motors,50),'smart_compliance')
        self.poppy_robot.attach_primitive(SmartCompliance(self.poppy_robot,self.poppy_robot.arms,50), 'arms_compliance')
        self.poppy_robot.attach_primitive(StandPosition(self.poppy_robot), 'stand')
        self.poppy_robot.attach_primitive(SitPosition(self.poppy_robot), 'sit')

        for m in self.poppy_robot.motors:
            m.compliant = False


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
        init = InitMove(self.poppy_robot, mvt, duration=2)
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
        self.poppy_robot.torque_protection.stop()
        self.poppy_robot.torque_protection.wait_to_stop()

    def run(self):
        while not(self.should_stop()):
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
        for m in self.poppy_robot.motors:
            m.moving_speed = 0


class WalkingScene(pypot.primitive.LoopPrimitive):
    def __init__(self, poppy_robot, freq=40):
        pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, freq)

        self.poppy_robot = poppy_robot
        self.walking_period = 3.5

    def setup(self):
        self.poppy_robot.smart_compliance.stop()
        self.poppy_robot.smart_compliance.wait_to_stop()

        for m in self.poppy_robot.motors:
            m.compliant = False
            m.torque_limit = 80
            m.moving_speed = 0

        self.poppy_robot.attach_primitive(WalkingGaitFromCPGFile(self.poppy_robot, cycle_period=self.walking_period, gain=1.5), 'air_walk')

        self.body_motion = [
                           Sinus(self.poppy_robot, 40, [self.poppy_robot.l_shoulder_y,], amp=5, freq=1.0/self.walking_period, phase=180),
                           Sinus(self.poppy_robot, 40, [self.poppy_robot.r_shoulder_y,], amp=5, freq=1.0/self.walking_period),
                           Sinus(self.poppy_robot, 40, [self.poppy_robot.l_elbow_y,], amp=10, freq=1.0/self.walking_period, offset=-10, phase=180),
                           Sinus(self.poppy_robot, 40, [self.poppy_robot.r_elbow_y,], amp=10, freq=1.0/self.walking_period, offset=-10),
                           Sinus(self.poppy_robot, 40, [self.poppy_robot.head_z,], amp=10, freq=0.1),
                           Sinus(self.poppy_robot, 40, [self.poppy_robot.head_y,], amp=15, freq=1/10),
                           Sinus(self.poppy_robot, 40, [self.poppy_robot.abs_z,], amp=5, freq=1.0/self.walking_period, phase=180),
                            ]

        self.poppy_robot.stand.start()
        self.poppy_robot.stand.wait_to_stop()

        self.poppy_robot.torque_protection.start()
        self.poppy_robot.air_walk.start()
        for motion in self.body_motion:
            motion.start()

    def update(self):
        pass

    def teardown(self):
        self.poppy_robot.air_walk.stop()
        self.poppy_robot.air_walk.wait_to_stop()
        self.poppy_robot.torque_protection.stop()
        self.poppy_robot.torque_protection.wait_to_stop()

        for m in self.poppy_robot.motors:
            m.moving_speed = 0

        self.poppy_robot.sit.start()

        for motion in self.body_motion:
            motion.stop()
            motion.wait_to_stop()


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
        pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, freq)

        self.poppy_robot = poppy_robot
        self._torque_max = 90


    def setup(self):
        self.poppy_robot.arms_compliance.start()

        self.poppy_robot.stand.start()
        self.poppy_robot.stand.wait_to_stop()


        for m in self.poppy_robot.torso:
            m.torque_limit = 60

        self.torque_limit = 90

    def update(self):
        pass

    def switch_mode(self):
        if self.torque_max > 70:
            self.torque_max = 0
        else:
            self.torque_max = 90

    @property
    def torque_max(self):
        return self._torque_max

    @torque_max.setter
    def torque_max(self, val):
        self._torque_max = val
        for m in self.poppy_robot.legs:
            m.torque_limit = val


    def teardown(self):
        self.poppy_robot.arms_compliance.stop()
        self.poppy_robot.arms_compliance.wait_to_stop()

        self.poppy_robot.smart_compliance.start()




