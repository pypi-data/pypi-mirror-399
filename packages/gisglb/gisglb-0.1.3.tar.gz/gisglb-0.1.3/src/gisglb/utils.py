import time
import math


class StopWatch:

    def __init__(self):
        self.__start_time = time.time()
        self.__stop_time = None

    def start(self):
        self.__start_time = time.time()

    def stop(self):
        self.__stop_time = time.time()

    def time_s(self):
        return self.__stop_time - self.__start_time

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.__stop_time == None:
            self.stop()

        time_s = math.floor(self.time_s() * 1000.0) / 1000.0

        return f'{time_s} (s)'
