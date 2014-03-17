import os
import cv2
import sys
import glob
import time

import PyQt4.QtCore
import PyQt4.QtGui
import PyQt4.uic

import pypot.robot
import pypot.primitive
import pypot.primitive.move as move

import poppytools
from poppytools.configuration.config import poppy_config
from poppytools.primitive.basic import InitRobot, SitPosition, StandPosition
from poppytools.primitive.interaction import ArmsCompliant, ArmsCopyMotion, SmartCompliance
from poppytools.primitive.walking import WalkingGaitFromCPGFile, WalkingGaitFromMat
from poppytools.behavior.idle import HeadOrShake

motor_to_motor = {
    'Head': 'head',
    'Torso': 'torso',
    'Left Arm': 'l_arm',
    'Right Arm': 'r_arm',
    'Left Leg': 'l_leg',
    'Right Leg': 'r_leg',
    }


from numpy import zeros
cv2.namedWindow("poppy")
cv2.imshow("poppy", zeros((10, 10, 3)))
cv2.waitKey(10)



class RecorderApp(PyQt4.QtGui.QApplication):
    def __init__(self, argv):
        PyQt4.QtGui.QApplication.__init__(self, argv)
        self.window =  PyQt4.uic.loadUi('demonstrator.ui')

        self.window.record_button.pressed.connect(self.start_recording)
        self.window.stop_button.pressed.connect(self.stop_recording)
        self.window.play_button.pressed.connect(self.play_move)
        self.window.stop_button_2.pressed.connect(self.stop_move)

        for i in range(len(self.window.motor_group_list)):
            if i in (2, 3):
                continue
            self.window.motor_group_list.item(i).setCheckState(False)

        self.scan_moves()

        cpg_filename = os.path.join(os.path.dirname(poppytools.__file__), 'behavior', 'IROS_Normal_Gait.mat')
        self.poppy = pypot.robot.from_config(poppy_config)
        self.poppy.start_sync()

        self.poppy.attach_primitive(InitRobot(self.poppy), 'init')
        self.poppy.attach_primitive(SmartCompliance(self.poppy, self.poppy.motors ,50), 'smart_compliance')
        self.poppy.attach_primitive(StandPosition(self.poppy), 'stand')
        # self.poppy.attach_primitive(ArmsCompliant(self.poppy, 10), 'arms_compliant')
        self.poppy.attach_primitive(SmartCompliance(self.poppy, self.poppy.arms, 50), 'arms_compliant')
        # self.poppy.attach_primitive(WalkingGaitFromCPGFile(self.poppy), 'walk')
        self.poppy.attach_primitive(WalkingGaitFromMat(self.poppy, cpg_filename, compliant_motion=True), 'walk')
        self.poppy.attach_primitive(ArmsCopyMotion(self.poppy, 50), 'arm_copy')
        self.poppy.attach_primitive(HeadOrShake(self.poppy, 10, 1), 'head_tracking')
        self.poppy.attach_primitive(SitPosition(self.poppy), 'sit_position')

        self.rest = self.poppy.init

        self.rest.start()
        self.rest.wait_to_stop()

        self.mp = []


    def start_recording(self):
        self.window.stop_button.setEnabled(True)
        self.window.record_button.setEnabled(False)

        motors = sum([getattr(self.poppy, name) for name in self.motor_group], [])

        if self.window.compliant_box.checkState():
            self.poppy.attach_primitive(SmartCompliance(self.poppy, motors, 50), 'recorder_compliance')
            self.poppy.recorder_compliance.start()

        time.sleep(0.2)

        self.recorder = move.MoveRecorder(self.poppy, 50, motors)
        self.recorder.start()

    def stop_recording(self):
        self.window.stop_button.setEnabled(False)
        self.window.record_button.setEnabled(True)

        filename = os.path.join('moves', '{}.json'.format(str(self.window.filename_field.text())))
        self.recorder.stop()
        self.recorder.wait_to_stop()

        with open(filename, 'w') as f:
            self.recorder.move.save(f)
        self.scan_moves()

        self.poppy.recorder_compliance.stop()
        self.poppy.recorder_compliance.wait_to_stop()

        del self.poppy.recorder_compliance

        self.rest = self.poppy.init
        self.rest.start()
        self.rest.wait_to_stop()


    def play_move(self):
        names = self.selected_move()
        if not names:
            return

        self.window.stop_button_2.setEnabled(True)
        #self.window.play_button.setEnabled(False)

        for name in names:
            if name == 'walk':
                self.poppy.walk.start()
                continue

            if name == 'smart compliance':
                self.poppy.smart_compliance.start()
                continue

            elif name == 'compliant arms':
                self.poppy.arms_compliant.start()
                continue

            elif name == 'arm copy':
                self.poppy.arm_copy.start()
                continue

            elif name == 'head tracking':
                self.poppy.head_tracking.start()
                continue

            elif name == 'sit':
                self.poppy.sit_position.start()
                self.rest = self.poppy.sit_position
                continue

            elif name == 'stand up':
                self.poppy.stand.start()
                self.rest = self.poppy.stand
                continue

            filename = os.path.join('moves','{}.json'.format(name))
            print filename

            with open(filename, 'r') as f:
                m = move.Move.load(f)

            motion_recorded = move.MovePlayer(self.poppy, m)

            motion_recorded.start()
            self.mp.append(motion_recorded)

    def stop_move(self):
        for motion_recorded in self.mp:
            motion_recorded.stop()
        self.mp = []

        if self.poppy.walk.is_alive():
            self.poppy.walk.stop()

        if self.poppy.arms_compliant.is_alive():
            self.poppy.arms_compliant.stop()

        if self.poppy.arm_copy.is_alive():
            self.poppy.arm_copy.stop()

        if self.poppy.head_tracking.is_alive():
            self.poppy.head_tracking.stop()

        self.window.play_button.setEnabled(True)
        self.window.stop_button_2.setEnabled(False)

        # self.rest.start()
        # self.rest.wait_to_stop()

        time.sleep(0.1)


    @property
    def motor_group(self):
        groups = []
        for i in range(len(self.window.motor_group_list)):
            checkbox = self.window.motor_group_list.item(i)
            if checkbox.checkState() == 2:
                groups.append(motor_to_motor[str(checkbox.text())])
        return groups

    def selected_move(self):
        i = (self.window.move_list.selectedItems())
        if not i:
            return []
        return [ii.text() for ii in i]


    def scan_moves(self):
        names = glob.glob(os.path.join('moves','*.json'))
        names = map(lambda p: os.path.split(p)[1].replace('.json', ''), names)

        names.append('stand up')
        names.append('walk')
        names.append('compliant arms')
        names.append('arm copy')
        names.append('smart compliance')
        names.append('head tracking')
        names.append('sit')

        b = True if names else False
        self.window.move_list.setEnabled(b)
        self.window.loop_box.setEnabled(b)
        self.window.play_button.setEnabled(b)

        if names:
            self.window.move_list.clear()
            for name in names:
                self.window.move_list.addItem(name)

if __name__ == '__main__':
    app = RecorderApp(sys.argv)
    app.window.show()
    sys.exit(app.exec_())
