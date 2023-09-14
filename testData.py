#!/usr/bin/python3

from threading import Thread, Lock
from time import sleep
from math import sin, pi


class SinGeneratorThread(Thread):
    def __init__(self, ddict, dlock, key='test', amp=1.0, freq=0.05, period=0.1):
        Thread.__init__(self)
        self.ddict = ddict
        self.dlock = dlock
        self.key = key
        self.amp = amp
        self.freq = freq
        self.period = period
        self.time = 0.0
        self.norm = 0.0
        self.stopped = False
        with self.dlock:
            self.ddict[self.key] = {'time': self.time, 'freq': self.freq, 'amp': self.amp, 'period': self.period, 'out': 0.0}

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:

            with self.dlock:
                self.freq = self.ddict[self.key]['freq']
                self.amp = self.ddict[self.key]['amp']

            self.norm += 2*pi*self.period*self.freq
            while self.norm > 2*pi:
                self.norm -= 2*pi
            self.time += self.period

            with self.dlock:
                self.period = self.ddict[self.key]['period']
                self.ddict[self.key]['out'] = self.amp * sin(self.norm)
                self.ddict[self.key]['time'] = self.time

            sleep(self.period)
        print('SinGen {} has stopped.'.format(self.key))


if __name__ == '__main__':

    testDict = dict()
    testLock = Lock()

    testGen = SinGeneratorThread(testDict, testLock)
    testGen.start()

    while True:
        try:
            with testLock:
                print(testDict)
            sleep(0.5)
        except KeyboardInterrupt:
            break

    testGen.stop()
    testGen.join()
