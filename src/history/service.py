import calendar
import datetime

from tkinter import ttk, BROWSE

import isodate

from ..statistic.service import second_to_human_view
from ..yandex.service import login
from ..statistic.service import color, color_error

def timestmap_to_date(date) -> str:
    return datetime.datetime.utcfromtimestamp(date).strftime("%Y-%m-%d %H:%M:%S")



def get_date():
    temp = datetime.datetime.now()

    today = datetime.datetime.fromisoformat(f"{temp.date()}T00:00:00+00:00").date()
    yesterday = temp.date() - datetime.timedelta(days=1)

    w_start = datetime.datetime.fromisoformat(
        f"{temp.date() - datetime.timedelta(days=temp.weekday())}T00:00:00+00:00").date()
    w_end = datetime.datetime.fromisoformat(
        f"{temp.date() + datetime.timedelta(days=6 - temp.weekday())}T23:59:59+00:00").date()
    m_start = datetime.datetime.fromisoformat(
        f"{temp.date() - datetime.timedelta(days=temp.day - 1)}T00:00:00+00:00").date()
    m_end = datetime.datetime.fromisoformat(
        f"{temp.date() + datetime.timedelta(days=calendar.monthrange(temp.date().year, temp.date().month)[1] - temp.day)}T23:59:59+00:00").date()

    return {
        "today": today,
        "yesterday": yesterday,
        "week": {
            "start": w_start,
            "end": w_end
        },
        "month": {
            "start": m_start,
            "end": m_end
        }
    }


class HistoryRange:


    def __init__(self, root_frame):
        self.day = 0
        self.table = None
        self.root = root_frame

    def init(self):
        self.table = ttk.Treeview(self.root, height=1, selectmode=BROWSE)
        self.table['columns'] = ('day')

        self.table.column('#0', width=0, stretch=False)
        self.table.column('day', anchor='center')

        self.table.heading("#0", text="", anchor='center')
        self.table.heading("day", text="Day", anchor='center')


    def pack(self):
        self.init()
        self.table.pack(fill='x')  # grid(row=2, column=0, sticky="ew")

    def packs(self):
        self.pack()

    def show(self):
        self.get()

    def close(self):
        self.table.destroy()

    def set(self, day):
        self.day = day


    def get(self):
        try:
            self.table.delete(0)
        except:
            pass

        self.table.insert(parent='', index=0, iid=f'0', text=f'',
                          values=(f'{second_to_human_view(self.day)}'))


class History:
    def __init__(self, root_frame):
        self.root = root_frame
        self.range = HistoryRange(root_frame)
        self.history = None
        self.state = False

    def init(self):
        self.history = ttk.Treeview(self.root)

        self.history['columns'] = ('date', 'link', 'time', 'title', 'comment')

        self.history.column('#0', width=0, stretch=False)
        self.history.column('date', anchor='center', width=0, stretch=False)
        self.history.column('link', anchor='center', width=100, stretch=False)
        self.history.column('time', anchor='center', width=80, stretch=False)
        self.history.column('title', anchor='center', width=130)
        self.history.column('comment', anchor='center', width=130)

        self.history.heading("#0", text="", anchor='center')
        self.history.heading("date", text="Date", anchor='center')
        self.history.heading("link", text="Link", anchor='center')
        self.history.heading("time", text="Time", anchor='center')
        self.history.heading("title", text="Title", anchor='center')
        self.history.heading("comment", text="Comment", anchor='center')

    def click(self):
        if self.state:
            self.destroy()
            self.range.close()
        else:
            self.range.pack()
            self.pack()
            self.show()
            self.range.show()
        self.state = not self.state

    def refresh(self):
        self.show()
        self.range.show()

    def pack(self):
        self.root.geometry("360x315")
        self.init()
        # self.history.range.pack()
        self.history.pack(fill='both', expand=True)

    def destroy(self):
        self.root.geometry("360x96")
        self.history.destroy()

    def save(self, time_s: str, name: str, date_at: str, link: str = None, title: str = '', error: bool = False):
        if self.history:
            try:
                self.history.insert(parent='', index='0', iid=f'{int(time_s)}_{date_at}', text=f'',
                                    values=(
                                        f"{date_at.split('.')[0]}",
                                        link,
                                        second_to_human_view(time_s),
                                        title,
                                        name,
                                    ),
                                    tag=f"{'error' if error else 'white'}")
                self.history.tag_configure('error', background=color_error)
                # self.history.tag_configure('gray', background=color)
                self.range.set(
                    day=int(self.range.day) + int(time_s),
                )
                self.range.show()
            except Exception as e:
                print(e)
                pass

    def show(self):
        date = get_date()
        user = login.isLogin()
        temp = login.get_statistic_fro_month(user['login'], str(f"{get_date()['yesterday']}T00:00:00"),
                                             str(f"{get_date()['today']}T23:59:59"))  # sqlite.get(all=False)
        if temp.status_code != 200:
            return
        temp = temp.json()

        if len(temp) == 0:
            return

        day = 0
        week = 0
        month = 0
        history_arr = []

        for i in temp:
            try:
                comment = i['comment']
            except:
                comment = ''

            month += int(isodate.parse_duration(i['duration']).total_seconds())
            temp_createdAt = datetime.datetime.fromisoformat(i['createdAt'].split('T')[0]).date()
            if date['week']['start'] <= temp_createdAt <= date['week']['end']:
                history_arr.append(
                    (
                        i['issue']['key'],
                        i['createdAt'],
                        int(isodate.parse_duration(i['duration']).total_seconds()),
                        comment,
                        i['issue']['display']
                    )
                )
                week += int(isodate.parse_duration(i['duration']).total_seconds())

            if date['today'] == temp_createdAt:
                day += int(isodate.parse_duration(i['duration']).total_seconds())

        self.range.week = week
        self.range.set(day)
        for i in self.history.get_children():
            self.history.delete(i)
        j = 0
        if len(history_arr):
            for i in reversed(history_arr):
                self.history.insert(parent='', index='end', iid=f'{j}', text=f'',
                                    values=(
                                        f"{i[1].split('.')[0]}",
                                        i[0],
                                        second_to_human_view(i[2]),
                                        i[4],
                                        i[3],
                                    ),
                                    tag=f"{'gray' if j%2==0 else 'white'}")
                j += 1

        self.history.tag_configure('gray', background=color)
        self.history.bind("<Double-1>", self.link_tree)

    def link_tree(self, event):
        input_id = self.history.selection()
        input_item = self.history.item(input_id)['values'][1]
        if input_item:
            import webbrowser
            webbrowser.open(f"https://tracker.yandex.ru/{input_item}")
            return
        # for opening the link in browser