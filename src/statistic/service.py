import calendar
from tkinter import Toplevel, Label, Frame, Entry, Button, StringVar, ttk
from src.yandex.service import login, timedelta_to_hms, second_to_human_view
from src.sqlite.service import sqlite
import datetime
import isodate




class Statistic:
    def __init__(self):
        self.table = None
        self.login = login

    def init(self, root_frame):
        # Toplevel object which will
        # be treated as a new window
        w_statistic = Toplevel(root_frame)

        # sets the title of the
        # Toplevel widget
        w_statistic.title("Statistic")

        # sets the geometry of toplevel
        w_statistic.geometry(f"600x200+{int(root_frame.winfo_screenwidth() / 2) - 250}"
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
        table['columns'] = ('day', 'time', 'link', 'comment')
        table.column('#0', width=0, stretch=False)
        table.column('day', anchor='center', width=120)
        table.column('time', anchor='center', width=120)
        table.column('link', anchor='center', width=120)
        table.column('comment', anchor='center', width=120)

        table.heading("#0", text="", anchor='center')
        table.heading("day", text="Day", anchor='center')
        table.heading("time", text="Time", anchor='center')
        table.heading("link", text="Link", anchor='center')
        table.heading("comment", text="Comment", anchor='center')

        j = 0
        for i in month_day_arr.keys():
            table.insert(parent='', index=0, iid=f'{i}', text=f'',
                         values=(f'{i}', f'{second_to_human_view(month_day_arr[i])}', '', ''),
                         tag=f"{'gray' if j%2==0 else 'white'}")
            j += 1
        j = 0
        for i in temp.json():
            try:
                comment = i['comment']
            except:
                comment = ''
            date = str(datetime.datetime.fromisoformat(i['createdAt'].split('T')[0]).date())
            table.insert(parent=f'{date}', index=0, iid=f'{date}_{j}', text=f'',
                         values=(
                             f"{(i['createdAt'].split('T')[1]).split('.')[0]}",
                             f"{second_to_human_view(int(isodate.parse_duration(i['duration']).total_seconds()))}",
                             f"{i['issue']['key']}",
                             f"{comment}"
                         ),
                         tag=f"{'gray' if j%2==0 else 'white'}"
                         )
            j += 1
        j = 0

        table.tag_configure('gray', background='#cccccc')
        Label(w_statistic, text=f'Month: {second_to_human_view(all_month)}').pack()
        table.pack(fill='x')
        table.bind("<Double-1>", self.link_tree)
        self.table = table

    def link_tree(self, event):
        input_id = self.table.selection()
        input_item = self.table.item(input_id)['values'][2]
        if input_item:
            import webbrowser
            webbrowser.open(f"https://tracker.yandex.ru/PN-2{input_item}")
        # for opening the link in browser

        # do whatever you want
# date link time comment