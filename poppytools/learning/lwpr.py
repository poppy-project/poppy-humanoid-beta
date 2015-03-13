import time
import numpy

# package available here: http://wcms.inf.ed.ac.uk/ipab/slmc/research/software-lwpr
import lwpr

import pypot.primitive

class LWPR_Learning(pypot.primitive.LoopPrimitive):
    def __init__(self, poppy_robot, learning_primitive, training_duration=120):
        pypot.primitive.LoopPrimitive.__init__(self, poppy_robot, freq=50)

        self.learning_primitive = learning_primitive
        self.learning_primitive.start()
        self.training_duration = training_duration
        self.first = True
        self.n_train = 0
        self.explored_action_space = []
        self.mse = 0
        self.exploration_duration = 30

    def update(self):
        pypot.primitive.LoopPrimitive.update()

        if self.first:
            self.init_learning()
            self.first = False
            self.poppy_robot.data_recording.start()

        self.info_learning(50*20)
        self.train_model()
        self.use_learned_model()


    def init_learning(self):
        for m in self.poppy_robot.torso:
            m.torque_limit = 50
            m.pid = (3,1,0)

        # Creation du model
        n_state_space = numpy.size(self.get_state_space())
        n_action_space = numpy.size(self.get_action_space())
        self.model = lwpr.LWPR(n_state_space, n_action_space)

        # Initialisation des valeurs
        self.model.init_D = 20 * numpy.eye(n_state_space)
        self.model.norm_in = self.explore_state_space_range(self.exploration_duration)
        self.model.init_alpha = numpy.ones([n_state_space,n_state_space])
        self.model.meta = True
        self.model.update_D = True
        self.model.diag_only = True
        self.model.penalty = 0.0001


    def train_model(self):
        self.current_state_space = self.get_state_space()
        self.current_action_space = self.get_action_space()
        self.action_predicted = self.model.update(self.current_state_space, self.current_action_space)

        self.current_mse = (self.current_action_space - self.action_predicted)**2
        self.mse = self.mse + self.current_mse
        self.n_train +=1

        self.explored_action_space.append(self.current_action_space)


    def use_learned_model(self):

        values = self.model.predict(self.get_state_space())

        if self.elapsed_time > self.training_duration+self.exploration_duration:
            for m in self.poppy_robot.torso:
                m.torque_limit = 80

            self.set_action_space(values)
            self.action = values
        else:
            self.action = values * 0

    def info_learning(self, max_train_set):
        if self.n_train > max_train_set:
            self.current_learning()
            self.n_train = 0
            self.explored_action_space = []

    def current_learning(self):
        nMSE = self.mse/self.n_train/numpy.var(numpy.array(self.explored_action_space), axis=0)
        print '#Data: {} #RFs: {} nMSE={}'.format(self.model.n_data, self.model.num_rfs, nMSE)
        #print "#Data: %5i  #RFs: %3i  nMSE=%5.3f" %(self.model.n_data, self.model.num_rfs, nMSE)

    def explore_state_space_range(self, duration):
        t0 = time.time()

        data = []
        while (time.time() - t0) < duration:
            data.append(self.get_state_space())
            time.sleep(0.02)

        self.exploration_data = numpy.array(data)
        self.range_state_space = 1.1 * numpy.ceil(numpy.max(numpy.array(data), axis=0) - numpy.min(numpy.array(data), axis=0))
        return self.range_state_space

    # State/Action Space
    def get_state_space(self):
        return self.learning_primitive.state_space

    def get_action_space(self):
        return self.learning_primitive.action_space

    def set_action_space(self, values):
        self.learning_primitive.action_space = values


