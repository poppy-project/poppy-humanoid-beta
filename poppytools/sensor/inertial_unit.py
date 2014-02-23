import serial
import threading

class Imu(threading.Thread):
    def __init__(self, port, baudrate = 57600):
        threading.Thread.__init__(self)
        self.daemon = True
        self.s = serial.Serial(port, baudrate)

        self.acc = Vector()
        self.tilt = Vector()
        self.gyro = Vector()
        self.magneto = Vector()

    def run(self):
        while True:
            l = self.s.readline()
            # We force this to catch up with any potential lag.
            while self.s.inWaiting():
                l = self.s.readline()

            l = l.replace('\r\n', '')
            try:
                tilt_val, acc_val, gyro_val, magneto_val = l.split(':')

                self.tilt.x, self.tilt.y, self.tilt.z = map(float, tilt_val.split(','))
                self.acc.x, self.acc.y, self.acc.z = map(float, acc_val.split(','))
                self.gyro.x, self.gyro.y, self.gyro.z = map(float, gyro_val.split(','))
                self.magneto.x, self.magneto.y, self.magneto.z = map(float, magneto_val.split(','))

            except ValueError:
                # Some lines sent by the Arduino just seems incoherent...
                pass


class Vector(object):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    @property
    def json(self):
        return [self.x, self.y, self.z]

    def __repr__(self):
        return '[{}, {}, {}]'.format(self.x, self.y, self.z)
