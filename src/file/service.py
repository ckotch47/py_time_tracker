from ..sqlite.service import get_path
import os
import requests

path = get_path()
folder = 'assets'
files = [
    "play.png",
    "stop.png",
    "history.png",
    "time.png"
]


def check_and_download_files():
    if not os.path.exists(f'{path}/{folder}'):
        # Create a new directory because it does not exist
        os.makedirs(f'{path}/{folder}')

    for i in files:
        if not os.path.isfile(f"{path}/{folder}/{i}"):
            r = requests.get(f'https://raw.githubusercontent.com/ckotch47/py_time_tracker/origin/assets/{i}',
                             allow_redirects=True)
            open(f'{path}/{folder}/{i}', 'wb').write(r.content)
