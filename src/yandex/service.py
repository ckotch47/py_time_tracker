import configparser
import tkinter
import os.path
import datetime
import calendar
from tkinter import messagebox

import isodate
import requests
from PIL import Image, ImageTk
import qrcode
from src.yandex.yandex import yandex
from src.sqlite.service import sqlite, get_path

BASE_URL = 'https://api.tracker.yandex.net/v2'

def timedelta_to_hms(duration, format=24):
    days, seconds = duration.days, duration.seconds
    hours = days * format + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds

def hms_to_second(duration, format=8):
    days, seconds = duration.days, duration.seconds
    hours = days * format + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours*3600 + minutes*60 + seconds

def second_to_human_view(sec, format=8):
    try:
        t = datetime.timedelta(seconds=int(sec))
        t = timedelta_to_hms(t, format)
        return f"{t[0] if t[0] > 9 else f'0{t[0]}'}:" \
               f"{t[1] if t[1] > 9 else f'0{t[1]}'}:" \
               f"{t[2] if t[2] > 9 else f'0{t[2]}'}"
    except TypeError:
        return '0:00:00'

class SimpleUtc(datetime.tzinfo):
    def tzname(self, **kwargs):
        return "UTC"
    def utcoffset(self, dt):
        return datetime.timedelta(0)

def get_date_utcnow_iso(time=None):
    try:
        return datetime.datetime.utcnow().replace(tzinfo=SimpleUtc()).isoformat()
    except:
        return time


class Login:
    def __init__(self):
        self.org_id = None
        self.sqlite = sqlite
        self.__mainWindow = None
        self.code = None
        self.jwt = None
        self.access_token = None
        self.settings = self.sqlite.get_settings()

    def isLogin(self):
        self.settings = self.sqlite.get_settings()
        try:
            if not self.settings[0][1] and not self.settings[0][2]:
                return self.GUI()
        except:
            if not self.settings[0][1] and not self.settings[0][2]:
                return self.GUI()

        self.access_token = self.settings[0][1]
        self.jwt = self.settings[0][2]
        self.org_id = self.settings[0][4]

        res = requests.get(url=f'{BASE_URL}/myself',
                           headers={"Authorization": "OAuth " + self.access_token, "X-Cloud-Org-ID": self.org_id})

        if res.status_code == 401:
            return self.refreshJWT()
        elif res.status_code == 200:
            return res.json()
        else:
            return False

    def refreshJWT(self):
        res = requests.post(url='https://oauth.yandex.ru/token', data={
            'grant_type': 'refresh_token',
            'refresh_token': self.jwt,
            'client_id': yandex.app_id,
            'client_secret': yandex.app_password
        })

        if res.status_code == 401 or res.status_code == 400:
            self.GUI()
        else:
            res = res.json()

    @staticmethod
    def generateQR():
        data = yandex.url
        filename = f'{get_path()}/qr_code.png'
        img = qrcode.make(data)
        img.save(filename)

    def GUI(self):
        if self.checkCode():
            image = Image.open(f'{get_path()}/qr_code.png')
        else:
            self.generateQR()
            image = Image.open(f'{get_path()}/qr_code.png')

        self.__mainWindow = tkinter.Toplevel()
        self.__mainWindow.wm_title('Yandex auth')
        # label
        label = tkinter.Label(self.__mainWindow, text='scan qr or past link into browser')
        label.pack(pady=5)

        # image
        canvas = tkinter.Canvas(self.__mainWindow, height=image.height, width=image.width)
        photo = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, anchor='nw', image=photo)
        canvas.pack(pady=5)

        # link
        link = tkinter.Entry(self.__mainWindow, width=65)
        link.insert(0, yandex.url)
        link.pack(pady=5)

        label = tkinter.Label(self.__mainWindow, text='CODE')
        label.pack()

        frame = tkinter.Frame(self.__mainWindow)
        frame.pack(side='bottom', fill='none')

        self.code = tkinter.Entry(frame, width=60)
        self.code.pack(side='left')

        btn = tkinter.Button(frame, text='Ok', command=self.sendCode)
        btn.pack(side='right')

        tkinter.mainloop()

    def sendCode(self):
        try:
            temp = requests.post(url='https://oauth.yandex.ru/token', data={
                'grant_type': 'authorization_code',
                'code': self.code.get(),
                'client_id': yandex.app_id,
                'client_secret': yandex.app_password
            }).json()
            self.sqlite.update_settings(token=temp['access_token'], jwt=temp['refresh_token'])
            self.access_token = temp['access_token']
            self.jwt = temp['refresh_token']
            self.__mainWindow.destroy()
        except Exception as e:
            messagebox.showerror('Error', e)
            # went_wrong()

    def set_org_id(self, org_id: str):
        self.org_id = org_id

    def write_worklog(self, task_id: str, start: str, duration: str, comment: str):
        tmp = requests.post(url=f'{BASE_URL}/issues/{task_id}/worklog',
                            headers={"Authorization": "OAuth " + self.access_token, "X-Cloud-Org-ID": self.org_id},
                            json={
                                "start": get_date_utcnow_iso(),
                                "duration": f"PT{duration}S",
                                "comment": comment
                            })
        return tmp

    def get_statistic_fro_month(self, user_login: str, from_data: str, to_data: str):
        tmp = requests.post(url=f'{BASE_URL}/worklog/_search',
                            # todo setting X-Cloud-Org-ID
                            headers={"Authorization": "OAuth " + self.access_token, "X-Cloud-Org-ID": self.org_id},
                            json={
                                  "createdBy": user_login,
                                  "createdAt": {
                                    "from": from_data,
                                    "to": to_data
                                  }
                            })
        return tmp

    def get_issue_by_query(self, query: str, page: int) -> []:
        tmp = requests.post(url=f'{BASE_URL}/issues/_search?expand=attachments&perPage=10&page={page}',
                            headers={"Authorization": "OAuth " + self.access_token, "X-Cloud-Org-ID": self.org_id},
                            json={
                                "query": f"{query}"
                            })
        return tmp if tmp.status_code == 200 else []


    def get_month_array(self, month=None, year=None):
        temp = datetime.datetime.now()

        if not month:
            month = temp.date().month

        if not year:
            year = temp.date().year

        user = self.isLogin()
        month_day_arr = dict()

        count_days = calendar.monthrange(year, month)[1] + 1
        for i in range(1, count_days):
            month_day_arr[
                datetime.datetime.fromisoformat(f"{year}-{month if month > 9 else f'0{month}'}-{i if i > 9 else f'0{i}'}").strftime(
                    "%Y-%m-%d")] = 0
        res = []

        for i in month_day_arr:
            tmp = login.get_statistic_fro_month(user['login'], f"{i}T00:00:00", f"{i}T23:59:59")
            try:
                if len(tmp.json()) > 0:
                    for j in tmp.json():
                        res.append(j)
            except:
                pass

        temp = res  # $login.get_statistic_fro_month(user['login'], str(data_from), str(date_to))
        if len(temp) == 0:
            pass
        all_month = 0
        for i in temp:
            date = str(datetime.datetime.fromisoformat(i['createdAt'].split('T')[0]).date())
            if date in month_day_arr.keys():
                month_day_arr[date] += int(isodate.parse_duration(i['duration']).total_seconds())
                all_month += int(hms_to_second(isodate.parse_duration(i['duration']), 8))

        return month_day_arr, res, all_month, count_days

    @staticmethod
    def checkCode():
        if os.path.isfile(f'{get_path()}/qr_code.png'):
            return True
        else:
            return False

    def show(self):
        if self.isLogin():
            return True
        else:
            self.GUI()


login = Login()
