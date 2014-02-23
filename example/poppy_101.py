import pypot.robot

import poppytools.primitive.basic as basic
from poppytools.configuration.config import poppy_config


poppy = pypot.robot.from_config(poppy_config)
poppy.start_sync()

poppy.attach_primitive(basic.StandPosition(poppy), 'stand_position')

poppy.stand_position.start()
poppy.stand_position.wait_to_stop()
