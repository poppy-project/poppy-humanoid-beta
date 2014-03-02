
poppy_config={}

poppy_config['controllers'] = {}

poppy_config['controllers']['lower_body_controller'] = {
    "port": "TODO: Set the good port name",
    "sync_read": True,
    "attached_motors": ["legs"],
}

poppy_config['controllers']['upper_body_controller'] = {
    "port": "TODO: Set the good port name",
    "sync_read": True,
    "attached_motors": ["torso", "head", "arms"],
}

poppy_config['motorgroups'] = {
    "legs": ["l_leg", "r_leg"],
    "l_leg": ["l_hip_x", "l_hip_z", "l_leg_sagitall"],
    "r_leg": ["r_hip_x", "r_hip_z", "r_leg_sagitall"],
    "l_leg_sagitall": ["l_hip_y", "l_knee_y", "l_ankle_y"],
    "r_leg_sagitall": ["r_hip_y", "r_knee_y", "r_ankle_y"],

    "torso": ["abs_y", "abs_x", "abs_z", "bust_y", "bust_x"],
    "head": ["head_z", "head_y"],
    "arms": ["l_arm", "r_arm"],
    "l_arm": ["l_shoulder_y", "l_shoulder_x", "l_arm_z", "l_elbow_y"],
    "r_arm": ["r_shoulder_y", "r_shoulder_x", "r_arm_z", "r_elbow_y"],
}

poppy_config['motors'] = {
    "l_elbow_y": {
      "id": 44,
      "type": "MX-28",
      "orientation": "direct",
      "offset": 0.0,
      "angle_limit": [-140, 0 ],
    },
    "r_elbow_y": {
      "id": 54,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": 0.0,
      "angle_limit": [0, 147 ],
    },
    "r_knee_y": {
      "id": 24,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": 0.0,
      "angle_limit": [-120, 2 ],
    },
    "head_y": {
      "id": 37,
      "type": "AX-12",
      "orientation": "indirect",
      "offset": 10.0,
      "angle_limit": [-40, 8 ],
    },
    "head_z": {
      "id": 36,
      "type": "AX-12",
      "orientation": "direct",
      "offset": 0.0,
      "angle_limit": [-100, 100 ],
    },
    "r_arm_z": {
      "id": 53,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": 0.0,
      "angle_limit": [-90, 90 ],
    },
    "r_ankle_y": {
      "id": 25,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": 0.0,
      "angle_limit": [-70, 25 ],
    },
    "r_shoulder_x": {
      "id": 52,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": 90.0,
      "angle_limit": [-110, 105 ],
    },
    "r_hip_z": {
      "id": 22,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": 0,
      "angle_limit": [-25, 40 ],
    },
    "r_hip_x": {
      "id": 21,
      "type": "MX-28",
      "orientation": "direct",
      "offset": 0.0,
      "angle_limit": [-45, 20 ],
    },
    "r_hip_y": {
      "id": 23,
      "type": "MX-64",
      "orientation": "indirect",
      "offset": 0.0,
      "angle_limit": [-85, 105 ],
    },
    "l_arm_z": {
      "id": 43,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": 0.0,
      "angle_limit": [-90, 90 ],
    },
    "l_hip_x": {
      "id": 11,
      "type": "MX-28",
      "orientation": "direct",
      "offset": 0.0,
      "angle_limit": [-22, 45 ],
    },
    "l_hip_y": {
      "id": 13,
      "type": "MX-64",
      "orientation": "direct",
      "offset": 2.0,
      "angle_limit": [-105, 85 ],
    },
    "l_hip_z": {
      "id": 12,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": 0,
      "angle_limit": [-40, 25 ],
    },
    "abs_x": {
      "id": 32,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": 0.0,
      "angle_limit": [-45, 45 ],
    },
    "abs_y": {
      "id": 31,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": 0.0,
      "angle_limit": [-37, 16 ],
    },
    "abs_z": {
      "id": 33,
      "type": "MX-28",
      "orientation": "direct",
      "offset": 0.0,
      "angle_limit": [-80, 80 ],
    },
    "l_ankle_y": {
      "id": 15,
      "type": "MX-28",
      "orientation": "direct",
      "offset": 0.0,
      "angle_limit": [-35, 70 ],
    },
    "bust_y": {
      "id": 34,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": 0.0,
      "angle_limit": [-46, 23 ],
    },
    "bust_x": {
      "id": 35,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": 0.0,
      "angle_limit": [-40, 40 ],
    },
    "l_knee_y": {
      "id": 14,
      "type": "MX-28",
      "orientation": "direct",
      "offset": 0.0,
      "angle_limit": [-2, 120 ],
    },
    "l_shoulder_x": {
      "id": 42,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": -90.0,
      "angle_limit": [-105, 110 ],
    },
    "l_shoulder_y": {
      "id": 41,
      "type": "MX-28",
      "orientation": "direct",
      "offset": 90,
      "angle_limit": [-140, 155 ],
    },
    "r_shoulder_y": {
      "id": 51,
      "type": "MX-28",
      "orientation": "indirect",
      "offset": 90,
      "angle_limit": [-155, 140 ],
    },
}

if __name__ == '__main__':
    '''
    You can easily generate the configuration file for your Poppy by specifying the 2 serial ports of the USB2AX dongles.
    Then execute this script. It will produce the poppy_config file needed to create the robot using this command:

    import json
    import pypot.robot
    poppy_config = json.load(path/poppy_config.json)
    poppy = pypot.robot.from_config(poppy_config)

    '''
    import json
    poppy_config['controllers']['lower_body_controller']['port'] = "COM31"
    poppy_config['controllers']['upper_body_controller']['port'] = "COM9"

    with open('poppy_config.json','w') as f:
        json.dump(poppy_config, f, indent=2)

