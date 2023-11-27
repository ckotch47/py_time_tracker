import os
import platform


class YandexAPI:
    app_id = None
    app_password = None
    url = None

    def __init__(self):
        self.uname_os = os.getlogin()
        self.system = platform.system()
        self.app_id = '9dae19d0b2cd40dcaeafe646fe5f2a53'
        self.app_password = '391f33de6adf4bd5a98b3e59b3627673'
        self.url = 'https://oauth.yandex.ru/authorize?response_type=code&client_id=' + \
                   self.app_id + '&device_name=' + self.system
        self.separator = '%2F'


yandex = YandexAPI()
