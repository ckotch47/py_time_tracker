import datetime
import threading
from time import sleep
from tkinter import StringVar
from ..history.service import History
import calendar


class Timer:
    thread = None

    def __init__(self, root_frame):
        self.name = None
        self.root_frame = root_frame
        self.history = History(root_frame)
        self._start_time = None
        self.play = False

        self.timer_s = 0
        self.time = StringVar()
        self.time.set(str(datetime.timedelta(seconds=0)))

    def start(self):
        while self.play:
            self.timer_s += 1
            self.time.set(str(datetime.timedelta(seconds=self.timer_s)))
            sleep(1)

    def stop(self, name=None):
        if name:
            self.name = name
        self.play = False
        if self.timer_s != 0:
            self.history.save(str(self.timer_s), self.name, calendar.timegm(datetime.datetime.now().utctimetuple()))
        self.timer_s = 0
        self._start_time = 0

    def loop(self, name: str = '1'):
        if self.play:
            return
        self.name = name
        self.play = True
        self._start_time = datetime.datetime
        self.thread = threading.Thread(target=self.start)
        self.thread.start()
