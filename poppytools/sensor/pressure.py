import numpy
import serial
import threading

class FootPressure(threading.Thread):
    def __init__(self, port, baudrate = 57600, n_sensors = 5):
        threading.Thread.__init__(self)
        self.daemon = True
        self.s = serial.Serial(port, baudrate)
        self._ns = n_sensors
        self._values = [numpy.nan] * self._n

    @property
    def pressor_values(self):
        return self._values

    def run(self):
        while True:
            try:
                l = self.s.readline()
                # We force this to catch up with any potential lag.
                while self.s.inWaiting():
                    l = self.s.readline()

                l = l.replace('\r\n', '')
                try:
                    ll = map(float, l.split(','))
                    if len(ll) == self._ns:
                        self._values = ll
                except ValueError:
                   pass
            except serial.SerialException:
                self._values = [numpy.nan] * self._ns
