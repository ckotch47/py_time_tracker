import os
import sys
from tkinter import *
from tkinter import messagebox, ttk

from .timer.service import Timer
from .settings.service import Settings
from .yandex.service import login
from .statistic.service import Statistic
from .sqlite.service import get_path

# from .history.service import History
settings_gui = Settings()
statistics_gui = Statistic()

overrideredirect = False
w_main = Tk()
timer = Timer(w_main)
w_main.overrideredirect(overrideredirect)
w_main.title("Time")
w_main.geometry(f"360x96+{w_main.winfo_screenwidth() - 360}+0")
w_main.resizable(True, True)
w_main.columnconfigure(0, weight=1)
w_main.rowconfigure(3, weight=2)


def on_closing():
    if not timer.play:
        w_main.destroy()
    else:
        messagebox.showerror('error', 'Please stop timer')


def get_right_click() -> str:
    if sys.platform == 'darwin':
        return "<Button-2>"
    else:
        return "<Button-3>"


def revert_overrideredirect() -> bool:
    global overrideredirect
    if overrideredirect:
        overrideredirect = False
    else:
        overrideredirect = True
    return overrideredirect


def menu(root_frame):
    global overrideredirect
    m = Menu(root_frame, tearoff=0)
    m.add_command(label="Overrideredirect",
                  command=lambda: [root_frame.overrideredirect(revert_overrideredirect())])
    m.add_command(label='Statistics', command=lambda: [statistics_gui.init(w_main)])
    m.add_command(label='Settings', command=lambda: [settings_gui.init(w_main)])

    m.add_command(label="Exit",
                  command=lambda: [on_closing()])

    def do_popup(event):
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()

    root_frame.bind(f"{get_right_click()}", do_popup)


def main():
    top_frame = Frame(w_main)
    bottom_frame = Frame(w_main)
    history_frame = Frame(w_main)
    bottom_link_frame = Frame(w_main)
    # history = History(w_main)
    text_entry = StringVar()
    link_entry = StringVar()

    w_main.protocol("WM_DELETE_WINDOW", on_closing)

    time = Label(top_frame, textvariable=timer.time)
    image_play = PhotoImage(file=f'{get_path()}/assets/play.png')
    image_stop = PhotoImage(file=f'{get_path()}/assets/stop.png')
    image_history = PhotoImage(file=f'{get_path()}/assets/history.png')
    btn_start = Button(top_frame, image=image_play, compound=LEFT, command=lambda: timer.loop(text_entry.get()))
    btn_stop = Button(top_frame, image=image_stop,
                      command=lambda: [timer.stop(text_entry.get(), link_entry.get()), text_entry.set(''),
                                       link_entry.set('')])
    btn_show_history = Button(top_frame, image=image_history, command=lambda: [statistics_gui.init(w_main)]) #command=timer.history.click)
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
    menu(w_main)
    w_main.focus_force()

    if sys.platform == 'win32':
        ttk.Style().theme_use("clam")

    user = login.isLogin()
    if user:
        timer.history.click()
    w_main.mainloop()
