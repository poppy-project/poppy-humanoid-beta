import os
import cv2
import numpy

import pypot.primitive
from scipy.linalg import norm

import poppytools

cascade_folder = os.path.join(os.path.dirname(poppytools.__file__), '..', 'utils', 'haarcascades')
cascade_name = 'haarcascade_frontalface_default.xml'
cascade = os.path.join(cascade_folder, cascade_name)


class HeadTracking(pypot.primitive.LoopPrimitive):
    def __init__(self, poppy_robot, freq, device_name):
        pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, freq)

        self.poppy_robot = poppy_robot
        self.camera = getattr(self.poppy_robot, device_name)
        self.cascade = cv2.CascadeClassifier(cascade)
        self.last_head_pos = (0, 0)
        self.last_head_rect = (0, 0, 0, 0)
        self.tracking = False
        self.move = False
        self.last_track = 0

    def init_loop_primitive(self):
        for m in self.poppy_robot.head:
            m.moving_speed = 10

    def grab_frame(self):
        return self.camera.last_frame

    def update(self):
        img = self.grab_frame()

        if img is None:
            self.tracking = False
            return

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        rects = self.cascade.detectMultiScale(gray,
                                              scaleFactor=1.3,
                                              minNeighbors=4,
                                              minSize=(30, 30),
                                              flags = cv2.CASCADE_SCALE_IMAGE)

        if len(rects) == 0:
            self.tracking = False
            if self.elapsed_time - self.last_track > 20:
                self.poppy_robot.head_y.goal_position = 0
                self.poppy_robot.head_z.goal_position = 0
            return

        rects[:,2:] += rects[:,:2]

        h, w = gray.shape

        pos = [((x1 + x2) / 2, (y1 + y2) / 2) for x1, y1, x2, y2 in rects]
        pos = [(x / float(w), 1 - (y / float(h))) for x, y in pos]
        pos = [(2 * x - 1, 2 * y - 1) for x, y in pos]
        d = [norm(numpy.array(p) - numpy.array(self.last_head_pos)) for p in pos]

        i = numpy.argmin(d)
        x, y = pos[i]
        self.last_head_rect = rects[i]

        if self.move:
            self.poppy_robot.head_y.goal_position = min(max(self.poppy_robot.head_y.present_position + (y * -20), -30), 30)
            self.poppy_robot.head_z.goal_position = min(max(self.poppy_robot.head_z.present_position + (x * -30), -60), 60)
            self.last_track = self.elapsed_time



        self.last_head_pos = (x, y)
        self.tracking = True


class HeadTracking2(pypot.primitive.LoopPrimitive):
    def __init__(self, poppy_robot, freq, device_name):
        pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, freq)

        self.poppy_robot = poppy_robot
        self.camera = getattr(self.poppy_robot, device_name)
        self.cascade = cv2.CascadeClassifier(cascade)
        self.last_head_pos = (0, 0)
        self.last_head_rect = (0, 0, 0, 0)
        self.tracking = False
        self.move = False
        self.last_track = 0

    def init_loop_primitive(self):
        for m in self.poppy_robot.head:
            m.moving_speed = 10

    def grab_frame(self):
        return self.camera.last_frame

    def update(self):
        img = self.grab_frame()

        if img is None:
            self.tracking = False
            return

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        rects = self.cascade.detectMultiScale(gray,
                                              scaleFactor=1.3,
                                              minNeighbors=4,
                                              minSize=(30, 30),
                                              flags = cv2.CASCADE_SCALE_IMAGE)

        if len(rects) == 0:
            self.tracking = False
            # if self.elapsed_time - self.last_track > 20:
            #     self.poppy_robot.head_y.goal_position = 0
            #     self.poppy_robot.head_z.goal_position = 0
            return

        rects[:,2:] += rects[:,:2]

        h, w = gray.shape

        pos = [((x1 + x2) / 2, (y1 + y2) / 2) for x1, y1, x2, y2 in rects]
        pos = [(x / float(w), 1 - (y / float(h))) for x, y in pos]
        pos = [(2 * x - 1, 2 * y - 1) for x, y in pos]
        d = [norm(numpy.array(p) - numpy.array(self.last_head_pos)) for p in pos]

        i = numpy.argmin(d)
        x, y = pos[i]
        self.last_head_rect = rects[i]

        if self.move:
            # print "move"
            self.poppy_robot.head_y.goal_position = min(max(self.poppy_robot.head_y.present_position + (y * -20), -30), 30)
            self.poppy_robot.head_z.goal_position = min(max(self.poppy_robot.head_z.present_position + (x * -30), -60), 60)

            # if self.poppy_robot.head_y.goal_position - (y) *- 20< 0.0:

            #     self.poppy_robot.head_y.goal_position = min(max(self.poppy_robot.head_y.present_position + 1.0, -30), 30)
            # else:
            #     self.poppy_robot.head_y.goal_position = min(max(self.poppy_robot.head_y.present_position - 1.0, -30), 30)



            # if self.poppy_robot.head_z.goal_position - (x) *- 20< 0.0:
            #     self.poppy_robot.head_z.goal_position = min(max(self.poppy_robot.head_z.present_position +1.0, -60), 60)
            # else:
            #     self.poppy_robot.head_z.goal_position = min(max(self.poppy_robot.head_z.present_position - 1.0, -60), 60)

            self.last_track = self.elapsed_time
            print x, y, self.poppy_robot.head_y.goal_position, self.poppy_robot.head_z.goal_position

        self.last_head_pos = (x, y)
        self.tracking = True
