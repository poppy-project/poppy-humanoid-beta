import json

import pypot.robot

import poppytools.primitive.basic as basic

with open('../poppytools/configuration/poppy_config.json','r') as f:
    poppy_config = json.load(f)


poppy = pypot.robot.from_config(poppy_config)
poppy.start_sync()

poppy.attach_primitive(basic.StandPosition(poppy), 'stand_position')

poppy.stand_position.start()
poppy.stand_position.wait_to_stop()
