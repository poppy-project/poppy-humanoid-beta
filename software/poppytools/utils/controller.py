import numpy

import pypot.primitive


from operator import attrgetter

from pypot.utils import attrsetter



class PIDController(pypot.primitive.LoopPrimitive):
    def __init__(self, robot,
                 target, feedback, action,
                 p_gain=4, i_gain=0, d_gain=0,
                 max_i = 500):

        pypot.primitive.LoopPrimitive.__init__(self, robot, freq=50)

        self.p_gain = p_gain
        self.i_gain = i_gain
        self.d_gain = d_gain
        self.max_i = max_i

        self._pid_order = 0
        self._current_error = 0
        self._cumulative_error = 0

        self.target = target
        self.feedback = feedback
        self.action = action

    def update(self):

        self._current_error = self.target - self.feedback

        self._pid_order = self.proportional_controller() + \
                          self.integral_controller() + \
                          self.derivative_controller()

        self._action(self._pid_order)


    # MARK: PID Functions
    def proportional_controller(self):
        return  self.p_gain * self._current_error

    def integral_controller(self):
        self._cumulative_error += self._current_error * self._period

        if self.i_gain > 0 :
            if abs(self._cumulative_error) > self.max_i:
                self._cumulative_error = numpy.sign(self._cumulative_error) * self.max_i

        return self.i_gain * self._cumulative_error

    def derivative_controller(self):
        return self.d_gain * self._current_error / float(self._period)


    # MARK: Property
    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, new_target):
        self.clear_error()
        self._target = new_target

    @property
    def feedback(self):
        return self._feedback()

    @feedback.setter
    def feedback(self, new_feedback):
        self._feedback_input = new_feedback
        self._feedback = lambda: attrgetter(self._feedback_input)(self.robot)

    @property
    def action(self):
        return self._pid_order

    @action.setter
    def action(self, new_action):
        self._action_output = new_action
        self._action = lambda x: attrsetter(self._action_output)(self.robot, x)

    def clear_error(self):
        self._cumulative_error = 0



