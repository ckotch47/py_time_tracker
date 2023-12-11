import calendar
from tkinter import Toplevel, Label, ttk
from src.yandex.service import login, second_to_human_view
import datetime
import isodate
import darkdetect

color = '#bfbfbf'
color_error = '#e57373'
color_cal_foreground = 'black'
color_cal_selectforeground = 'red'
color_cal_background = 'gray'
color_cal_headersforeground = 'black'
color_cal_normalforeground = 'black'
if darkdetect.isDark():
    color = '#353535'
    color_error = '#e53935'
    color_cal_foreground = 'white'
    color_cal_selectforeground = 'red'
    color_cal_background = 'gray'
    color_cal_headersforeground = 'white'
    color_cal_normalforeground = 'white'


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

        month_day_arr, res, all_month, count_days = login.get_month_array()
        temp = res
        table = ttk.Treeview(w_statistic)
        table['columns'] = ('day', 'time', 'link', 'title', 'comment')
        table.column('#0', width=0, stretch=False)
        table.column('day', anchor='center', width=120)
        table.column('time', anchor='center', width=120)
        table.column('link', anchor='center', width=120)
        table.column('title', anchor='center', width=120)
        table.column('comment', anchor='center', width=120)

        table.heading("#0", text="", anchor='center')
        table.heading("day", text="Day", anchor='center')
        table.heading("time", text="Time", anchor='center')
        table.heading("link", text="Link", anchor='center')
        table.heading("title", text="Title", anchor='center')
        table.heading("comment", text="Comment", anchor='center')

        j = 0
        for i in month_day_arr.keys():
            table.insert(parent='', index=0, iid=f'{i}', text=f'',
                         values=(f'{i}', f'{second_to_human_view(month_day_arr[i])}', '', ''),
                         tag=f"{'gray' if j % 2 == 0 else 'white'}")
            j += 1
        j = 0
        for i in temp:
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
                             f"{i['issue']['display']}",
                             f"{comment}",
                         ),
                         tag=f"{'gray' if j % 2 == 0 else 'white'}"
                         )
            j += 1
        j = 0

        table.tag_configure('gray', background=color)
        Label(w_statistic, text=f'Month: {second_to_human_view(all_month, 24)}').pack()
        table.pack(fill='both', expand=True)
        table.bind("<Double-1>", self.link_tree)
        self.table = table

    def link_tree(self, event):
        input_id = self.table.selection()
        input_item = self.table.item(input_id)['values'][2]
        if input_item:
            import webbrowser
            webbrowser.open(f"https://tracker.yandex.ru/{input_item}")
            return
# date link time comment
