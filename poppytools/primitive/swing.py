import numpy

import pypot.robot

from pypot.primitive.utils import Sinus


INIT_POSITION = {'l_ankle_y': 0,
                'l_hip_x': 0,
                'l_hip_y': -90,
                'l_hip_z': 0,
                'l_knee_y': 90,
                'r_ankle_y': 0,
                'r_hip_x': 0,
                'r_hip_y': -90,
                'r_hip_z': 0,
                'r_knee_y': 90,
                'abs_x':  0.0,
                'abs_y': 0.0,
                'abs_z':  0.0,
                'bust_x':  0.0,
                'bust_y': 0.0,
                'head_y':  0.0,
                'head_z':  0.0,
                'l_shoulder_y' : 0 ,
                'r_shoulder_y' : 0 ,
                'l_shoulder_x' : 17 ,
                'r_shoulder_x' : -17 ,
                'l_arm_z' : 62 ,
                'r_arm_z' : -62 ,
                'l_elbow_y' : -145 ,
                'r_elbow_y' : -145
                }

BACK_POSITION = {
                "l_hip_y" : -44 ,
                "r_hip_y" : -44 ,
                "abs_y" : 14 ,
                "abs_x" : 0 ,
                "abs_z" : 0 ,
                "bust_y" : 24 ,
                "bust_x" : 0 ,
                "head_y" : 25 ,
                "l_shoulder_y" : -45 ,
                "r_shoulder_y" : -45 ,
                "l_shoulder_x" : 18 ,
                "r_shoulder_x" : -18 ,
                "l_arm_z" : 13 ,
                "r_arm_z" : -13 ,
                "l_elbow_y" : -84 ,
                "r_elbow_y" : -84 ,
                }

FRONT_POSITION = {
                "l_hip_y" : -97 ,
                "r_hip_y" : -97 ,
                "abs_y" : -14 ,
                "abs_x" : 0 ,
                "abs_z" : 0 ,
                "bust_y" : -2 ,
                "bust_x" : 0 ,
                "head_y" : -3 ,
                "l_shoulder_y" : 15 ,
                "r_shoulder_y" : 15 ,
                "l_shoulder_x" : 16 ,
                "r_shoulder_x" : -8 ,
                "l_arm_z" : 90 ,
                "r_arm_z" : -90 ,
                "l_elbow_y" : -150 ,
                "r_elbow_y" : -150 ,
                }


class SwingPosture(pypot.primitive.Primitive):
    def run(self):
        self.robot.goto_position(INIT_POSITION, 2, wait=True)


class SwingMotionUpperBody(pypot.primitive.LoopPrimitive):
    def __init__(self, poppy_robot, swing_frequency=0.5):
        pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, 30)
        self.poppy_robot = poppy_robot

        self._freq = swing_frequency
        self.motion_period =  1 / (2 * self._freq)

    def update(self):
        s = numpy.cos(self._freq * 2.0 * numpy.pi * self.elapsed_time)

        duration = self.motion_period - ((self.elapsed_time - self.motion_period/2) % self.motion_period)

        if s > 0:
            self.poppy_robot.goto_position(FRONT_POSITION, duration)
        else:
            self.poppy_robot.goto_position(BACK_POSITION, duration)


class SwingMotionLegs(pypot.primitive.LoopPrimitive):
    def __init__(self, poppy_robot, swing_frequency=0.5):
        pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, 10)
        self.poppy_robot = poppy_robot

        amp = 50
        offset = 60

        motors_list = [self.poppy_robot.l_knee_y, self.poppy_robot.r_knee_y]

        self.legs_sinus = [Sinus(self.poppy_robot, 50, motors_list, amp, swing_frequency, offset),
                    ]
                    # Sinus(self.poppy_robot, 50, motors_list, 0.1*amp, 3 * swing_frequency),

    def start(self):
        pypot.primitive.LoopPrimitive.start(self)
        [all_sinus.start() for all_sinus in self.legs_sinus]

    def stop(self):
        [all_sinus.stop() for all_sinus in self.legs_sinus]
        pypot.primitive.LoopPrimitive.stop(self)

    def update(self):
        pass


if __name__ == '__main__':
    import time
    import json
    import pypot.robot

    from poppytools.configuration.config import poppy_config


    poppy = pypot.robot.from_config(poppy_config)
    poppy.start_sync()

    pendulum_frequency = 0.45
    poppy.attach_primitive(SwingPosture(poppy), 'swing_init_position')
    poppy.attach_primitive(SwingMotionUpperBody(poppy, pendulum_frequency), 'upper_body_swing_motion')
    poppy.attach_primitive(SwingMotionLegs(poppy, pendulum_frequency), 'leg_swing_motion')

    # Init robot position
    poppy.compliant = False
    poppy.power_up()

    poppy.swing_init_position.start()
    poppy.swing_init_position.wait_to_stop()
    time.sleep(1)


    poppy.upper_body_swing_motion.start()
    poppy.leg_swing_motion.start()


    i = 0
    while True:
        try:
            time.sleep(1)

            i += 1
            if i == 60 * 3:
                poppy.upper_body_swing_motion.stop()
                poppy.leg_swing_motion.stop()
                poppy.upper_body_swing_motion.wait_to_stop()
                poppy.leg_swing_motion.wait_to_stop()

                poppy.swing_init_position.start()

                i = 0

                time.sleep(2 * 60)

                poppy.power_up()
                poppy.l_arm_z.compliant = True

                time.sleep(1)
                for m in poppy.motors:
                    m.torque_limit = 60

                poppy.upper_body_swing_motion.start()
                poppy.leg_swing_motion.start()

        except KeyboardInterrupt:
            poppy.leg_swing_motion.stop()
            poppy.upper_body_swing_motion.stop()

            poppy.leg_swing_motion.wait_to_stop()
            poppy.upper_body_swing_motion.wait_to_stop()

            poppy.swing_init_position.start()

            time.sleep(2)
            break

