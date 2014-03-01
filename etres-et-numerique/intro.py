import os
import time

import pypot.primitive
import pypot.primitive.move as move

from poppytools.primitive.interaction import SmartCompliance

MOVES = ['intro',
        'passage_plage',
        'mvt_sable',
        'passage_dos',
        'mvt_petitpied',
        'mvt_retournement',
        'mvt_mainfoetus',
        'passage_4pattes',
        '4patte_chute']


class GroundMotionIntro(pypot.primitive.Primitive):
    def __init__(self, poppy_robot, move_list=MOVES, move_path='moves'):
        pypot.primitive.Primitive.__init__(self, poppy_robot)

        self.poppy_robot = poppy_robot
        self.move_list = move_list
        self.move_path = move_path

    def setup(self):
        self.safe_prim = ProtectPoppy(self.poppy_robot)
        self.start()

    def run(self):
        for mvt_name in self.move_list:
            mvt = self.load_move(mvt_name)
            self.init_motion(mvt)
            self.run_motion(mvt)

    def teardown(self):
        self.safe_prim.stop()
        self.safe_prim.wait_to_stop()
        del self.safe_prim

        self.poppy_robot.attach_primitive(SmartCompliance(self.poppy_robot,50), 'smart_compliance')
        self.poppy_robot.smart_compliance.start()


    def init_motion(self, mvt):
        init = InitMove(self.poppy_robot, mvt)
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

        # print 'torque:', [m.torque_limit for m in self.poppy_robot.motors]

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

