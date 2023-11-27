import calendar
from tkinter import Toplevel, Label, Frame, Entry, Button, StringVar, ttk
from src.yandex.login import login
from src.sqlite.service import sqlite
import datetime
import isodate


def second_to_human_view(sec):
    try:
        return datetime.timedelta(seconds=int(sec))
    except TypeError:
        return '0:00:00'


class Statistic:
    def __init__(self):
        self.login = login

    def init(self, root_frame):
        # Toplevel object which will
        # be treated as a new window
        w_statistic = Toplevel(root_frame)

        # sets the title of the
        # Toplevel widget
        w_statistic.title("Statistic")

        # sets the geometry of toplevel
        w_statistic.geometry(f"300x200+{int(root_frame.winfo_screenwidth() / 2) - 250}"
                             f"+{int(root_frame.winfo_screenheight() / 2) - 150}")

        user = login.isLogin()
        if not user:
            return
        temp = datetime.datetime.now()
        data_from = temp.date() - datetime.timedelta(days=temp.day - 1)
        date_to = temp.date() + datetime.timedelta(
            days=calendar.monthrange(temp.date().year, temp.date().month)[1] - temp.day)

        month_day_arr = dict()
        for i in range(1, calendar.monthrange(temp.date().year, temp.date().month)[1] + 1):
            month_day_arr[
                datetime.datetime.fromisoformat(f"{temp.year}-{temp.month}-{i if i > 9 else f'0{i}'}").strftime(
                    "%Y-%m-%d")] = 0

        temp = login.get_statistic_fro_month(user['login'], str(data_from), str(date_to))
        if temp.status_code != 200:
            pass
        all_month = 0
        for i in temp.json():
            date = str(datetime.datetime.fromisoformat(i['createdAt'].split('T')[0]).date())
            if date in month_day_arr.keys():
                month_day_arr[date] += int(isodate.parse_duration(i['duration']).total_seconds())
                all_month += int(isodate.parse_duration(i['duration']).total_seconds())

        table = ttk.Treeview(w_statistic)
        table['columns'] = ('day', 'time')

        table.column('#0', width=0, stretch=False)
        table.column('day', anchor='center', width=120)
        table.column('time', anchor='center', width=120)

        table.heading("#0", text="", anchor='center')
        table.heading("day", text="Day", anchor='center')
        table.heading("time", text="Time", anchor='center')


        for i in month_day_arr.keys():
            table.insert(parent='', index=0, iid=f'{i}', text=f'',
                              values=(f'{i}', f'{second_to_human_view(month_day_arr[i])}'))

        Label(w_statistic, text=f'Month: {second_to_human_view(all_month)}').pack()
        table.pack(fill='y')
