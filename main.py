import os

import requests

from src.main import main, get_path

if not os.path.isfile(f'{get_path()}/assets/play.png') or \
        not os.path.isfile(f'{get_path()}/assets/stop.png') or \
        not os.path.isfile(f'{get_path()}/assets/history.png'):

    if not os.path.exists(f'{get_path()}/assets'):
        # Create a new directory because it does not exist
        os.makedirs(f'{get_path()}/assets')

    r = requests.get('https://raw.githubusercontent.com/ckotch47/py_time_tracker/origin/assets/play.png', allow_redirects=True)
    open(f'{get_path()}/assets/play.png', 'wb').write(r.content)
    r = requests.get('https://raw.githubusercontent.com/ckotch47/py_time_tracker/origin/assets/stop.png', allow_redirects=True)
    open(f'{get_path()}/assets/stop.png', 'wb').write(r.content)
    r = requests.get('https://raw.githubusercontent.com/ckotch47/py_time_tracker/origin/assets/history.png', allow_redirects=True)
    open(f'{get_path()}/assets/history.png', 'wb').write(r.content)
#  pyinstaller --onefile --noconsole --noconfirm -n pytimetracker main.py
main()
