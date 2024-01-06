from tkinter import Toplevel, Label, Frame, Entry, Button, StringVar, IntVar
from tkinter.messagebox import showinfo
from tkinter.ttk import Checkbutton

from src.yandex.service import login
from src.sqlite.service import sqlite


class Settings:
    def __init__(self):
        self.w_settings = None
        self.login = login
        self.org_id = None
        self.enabled = None

    def init(self, root_frame):
        # Toplevel object which will
        # be treated as a new window
        self.w_settings = Toplevel(root_frame)

        # sets the title of the
        # Toplevel widget
        self.w_settings.title("Settings")

        # sets the geometry of toplevel
        self.w_settings.geometry(f"500x150+{int(root_frame.winfo_screenwidth() / 2) - 250}"
                                 f"+{int(root_frame.winfo_screenheight() / 2) - 150}")

        temp = sqlite.get_settings()
        user = login.isLogin()
        self.org_id = StringVar()
        icon = sqlite.get_icon_black_or_white()[1]
        self.enabled = IntVar()
        if icon == 'time':
            self.enabled.set(0)
        else:
            self.enabled.set(1)

        try:
            self.org_id.set(temp[0][4])
        except:
            pass
        try:
            name = user['login']
        except:
            name = False

        frame_info = Frame(self.w_settings, pady=5)
        Label(frame_info, text="Reboot after change settings").pack(side='top', fill='x')
        frame_info.pack(fill='x')
        # A Label widget to show in toplevel
        frame_account = Frame(self.w_settings, pady=5)
        Label(frame_account, text="Account login").pack(side='left')
        Button(frame_account, text='Reset', command=self.login.GUI, width=10).pack(side='right', padx=10)
        Label(frame_account, text=f"{name}").pack(side='left', padx=10)
        frame_account.pack(fill='x')

        frame_org = Frame(self.w_settings, pady=5)
        Label(frame_org, text='Org-ID').pack(side='left')
        Button(frame_org, text='Save', command=self.save_settings, width=10).pack(side='right', padx=10)
        Entry(frame_org, textvariable=self.org_id).pack(side='right', padx=10)
        frame_org.pack(fill='x')

        frame_icon = Frame(self.w_settings, pady=5)
        Checkbutton(
            frame_icon,
            text="Use black icon",
            variable=self.enabled,
            command=self.button_black_icon).pack(side='left', padx=10)

        frame_icon.pack(fill='x')

    def button_black_icon(self):
        icon = sqlite.revert_icon()
        if icon == 'time':
            self.enabled.set(0)
        else:
            self.enabled.set(1)

    def save_settings(self):
        login.set_org_id(self.org_id.get())
        sqlite.update_settings(org_id=self.org_id.get())
        self.w_settings.destroy()
