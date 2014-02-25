import cv2
import numpy

import pypot.primitive
from collections import deque


from poppytools.primitive.idle import UpperBodyIdleMotion, HeadIdleMotion
from poppytools.sensor.vision import PSEyeCamera
from poppytools.primitive.tracking import HeadTracking
from poppytools.primitive.interaction import ArmsTurnCompliant

class HeadOrShake(pypot.primitive.LoopPrimitive):
    def __init__(self, poppy_robot, freq, camera_id):
        pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, freq)

        self.poppy_robot = poppy_robot
        self.camera_id = camera_id
        self.freq = freq
        self.mode = 'head_idle'

    def start(self):
        self.poppy_robot._camera = PSEyeCamera(self.camera_id)
        self.poppy_robot._head_tracking = HeadTracking(self.poppy_robot, self.freq, '_camera')
        self.poppy_robot._breathing = UpperBodyIdleMotion(self.poppy_robot, self.freq)
        self.poppy_robot._head_motion = HeadIdleMotion(self.poppy_robot, self.freq)
        self.poppy_robot._arm_interaction = ArmsTurnCompliant(self.poppy_robot, self.freq)
        self.track = deque([False], 2 * self.freq)

        self.poppy_robot._camera.start()
        self.poppy_robot._head_tracking.start()
        self.poppy_robot._breathing.start()
        self.poppy_robot._head_motion.start()
        self.poppy_robot._arm_interaction.start()

        pypot.primitive.LoopPrimitive.start(self)

        self.mode = 'head_idle'

    def stop(self):
        self.poppy_robot._head_tracking.stop()
        self.poppy_robot._head_tracking.wait_to_stop()
        self.poppy_robot._breathing.stop()
        self.poppy_robot._breathing.wait_to_stop()
        self.poppy_robot._head_motion.stop()
        self.poppy_robot._head_motion.wait_to_stop()
        self.poppy_robot._arm_interaction.stop()
        self.poppy_robot._arm_interaction.wait_to_stop()

        del self.poppy_robot._head_tracking
        del self.poppy_robot._camera
        del self.poppy_robot._breathing
        del self.poppy_robot._head_motion
        del self.poppy_robot._arm_interaction

        pypot.primitive.LoopPrimitive.stop(self)

    def switch_mode(self):
        if self.mode == 'head_idle':
            self.mode = 'tracking'
            self.poppy_robot._head_motion.stop()
            self.poppy_robot._head_motion.wait_to_stop()
            self.poppy_robot._head_tracking.move = True

        else:
            self.mode = 'head_idle'
            self.poppy_robot._head_tracking.move = False
            self.poppy_robot._head_motion.start()

    def update(self):
        img = self.poppy_robot._camera.last_frame

        if img is not None:
            self.track.append(self.poppy_robot._head_tracking.tracking)

            x1, y1, x2, y2 = self.poppy_robot._head_tracking.last_head_rect
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0))

            cv2.imshow("poppy", img.copy())
            cv2.waitKey(1)

        if self.mode == 'tracking' and numpy.mean(self.track) < 0.1:
            self.switch_mode()

        if self.mode == 'head_idle' and self.track[-1]:
            self.switch_mode()

        #print self.mode, self.poppy_robot._head_tracking.move

    def pause(self):
        self.poppy_robot._camera.pause()
        self.poppy_robot._head_tracking.pause()

        pypot.primitive.LoopPrimitive.pause(self)

    def resume(self):
        self.poppy_robot._camera.resume()
        self.poppy_robot._head_tracking.resume()

        pypot.primitive.LoopPrimitive.resume(self)
