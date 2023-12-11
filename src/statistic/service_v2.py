import datetime
import threading
from tkinter import ttk
from typing import Any

import isodate
from tkcalendar import Calendar

from src.statistic.service import color, color_cal_foreground, color_cal_selectforeground, color_cal_background, \
    color_cal_headersforeground, color_cal_normalforeground
from src.yandex.service import login, second_to_human_view


class Agenda(Calendar):

    def __init__(self, master=None, **kw):
        Calendar.__init__(self, master, **kw)
        # change a bit the options of the labels to improve display
        for i, row in enumerate(self._calendar):
            for j, label in enumerate(row):
                self._cal_frame.rowconfigure(i + 1, uniform=1)
                self._cal_frame.columnconfigure(j + 1, uniform=1)
                label.configure(justify="center", anchor="n", padding=(1, 4))

    def _display_days_without_othermonthdays(self):
        year, month = self._date.year, self._date.month

        cal = self._cal.monthdays2calendar(year, month)
        while len(cal) < 6:
            cal.append([(0, i) for i in range(7)])

        week_days = {i: 'normal.%s.TLabel' % self._style_prefixe for i in
                     range(7)}  # style names depending on the type of day
        week_days[self['weekenddays'][0] - 1] = 'we.%s.TLabel' % self._style_prefixe
        week_days[self['weekenddays'][1] - 1] = 'we.%s.TLabel' % self._style_prefixe
        _, week_nb, d = self._date.isocalendar()
        if d == 7 and self['firstweekday'] == 'sunday':
            week_nb += 1
        modulo = max(week_nb, 52)
        for i_week in range(6):
            if i_week == 0 or cal[i_week][0][0]:
                self._week_nbs[i_week].configure(text=str((week_nb + i_week - 1) % modulo + 1))
            else:
                self._week_nbs[i_week].configure(text='')
            for i_day in range(7):
                day_number, week_day = cal[i_week][i_day]
                style = week_days[i_day]
                label = self._calendar[i_week][i_day]
                label.state(['!disabled'])
                if day_number:
                    txt = str(day_number)
                    label.configure(text=txt, style=style)
                    date = self.date(year, month, day_number)
                    if date in self._calevent_dates:
                        ev_ids = self._calevent_dates[date]
                        i = len(ev_ids) - 1
                        while i >= 0 and not self.calevents[ev_ids[i]]['tags']:
                            i -= 1
                        if i >= 0:
                            tag = self.calevents[ev_ids[i]]['tags'][-1]
                            label.configure(style='tag_%s.%s.TLabel' % (tag, self._style_prefixe))
                        # modified lines:
                        text = '%s\n' % day_number + '\n'.join([self.calevents[ev]['text'] for ev in ev_ids])
                        label.configure(text=text)
                else:
                    label.configure(text='', style=style)

    def _display_days_with_othermonthdays(self):
        year, month = self._date.year, self._date.month

        cal = self._cal.monthdatescalendar(year, month)

        next_m = month + 1
        y = year
        if next_m == 13:
            next_m = 1
            y += 1
        if len(cal) < 6:
            if cal[-1][-1].month == month:
                i = 0
            else:
                i = 1
            cal.append(self._cal.monthdatescalendar(y, next_m)[i])
            if len(cal) < 6:
                cal.append(self._cal.monthdatescalendar(y, next_m)[i + 1])

        week_days = {i: 'normal' for i in range(7)}  # style names depending on the type of day
        week_days[self['weekenddays'][0] - 1] = 'we'
        week_days[self['weekenddays'][1] - 1] = 'we'
        prev_m = (month - 2) % 12 + 1
        months = {month: '.%s.TLabel' % self._style_prefixe,
                  next_m: '_om.%s.TLabel' % self._style_prefixe,
                  prev_m: '_om.%s.TLabel' % self._style_prefixe}

        week_nb = cal[0][1].isocalendar()[1]
        modulo = max(week_nb, 52)
        for i_week in range(6):
            self._week_nbs[i_week].configure(text=str((week_nb + i_week - 1) % modulo + 1))
            for i_day in range(7):
                style = week_days[i_day] + months[cal[i_week][i_day].month]
                label = self._calendar[i_week][i_day]
                label.state(['!disabled'])
                txt = str(cal[i_week][i_day].day)
                label.configure(text=txt, style=style)
                if cal[i_week][i_day] in self._calevent_dates:
                    date = cal[i_week][i_day]
                    ev_ids = self._calevent_dates[date]
                    i = len(ev_ids) - 1
                    while i >= 0 and not self.calevents[ev_ids[i]]['tags']:
                        i -= 1
                    if i >= 0:
                        tag = self.calevents[ev_ids[i]]['tags'][-1]
                        label.configure(style='tag_%s.%s.TLabel' % (tag, self._style_prefixe))
                    # modified lines:
                    text = '%s\n' % date.day + '\n'.join([self.calevents[ev]['text'] for ev in ev_ids])
                    label.configure(text=text)

    def _show_event(self, date):
        """Display events on date if visible."""
        w, d = self._get_day_coords(date)
        if w is not None:
            label = self._calendar[w][d]
            if not label.cget('text'):
                # this is an other month's day and showothermonth is False
                return
            ev_ids = self._calevent_dates[date]
            i = len(ev_ids) - 1
            while i >= 0 and not self.calevents[ev_ids[i]]['tags']:
                i -= 1
            if i >= 0:
                tag = self.calevents[ev_ids[i]]['tags'][-1]
                label.configure(style='tag_%s.%s.TLabel' % (tag, self._style_prefixe))
            # modified lines:
            text = '%s\n' % date.day + '\n'.join([self.calevents[ev]['text'] for ev in ev_ids])

            label.configure(text=text, border=1)

    def _on_click(self, event):
        if self._properties['state'] == 'normal':
            label = event.widget
            if "disabled" not in label.state():
                day = label.cget("text")
                style = label.cget("style")
                if style in ['normal_om.%s.TLabel' % self._style_prefixe, 'we_om.%s.TLabel' % self._style_prefixe]:
                    if label in self._calendar[0]:
                        self._prev_month()
                    else:
                        self._next_month()
                if day:
                    day = int(str(day).split('\n')[0])
                    year, month = self._date.year, self._date.month
                    self._remove_selection()
                    self._sel_date = self.date(year, month, day)
                    self._display_selection()
                    if self._textvariable is not None:
                        self._textvariable.set(self.format_date(self._sel_date))
                    self.event_generate("<<CalendarSelected>>")


import tkinter as tk

calendar_arr = {}
show_month = []


class StatisticV2:
    def __init__(self):
        self.root = None
        self.month_time = None
        self.table = None
        self.agenda = None

    def select_day(self, event):
        for i in self.table.get_children():
            self.table.delete(i)

        tmp_arr = []
        for i in calendar_arr[self.agenda.get_displayed_month()[0]][1]:
            if self.agenda.selection_get() == datetime.datetime.fromisoformat(i['createdAt'].split('T')[0]).date():
                if i['issue']['key'] not in tmp_arr:
                    tmp_arr.append(i['issue']['key'])

        main_arr = []
        for i in tmp_arr:
            second = 0
            for j in list(filter(lambda x: x['issue']['key'] == i, calendar_arr[self.agenda.get_displayed_month()[0]][1])):
                if self.agenda.selection_get() == datetime.datetime.fromisoformat(j['createdAt'].split('T')[0]).date():
                    second += int(isodate.parse_duration(j['duration']).total_seconds())
            main_arr.append([second_to_human_view(second, 8), i, j['issue']['display']])

        j = 0
        for i in main_arr:
            self.table.insert(
                parent=f"", index='end', iid=f'{i[1]}', text=f'',
                values=(
                    i[0],
                    i[1],
                    i[2],
                    '',
                ),
                tag=f"{'gray' if j % 2 == 0 else 'white'}"
            )
            j += 1

        j = 0
        for i in calendar_arr[self.agenda.get_displayed_month()[0]][1]:
            if self.agenda.selection_get() == datetime.datetime.fromisoformat(i['createdAt'].split('T')[0]).date():
                try:
                    comment = i['comment']
                except:
                    comment = ''
                self.table.insert(parent=f"{i['issue']['key']}", index='end', iid=f'{j}', text=f'',
                                 values=(
                                     second_to_human_view(isodate.parse_duration(i['duration']).total_seconds(), 8),
                                     i['issue']['key'],
                                     i['issue']['display'],
                                     comment,
                                 ),
                                 tag=f"{'gray' if j % 2 == 0 else 'white'}")
                j += 1

    def select_month(self, event):
        data = self.agenda.get_displayed_month()

        global calendar_arr
        if data[0] in show_month:
            self.month_time.set(f'month: {second_to_human_view(calendar_arr[data[0]][2], 24)}')
            return
        show_month.append(data[0])
        temp = login.get_month_array(data[0], data[1])
        th = threading.Thread(target=self.refresh_calendar(temp))
        th.start()
        th.join()

    def refresh_calendar(self, temp):
        m = self.agenda.get_displayed_month()[0]
        global calendar_arr
        calendar_arr[m] = temp
        self.month_time.set(f'month: {second_to_human_view(temp[2], 24)}')
        for i in dict(calendar_arr[m][0]).keys():
            if int(calendar_arr[m][0][i]) != 0:
                self.agenda.calevent_create(
                    datetime.datetime.fromisoformat(i),
                    f'{second_to_human_view(calendar_arr[m][0][i])}',
                    'time'
                )
        return

    def show(self, root_frame):
        self.month_time = tk.StringVar()
        self.init(root_frame)
        # th = threading.Thread(target=self.init(root_frame))
        # th.start()
        # th.join()

    def init(self, root_frame):
        self.root = tk.Toplevel(root_frame)

        self.root.title("Statistic")
        self.root.geometry(f"1200x500+{int(root_frame.winfo_screenwidth() / 2) - 250}"
                             f"+{int(root_frame.winfo_screenheight() / 2) - 150}")
        tk.Label(self.root, textvariable=self.month_time).pack(fill="x", side='top')

        self.agenda = Agenda(self.root, selectmode='day', font="Arial 14",
                             foreground=color_cal_foreground,
                             selectforeground=color_cal_selectforeground,
                             background=color_cal_background,
                             headersforeground=color_cal_headersforeground,
                             normalforeground=color_cal_normalforeground,
                             showweeknumbersbool=False)

        date = self.agenda.datetime.today()
        show_month.append(date.month)
        self.refresh_calendar(login.get_month_array())
        self.agenda.tag_config('time', foreground='orange')
        self.agenda.bind('<<CalendarSelected>>', self.select_day)
        self.agenda.bind('<<CalendarMonthChanged>>', self.select_month)
        self.agenda.pack(fill="both", expand=True, side='left')

        self.table = ttk.Treeview(self.root)
        self.table['columns'] = ('time', 'link', 'title', 'comment')
        self.table.column('#0', width=0, stretch=False)
        self.table.column('time', anchor='center', width=70)
        self.table.column('link', anchor='center', width=70)
        self.table.column('title', anchor='center', width=160)
        self.table.column('comment', anchor='center', width=160)

        self.table.heading("#0", text="", anchor='center')
        self.table.heading("time", text="Time", anchor='center')
        self.table.heading("link", text="Link", anchor='center')
        self.table.heading("title", text="Title", anchor='center')
        self.table.heading("comment", text="Comment", anchor='center')
        self.table.pack(fill="both", expand=True, side='right')
        self.table.tag_configure('gray', background=color)

        self.table.bind("<Double-1>", self.link_tree)
        self.root.mainloop()

    def link_tree(self, event):
        input_id = self.table.selection()
        try:
            int(input_id[0])
        except:
            return
        input_item = self.table.item(input_id)['values'][1]
        if input_item:
            import webbrowser
            webbrowser.open(f"https://tracker.yandex.ru/{input_item}")
            return