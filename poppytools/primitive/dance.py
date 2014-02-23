import numpy

import pypot.primitive

def sinus(ampl,t,freq=0.5, phase=0, offset=0):
    pi = numpy.pi
    return ampl * numpy.sin(freq * 2.0 * pi * t + phase * pi / 180.0 ) + offset


class SimpleBodyBeats(pypot.primitive.LoopPrimitive):
    '''
    Simple primitive to make Poppy shake its booty following a given beat rate in bpm.

    '''
    def __init__(self, poppy_robot, bpm, motion_amplitude=10):
        pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, 50)

        self.poppy_robot = poppy_robot
        self._bpm = bpm
        self.amplitude = motion_amplitude
        self.frequency = bpm / 60.0
        self.pi = numpy.pi


        for m in self.poppy_robot.motors:
            m.moving_speed = 50.0


    def update(self):
        t = self.elapsed_time
        amp = self._amplitude
        freq = self.frequency

        self.poppy_robot.head_y.goal_position = sinus(amp / 2.0, t, freq)
        self.poppy_robot.head_z.goal_position = sinus(amp / 2.0, t, freq / 2.0)

        self.poppy_robot.bust_x.goal_position = sinus(amp / 6.0, t, freq / 2.0) + sinus(amp / 6.0, t, freq / 4.0)
        self.poppy_robot.abs_x.goal_position = - sinus(amp / 8.0, t, freq / 4.0) + sinus(amp / 6.0, t, freq / 4.0)

        self.poppy_robot.l_shoulder_y.goal_position = sinus(amp / 3.0, t, freq / 2.0)
        self.poppy_robot.r_shoulder_y.goal_position = - sinus(amp / 3.0, t, freq / 2.0)

        self.poppy_robot.r_elbow_y.goal_position = sinus(amp / 2.0, t, freq, offset=-20)
        self.poppy_robot.l_elbow_y.goal_position = sinus(amp / 2.0, t, freq / 2.0, offset=-20)


    @property
    def bpm(self):
        return self._bpm

    @bpm.setter
    def bpm(self, new_bpm):
        '''
        Permits to change the beat rate while the motion is performing
        '''
        self._bpm = new_bpm
        self.frequency = self._bpm / 60.0

    @property
    def amplitude(self):
        return self._amplitude

    @amplitude.setter
    def amplitude(self, new_amp):
        self._amplitude = new_amp


if __name__ == '__main__':
    import time
    import pypot.robot

    from poppytools.configuration.config import poppy_config
    from poppytools.primitive.basic import StandPosition

    # create the robot from the configuration file
    poppy = pypot.robot.from_config(poppy_config)
    poppy.start_sync()

    # Init robot position
    poppy.attach_primitive(StandPosition(poppy),'stand')
    poppy.stand.start()
    poppy.stand.wait_to_stop()

    # Create dancing primitive
    bpm = 100
    poppy.attach_primitive(SimpleBodyBeats(poppy, bpm), 'beats' )
    poppy.beats.start()

    while True:
        try:
            time.sleep(1)

        except KeyboardInterrupt:
            poppy.beats.stop()
            poppy.stand.start()
            poppy.stand.wait_to_stop()
            break
