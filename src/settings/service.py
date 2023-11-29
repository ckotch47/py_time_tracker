from tkinter import Toplevel, Label, Frame, Entry, Button, StringVar
from src.yandex.service import login
from src.sqlite.service import sqlite


class Settings:
    def __init__(self):
        self.w_settings = None
        self.login = login
        self.org_id = None

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
        try:
            self.org_id.set(temp[0][4])
        except:
            pass
        try:
            name = user['login']
        except:
            name = False
        # A Label widget to show in toplevel
        frame_account = Frame(self.w_settings)
        Label(frame_account, text="Account login").pack(side='left')
        Button(frame_account, text='Reset', command=self.login.GUI).pack(side='right', padx=10)
        Label(frame_account, text=f"{name}").pack(side='left', padx=10)
        frame_account.pack(fill='x')

        frame_org = Frame(self.w_settings)
        Label(frame_org, text='Org-ID').pack(side='left')
        Entry(frame_org, textvariable=self.org_id).pack(side='right', padx=10)
        frame_org.pack(fill='x')

        Button(self.w_settings, text='Save', command=self.save_settings).pack(side='right', padx=10)

    def save_settings(self):
        login.set_org_id(self.org_id.get())
        sqlite.update_settings(org_id=self.org_id.get())
        self.w_settings.destroy()
