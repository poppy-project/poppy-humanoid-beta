import time
import numpy
import pypot.primitive

from poppytools.primitive.interaction import SmartCompliance



class Spasmes(pypot.primitive.Primitive):
    def __init__(self, poppy_robot, duration):
        pypot.primitive.Primitive.__init__(self, poppy_robot)

        self.poppy_robot = poppy_robot
        self.duration = duration

        if not(hasattr(self.poppy_robot, 'smart_compliance')):
            self.poppy_robot.attach_primitive(SmartCompliance(self.poppy_robot, self.poppy_robot.motors, 50), 'smart_compliance')

    def setup(self):
        self.poppy_robot.smart_compliance.start()

    def run(self):
        self.poppy_robot.smart_compliance.stop()
        self.poppy_robot.smart_compliance.wait_to_stop()

        self.create_spasme()

        time.sleep(self.duration)

        self.poppy_robot.smart_compliance.start()

        time.sleep(1)

    def create_spasme(self):
        for m in self.poppy_robot.motors:
            m.compliant = False

        for m in self.poppy_robot.r_arm + self.poppy_robot.l_arm + self.poppy_robot.head:
            pos = m.present_position + numpy.random.choice([-1,1]) * numpy.random.randint(10,30)
            m.goto_position(pos, self.duration/2)

        for m in self.poppy_robot.l_leg_sagitall + self.poppy_robot.r_leg_sagitall:
            pos = m.present_position + numpy.random.choice([-1,1]) * numpy.random.randint(10,50)
            m.goto_position(pos, self.duration/2)
            #m.goto_position(m.present_position + numpy.random.randint(-30,30),0.3)




