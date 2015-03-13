import math
import numpy

import pypot.primitive


L_FOOT = 0.12
L_HEEL = 0.03
H_FOOT = 0.038
L_LEG = 0.1776
L_THIGH = 0.1813


class SagitallHipMotion(pypot.primitive.Primitive):
    def init(self, robot):
        pypot.primitive.Primitive.__init__(self, robot)

        self._x = 0
        self._y = 0
        self._theta = 0
        self._duration = 1

    def run(self):
        mouv_hip(self.robot, self._x, self._y, self._theta, self.duration)

    def mouv_x(self, value):
        self._x += value
        self.start()

    def mouv_y(self, value):
        self._y += value
        self.start()

    def mouv_theta(self, value):
        self._theta += value
        self.start()

    def set_duration(self, value):
        self._duration = max(value, 0)



def ikin_sagitall_hip(x, y, theta=0):

    y += L_LEG + L_THIGH;

    if math.sqrt(x**2 + y**2) > L_LEG+L_THIGH:
        #print " IK cannot reach the desired target "
        r = math.sqrt(x**2 +y**2)
        alpha_desired = 2 * numpy.arctan( y/(x +r))
        x = (L_LEG + L_THIGH) * numpy.sin(alpha_desired)
        y = (L_LEG + L_THIGH) * numpy.cos(alpha_desired)

    sol_ankle = numpy.real(math.degrees(-2*numpy.arctan(
                (2*L_LEG*x + numpy.lib.scimath.sqrt(- L_LEG**4 + 2*L_LEG**2*L_THIGH**2 + 2*L_LEG**2*x**2
                + 2*L_LEG**2*y**2 - L_THIGH**4 + 2*L_THIGH**2*x**2
                + 2*L_THIGH**2*y**2 - x**4 - 2*x**2*y**2 - y**4))/(L_LEG**2 + 2*L_LEG*y - L_THIGH**2 + x**2 + y**2)
                )));
    sol_knee = numpy.real(math.degrees(2*numpy.arctan(
                numpy.lib.scimath.sqrt(
                (- L_LEG**2 + 2*L_LEG*L_THIGH - L_THIGH**2 + x**2 + y**2)
                *(L_LEG**2 + 2*L_LEG*L_THIGH + L_THIGH**2 - x**2 - y**2))
                /(- L_LEG**2 + 2*L_LEG*L_THIGH - L_THIGH**2 + x**2 + y**2))));



    sol_hip = -1*( sol_ankle + sol_knee) + theta/2.0;
    sol_abs = theta/2.0;

    return numpy.array([sol_ankle, sol_knee, sol_hip, sol_abs])


def mouv_hip(robot, x, y, theta=0, duration=0):
    q = ikin_sagitall_hip(x, y, theta)
    duration = max(duration,0)

    robot.goto_position({'l_ankle_y': q[0],
                        'r_ankle_y': q[0],
                        'l_knee_y': q[1],
                        'r_knee_y': q[1],
                        'l_hip_y': q[2],
                        'r_hip_y': q[2],
                        'abs_y': -q[3]},
                        duration,
                        wait=True)


def ikin_sagitall_toe(x_toe, y_toe, theta=0):
    theta = math.radians(theta);

    x = x_toe - L_FOOT*numpy.cos(theta) - H_FOOT*numpy.sin(theta);
    y = y_toe - (L_LEG+L_THIGH+H_FOOT) + H_FOOT*numpy.cos(theta) - L_FOOT*numpy.sin(theta);

    if math.sqrt(x**2 +y**2) >= (L_LEG+L_THIGH):
        r = math.sqrt(x**2 +y**2)
        alpha = 2 * numpy.arctan( y/(x +r))
        x = r * numpy.cos(alpha)
        y = r * numpy.sin(alpha)

    hip_motor =  numpy.real(- 2*numpy.arctan(
                (2*L_THIGH*x + numpy.lib.scimath.sqrt(- L_LEG**4 + 2*L_LEG**2*L_THIGH**2 + 2*L_LEG**2*x**2 + 2*L_LEG**2*y**2 - L_THIGH**4 + 2*L_THIGH**2*x**2 + 2*L_THIGH**2*y**2 - x**4 - 2*x**2*y**2 - y**4))
                /(- L_LEG**2 + L_THIGH**2 - 2*L_THIGH*y + x**2 + y**2)))
    knee_motor =  numpy.real(2*numpy.arctan(
                numpy.lib.scimath.sqrt((- L_LEG**2 + 2*L_LEG*L_THIGH - L_THIGH**2 + x**2 + y**2)*(L_LEG**2 + 2*L_LEG*L_THIGH + L_THIGH**2 - x**2 - y**2))
                /(- L_LEG**2 + 2*L_LEG*L_THIGH - L_THIGH**2 + x**2 + y**2)))
    ankle_motor = numpy.real(- knee_motor - hip_motor - theta)


    return numpy.degrees(numpy.array([hip_motor, knee_motor, ankle_motor]))

def mouv_left_toe(robot, x, y, theta=0, duration=0, wait=True):
    q = ikin_sagitall_toe(x, y, theta)
    duration = max(duration,0)

    robot.goto_position({'l_ankle_y': q[2],
                        'l_knee_y': q[1],
                        'l_hip_y': q[0]},
                        duration,
                        wait)

def mouv_right_toe(robot, x, y, theta=0, duration=0, wait=True):
    q = ikin_sagitall_toe(x, y, theta)
    duration = max(duration,0)

    robot.goto_position({'r_ankle_y': q[2],
                        'r_knee_y': q[1],
                        'r_hip_y': q[0]},
                        duration,
                        wait)

def sinus(ampl,t,freq=0.5, phase=0, offset=0):
    pi = numpy.pi
    return ampl * numpy.sin(freq * 2.0 * pi * t + phase * pi / 180.0 ) + offset

def cosinus(ampl,t,freq=0.5, phase=0, offset=0):
    pi = numpy.pi
    return ampl * numpy.cos(freq * 2.0 * pi * t + phase * pi / 180.0 ) + offset
