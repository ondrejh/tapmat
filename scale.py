#!/usr/bin/python3

from threading import Thread, Lock
from time import sleep


DEFAULT_CALIBRATION = [(123456, 0.0), (1234567, 50.0), (234567, 10.0)]


def line(x, a, b):
    return a[1] + (b[1] - a[1]) / (b[0] - a[0]) * (x - a[0])

def aprox(raw, calib):
    if len(calib) < 1:
        return 0.0
    elif len(calib) == 1:
        return calib[0][1]
    else:
        calib.sort(key=lambda x: x[0])
        if raw < calib[0][0]:
            return line(raw, calib[0], calib[1])
        for i in range(len(calib)-1):
            if raw < calib[i+1][0]:
                return line(raw, calib[i], calib[i+1])
        return line(raw, calib[-2], calib[-1])


class ScaleThread(Thread):

    def __init__(self, ddict, dlock, key='scale', period=0.1):
        Thread.__init__(self)
        self.ddict = ddict
        self.dlock = dlock
        self.key = key
        self.period = period
        self.stopped = False
        with dlock:
            if self.key not in self.ddict:
                self.ddict[key] = {'weight': 0.0, 'raw': 0, 'calib': DEFAULT_CALIBRATION}

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            # measurement here
            with self.dlock:
                scale = self.ddict[self.key]
                scale['weight'] = aprox(scale['raw'], scale['calib'])

            sleep(self.period)
        print('Scale {} has stopped.'.format(self.key))


if __name__ == "__main__":

    testData = dict()
    testLock = Lock()

    scale = ScaleThread(testData, testLock)
    scale.start()

    while True:
        try:
            with testLock:
                print(testData)
            sleep(1.0)
        except KeyboardInterrupt:
            break

    scale.stop()
    scale.join()
