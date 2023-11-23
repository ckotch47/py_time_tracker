import sys
from tkinter import *
from tkinter import messagebox

from .timer.service import Timer

overrideredirect = True


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
                  command=lambda: [
    print(root_frame.geometry()), root_frame.overrideredirect(revert_overrideredirect())])
    m.add_command(label="Stick up",
                  command=lambda: root_frame.winfo_geometry())

    def do_popup(event):
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()

    root_frame.bind(f"{get_right_click()}", do_popup)


def main():
    global overrideredirect
    root = Tk()
    root.overrideredirect(overrideredirect)
    root.title("Time")
    root.geometry(f"360x64+{root.winfo_screenwidth() - 360}+0")
    root.resizable(False, False)
    root.columnconfigure(0, weight=1)

    timer = Timer(root)
    text_entry = StringVar()

    def on_closing():
        if timer.timer_s == 0 and messagebox.askokcancel("Quit", "Do you want to quit? "):
            root.destroy()
        else:
            messagebox.showerror('error', 'Please stop timer')

    root.protocol("WM_DELETE_WINDOW", on_closing)

    time = Label(textvariable=timer.time)
    btn_start = Button(text="Start", command=lambda: timer.loop(text_entry.get()))
    btn_stop = Button(text="Stop", command=lambda: [timer.stop(text_entry.get()), text_entry.set('')])
    btn_show_history = Button(text="History", command=timer.history.click)
    entry_comment = Entry(textvariable=text_entry, width=30)

    time.grid(row=0, column=0, sticky=W)
    btn_start.grid(row=0, column=0, sticky=N)
    btn_stop.grid(row=0, column=0, sticky=E)

    entry_comment.grid(row=1, column=0, sticky=W)
    btn_show_history.grid(row=1, column=0, sticky=E)

    menu(root)
    root.focus_force()
    root.mainloop()
