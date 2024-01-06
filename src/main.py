import sys
from babel.numbers import *
from tkinter import *
from tkinter import messagebox, ttk

import pystray
from PIL import Image
from pystray import MenuItem as item

from .statistic.service_v2 import StatisticV2
from .timer.service import Timer
from .settings.service import Settings, sqlite
from .yandex.service import login
from .statistic.service import Statistic
from .sqlite.service import get_path
from .file.service import path, folder
from .issue.service import IssueGui

# from .history.service import History

def get_right_click() -> str:
    if sys.platform == 'darwin':
        return "<Button-2>"
    else:
        return "<Button-3>"


class PystrayIcon:
    show = False
    title = "pytimetracker"
    icon = 'time'
    image = Image.open(f"{path}/{folder}/time.png")

    def __init__(self, root_frame, timer):
        try:
            self.icon = sqlite.get_icon_black_or_white()[1]
            self.image = Image.open(f"{path}/{folder}/{self.icon}.png")
        except:
            pass

        if sys.platform == 'linux':
            return None
        self.menu = (item('Show time tracker', self.show_window), item('Close', self.quit_window))
        self.icon = pystray.Icon("name", self.image, "title", self.menu)
        self.root_frame = root_frame
        self.timer = timer
        self.icon.run_detached()

    def quit_window(self, item):
        self.show_window(item)
        if not self.timer.play:
            if sys.platform != 'linux':
                self.icon.stop()
            self.root_frame.after(2, self.root_frame.destroy)
        else:
            messagebox.showerror('error', 'Please stop timer')

    def show_window(self, item):
        if not self.show:
            self.root_frame.deiconify()
        else:
            self.root_frame.withdraw()
            self.root_frame.deiconify()


class WMain:
    overrideredirect = False
    settings_gui = Settings()
    statistics_gui = Statistic()
    statistic_v2 = StatisticV2()
    title = "Time"
    show = True

    def __init__(self):

        self.menuBar = None
        self.w_main = Tk()
        # self.w_main.bind("<Unmap>", self.minimize)
        self.timer = Timer(self.w_main)
        self.s_tray_icon = PystrayIcon(self.w_main, self.timer)
        self.w_main.overrideredirect(self.overrideredirect)
        self.w_main.title(self.title)
        self.w_main.geometry(f"360x96+{self.w_main.winfo_screenwidth() - 360}+0")
        self.w_main.resizable(True, True)
        self.w_main.columnconfigure(0, weight=1)
        self.w_main.rowconfigure(3, weight=2)


        self.issue_gui = IssueGui()

        from src.update.service import check_last_releases
        check_last_releases()
    def on_closing(self):
        if not self.timer.play:
            self.w_main.destroy()
        else:
            messagebox.showerror('error', 'Please stop timer')

    def revert_overrideredirect(self) -> bool:
        if self.overrideredirect:
            self.overrideredirect = False
        else:
            self.overrideredirect = True
        return self.overrideredirect

    def menu(self):
        m = Menu(self.w_main, tearoff=0)
        m.add_command(label="Overrideredirect",
                      command=lambda: [self.w_main.overrideredirect(self.revert_overrideredirect())])

        m.add_command(label='Statistics', command=lambda: [self.statistics_gui.init(self.w_main)])
        m.add_command(label='Statistics V2', command=lambda: [self.statistic_v2.show(self.w_main)])
        m.add_command(label='Issue', command=lambda: [self.issue_gui.init(self.w_main)])
        m.add_command(label='Settings', command=lambda: [self.settings_gui.init(self.w_main)])

        # m.add_command(label="Exit", command=lambda: [self.on_closing()])

        def do_popup(event):
            try:
                m.tk_popup(event.x_root, event.y_root)
            finally:
                try:
                    m.grab_release()
                except:
                    pass

        self.w_main.bind(f"{get_right_click()}", do_popup)

    def top_level_menu(self):
        main_menu = Menu(self.w_main)
        self.w_main.config(menu=main_menu)

        main_menu_command = Menu(main_menu, tearoff=0)
        main_menu_command.add_command(label="Overrideredirect",
                      command=lambda: [self.w_main.overrideredirect(self.revert_overrideredirect())])

        main_menu_command.add_command(label='Statistics', command=lambda: [self.statistics_gui.init(self.w_main)])
        main_menu_command.add_command(label='Statistics V2', command=lambda: [self.statistic_v2.show(self.w_main)])
        main_menu_command.add_command(label='Issue', command=lambda: [self.issue_gui.init(self.w_main)])
        main_menu_command.add_command(label='Settings', command=lambda: [self.settings_gui.init(self.w_main)])

        main_menu_command.add_command(label="Exit", command=lambda: [self.on_closing()])

        main_menu.add_cascade(label="Menu", menu=main_menu_command)

    def minimize(self, event=None):
        if not self.overrideredirect:
            self.s_tray_icon.show = False
            self.w_main.iconify()

    def maximaze(self, event=None):
        self.s_tray_icon.show = True

    def close(self):
        self.s_tray_icon.show = False
        self.w_main.iconify()
        # self.w_main.iconify()

    def main(self):

        top_frame = Frame(self.w_main)
        bottom_frame = Frame(self.w_main)
        history_frame = Frame(self.w_main)
        bottom_link_frame = Frame(self.w_main)
        # history = History(w_main)
        text_entry = StringVar()
        link_entry = StringVar()
        # self.w_main.withdraw()  # hide

        self.w_main.protocol("WM_DELETE_WINDOW", self.minimize)
        self.w_main.bind('<Unmap>', self.minimize)
        self.w_main.bind('<Map>', self.maximaze)
        time = Label(top_frame, textvariable=self.timer.time)
        image_play = PhotoImage(file=f'{get_path()}/assets/play.png')
        image_stop = PhotoImage(file=f'{get_path()}/assets/stop.png')
        image_history = PhotoImage(file=f'{get_path()}/assets/history.png')
        btn_start = Button(top_frame, width=16, height=16, image=image_play, compound=LEFT,
                           command=lambda: self.timer.loop(text_entry.get()))
        btn_stop = Button(top_frame, width=16, height=16, image=image_stop,
                          command=lambda: [self.timer.stop(text_entry.get(), link_entry.get()), text_entry.set(''),
                                           link_entry.set('')])
        btn_show_history = Button(top_frame, width=16, height=16, image=image_history,
                                  command=lambda: [
                                      self.statistic_v2.show(self.w_main)])
        entry_comment = Entry(bottom_frame, textvariable=text_entry, width=25)
        entry_link = Entry(bottom_link_frame, textvariable=link_entry, width=25)

        time.pack(side=LEFT, fill='x')

        btn_show_history.pack(side=RIGHT, padx=(0, 0))
        btn_stop.pack(side=RIGHT, padx=(0, 10))
        btn_start.pack(side=RIGHT, padx=10)

        Label(bottom_frame, text='Comment').pack(side='left')
        entry_comment.pack(fill='x', side='right')
        Label(bottom_link_frame, text='Id or link').pack(side='left')
        entry_link.pack(fill='x', side='right')

        top_frame.pack(fill='x', pady=(0, 10))
        bottom_frame.pack(fill='x')
        bottom_link_frame.pack(fill='x')
        history_frame.pack(pady=(0, 10))
        self.menu()
        self.top_level_menu()
        self.w_main.focus_force()

        if sys.platform == 'win32':
            ttk.Style().theme_use("winnative")

        user = login.isLogin()
        if user:
            self.timer.history.click()

        self.w_main.mainloop()


w_main = WMain()
