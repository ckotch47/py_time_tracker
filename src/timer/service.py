import datetime
import threading
from time import sleep
from tkinter import StringVar, messagebox
from ..history.service import History, sqlite
from ..yandex.service import login
import calendar
import re


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

    def stop(self, name=None, link=None):
        if name:
            self.name = name
        self.play = False
        if self.timer_s == 0:
            return
        self.history.save(str(self.timer_s), self.name, datetime.datetime.now().isoformat(),
                              link)
        ext_link = re.findall(r'[A-Z]*-[0-9]*', link)
        if len(ext_link) == 0:
            self.timer_s = 0
            self._start_time = 0
            return
        ext_link = ext_link[0]
        try:
            res = login.write_worklog(ext_link, datetime.datetime.now().isoformat(), str(self.timer_s), self.name)
            if res.status_code != 201:
                messagebox.showerror('Not sent into tracker', res.json())
        except Exception as e:
            print(e)
            messagebox.showerror('Not sent into tracker', e)

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
