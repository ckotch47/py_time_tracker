from tkinter import messagebox

import requests

self_version = 'v0.0.4'


def check_last_releases():
    r = requests.get(f'https://github.com/ckotch47/py_time_tracker/releases/latest',
                     allow_redirects=True)
    tmp = r.url.split('/')
    if tmp[len(tmp) - 1] != self_version:
        messagebox.showinfo(message=f'Update to new releases {tmp[len(tmp) - 1]}')
