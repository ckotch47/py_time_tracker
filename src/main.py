import sys
from tkinter import *
from tkinter import messagebox, ttk

from .timer.service import Timer

overrideredirect = False
root = Tk()
timer = Timer(root)
root.overrideredirect(overrideredirect)
root.title("Time")
root.geometry(f"360x64+{root.winfo_screenwidth() - 360}+0")
root.resizable(False, False)
root.columnconfigure(0, weight=1)
root.rowconfigure(3, weight=2)



def on_closing():
    if not timer.play:
        root.destroy()
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
    m.add_command(label="Exit",
                  command=lambda: [on_closing()])

    def do_popup(event):
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()

    root_frame.bind(f"{get_right_click()}", do_popup)


def main():
    top_frame = Frame(root)
    bottom_frame = Frame(root)
    history_frame = Frame(root)

    text_entry = StringVar()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    time = Label(top_frame, textvariable=timer.time)
    image_play = PhotoImage(file='assets/play.png')
    image_stop = PhotoImage(file='assets/stop.png')
    image_history = PhotoImage(file='assets/history.png')
    btn_start = Button(top_frame, image=image_play, compound=LEFT, command=lambda: timer.loop(text_entry.get()))
    btn_stop = Button(top_frame, image=image_stop, command=lambda: [timer.stop(text_entry.get()), text_entry.set('')])
    btn_show_history = Button(top_frame, image=image_history, command=timer.history.click)
    entry_comment = Entry(bottom_frame, textvariable=text_entry, width=100)

    time.pack(side=LEFT, fill='x')

    btn_show_history.pack(side=RIGHT, padx=(0, 0))
    btn_stop.pack(side=RIGHT, padx=(0, 10))
    btn_start.pack(side=RIGHT, padx=10)

    entry_comment.pack(side=LEFT, fill='x')

    top_frame.pack(fill='x', pady=(0, 10))
    bottom_frame.pack(fill='x')
    history_frame.pack(pady=(0, 10))
    menu(root)
    root.focus_force()

    if sys.platform == 'win32':
        ttk.Style().theme_use("clam")

    root.mainloop()
