import os
import json

with open(os.path.join(os.path.dirname(__file__), 'poppy_config.json'),'r') as f:
    poppy_config = json.load(f)

