from collections import deque

import pypot.primitive
from pypot.primitive.utils import Sinus


class UpperBodyIdleMotion(pypot.primitive.LoopPrimitive):
    def __init__(self, poppy_robot, freq):
        pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, freq)

        self.poppy_robot = poppy_robot
        self.body = [
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.abs_z, ], amp=3, freq=0.2),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.abs_z, ], amp=0.8, freq=0.5),

                  Sinus(self.poppy_robot, 50, [self.poppy_robot.l_shoulder_x, ], amp=2, freq=0.2, offset=5),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.l_shoulder_x, ], amp=0.8, freq=0.5),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.r_shoulder_x, ], amp=2, freq=0.2, offset=-5,phase=66),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.r_shoulder_x, ], amp=0.8, freq=0.5, phase=66),

                  Sinus(self.poppy_robot, 50, [self.poppy_robot.l_shoulder_y, ], amp=3, freq=0.2, offset=15),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.l_shoulder_y, ], amp=0.8, freq=0.5),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.r_shoulder_y, ], amp=3, freq=0.1, offset=15, phase=123),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.r_shoulder_y, ], amp=0.8, freq=0.5, phase=123),

                  Sinus(self.poppy_robot, 50, [self.poppy_robot.l_elbow_y, ], amp=2, freq=0.5, offset=-25),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.l_elbow_y, ], amp=0.3, freq=0.2),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.r_elbow_y, ], amp=2, freq=0.5, offset=-25, phase=75),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.r_elbow_y, ], amp=0.3, freq=0.2, phase=75),

                  Sinus(self.poppy_robot, 50, [self.poppy_robot.l_arm_z, ], amp=3, freq=0.2),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.r_arm_z, ], amp=3, freq=0.2, phase=78)
                ]

    def start(self):
        pypot.primitive.LoopPrimitive.start(self)

        for m in self.poppy_robot.torso + self.poppy_robot.arms:
            m.compliant = False

        [all_sinus.start() for all_sinus in self.body]

    def pause(self):
        [all_sinus.pause() for all_sinus in self.body]

    def resume(self):
        [all_sinus.resume() for all_sinus in self.body]

    def stop(self):
        [all_sinus.stop() for all_sinus in self.body]

        pypot.primitive.LoopPrimitive.stop(self)

    def update(self):
        pass


class HeadIdleMotion(pypot.primitive.LoopPrimitive):
    def __init__(self, poppy_robot, freq):
        pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, freq)

        self.poppy_robot = poppy_robot
        self.head = [Sinus(self.poppy_robot, 50, [self.poppy_robot.head_z, ], amp=20, freq=0.05),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.head_z, ], amp=15, freq=0.01),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.head_y, ], amp=20, freq=0.04),
                  Sinus(self.poppy_robot, 50, [self.poppy_robot.head_y, ], amp=5, freq=0.09),
                    ]

    def start(self):
        pypot.primitive.LoopPrimitive.start(self)

        for m in self.poppy_robot.head:
            m.compliant = False

        [all_sinus.start() for all_sinus in self.head]

    def pause(self):
        [all_sinus.pause() for all_sinus in self.head]

    def resume(self):
        [all_sinus.resume() for all_sinus in self.head]

    def stop(self):
        [all_sinus.stop() for all_sinus in self.head]
        pypot.primitive.LoopPrimitive.stop(self)

    def update(self):
        pass

