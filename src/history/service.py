import calendar
import datetime
import time
from tkinter import ttk, BROWSE, Label
from ..sqlite.service import sqlite


def timestmap_to_date(date) -> str:
    return datetime.datetime.utcfromtimestamp(date).strftime("%Y-%m-%d %H:%M:%S")


def second_to_human_view(sec):
    try:
        return datetime.timedelta(seconds=int(sec))
    except TypeError:
        return '0:00:00'


class HistoryRange:
    def __init__(self, root_frame):
        self.table = None
        self.root = root_frame

    def init(self):
        self.table = ttk.Treeview(self.root, height=1, selectmode=BROWSE)
        self.table['columns'] = ('day', 'weak', 'month')

        self.table.column('#0', width=0, stretch=False)
        self.table.column('day', anchor='center', width=120)
        self.table.column('weak', anchor='center', width=120)
        self.table.column('month', anchor='center', width=120)

        self.table.heading("#0", text="", anchor='center')
        self.table.heading("day", text="Day", anchor='center')
        self.table.heading("weak", text="Weak", anchor='center')
        self.table.heading("month", text="Month", anchor='center')

    def pack(self):
        Label(text='Local').pack()
        self.table.pack()  # grid(row=2, column=0, sticky="ew")

    def show(self):
        self.init()
        self.get()
        self.pack()

    def close(self):
        self.table.destroy()

    def get(self):
        try:
            self.table.delete(0)
        except:
            pass

        temp = datetime.datetime.now()
        today = {
            'start': time.mktime(datetime.datetime.fromisoformat(f"{temp.date()}T00:00:00+00:00").timetuple()) + 10787,
            'end': time.mktime(datetime.datetime.fromisoformat(f"{temp.date()}T23:59:59+00:00").timetuple()) + 10787
        }
        weak = {
            'start': time.mktime(datetime.datetime.fromisoformat(
                f"{temp.date() - datetime.timedelta(days=temp.weekday())}T00:00:00+00:00").timetuple()) + 10787,
            'end': time.mktime(datetime.datetime.fromisoformat(
                f"{temp.date() + datetime.timedelta(days=6 - temp.weekday())}T23:59:59+00:00").timetuple()) + 10787,
        }
        mouth = {
            'start': time.mktime(datetime.datetime.fromisoformat(
                f"{temp.date() - datetime.timedelta(days=temp.day - 1)}T00:00:00+00:00").timetuple()) + 10787,
            'end': time.mktime(datetime.datetime.fromisoformat(
                f"{temp.date() + datetime.timedelta(days=calendar.monthrange(temp.date().year, temp.date().month)[1] - temp.day)}T23:59:59+00:00").timetuple()) + 10787
        }
        sql_today = f"select sum(time) from data where data_at > {today.get('start')} AND data_at < {today.get('end')}"
        sql_weak = f"select sum(time) from data where data_at > {weak.get('start')} AND data_at < {weak.get('end')}"
        sql_mouth = f"select sum(time) from data where data_at > {mouth.get('start')} AND data_at < {mouth.get('end')}"
        day = sqlite.execute(sql_today).fetchall()[0][0]
        week = sqlite.execute(sql_weak).fetchall()[0][0]
        mouth = sqlite.execute(sql_mouth).fetchall()[0][0]

        self.table.insert(parent='', index=0, iid=f'0', text=f'',
                          values=(f'{second_to_human_view(day)}', f'{second_to_human_view(week)}',
                                  f'{second_to_human_view(mouth)}'))


class History:
    def __init__(self, root_frame):
        self.root = root_frame
        self.range = HistoryRange(root_frame)
        self.history = None
        self.state = False

    def init(self):
        self.history = ttk.Treeview(self.root)

        self.history['columns'] = ('id', 'time', 'name', 'link', 'date_at')

        self.history.column('#0', width=0, stretch=False)
        self.history.column('id', anchor='center', width=50)
        self.history.column('time', anchor='center', width=80)
        self.history.column('name', anchor='center', width=100)
        self.history.column('link', anchor='center', width=100)
        self.history.column('date_at', anchor='center', width=130)

        self.history.heading("#0", text="", anchor='center')
        self.history.heading("id", text="Id", anchor='center')
        self.history.heading("time", text="Time", anchor='center')
        self.history.heading("name", text="Name", anchor='center')
        self.history.heading("link", text="Link", anchor='center')
        self.history.heading("date_at", text="DateAt", anchor='center')

    def click(self):
        if self.state:
            self.destroy()
            self.range.close()
        else:
            self.range.show()
            self.pack()
            self.show()
        self.state = not self.state

    def pack(self):
        self.root.geometry("360x315")
        self.init()
        self.history.pack()

    def destroy(self):
        self.root.geometry("360x96")
        self.history.destroy()

    def save(self, time_s: str, name: str, date_at: int, link: str = None):
        i = sqlite.save(time_s, name, date_at, link)
        if self.history:
            try:
                self.history.insert(parent='', index=0, iid=f'{i[0]}', text=f'{i[1]}',
                                    values=(i[0], f'{datetime.timedelta(seconds=int(i[1]))}', f'{i[2]}',
                                            i[4], f'{timestmap_to_date(i[3])}'))
                self.range.get()
            except:
                pass

    def show(self):
        temp = sqlite.get(all=False)
        if temp:
            for i in temp:
                self.history.insert(parent='', index='end', iid=f'{i[0]}', text=f'{i[1]}',
                                    values=(i[0], f'{(datetime.timedelta(seconds=int(i[1])))}', f'{i[2]}',
                                            i[4], f'{timestmap_to_date(i[3])}'))
