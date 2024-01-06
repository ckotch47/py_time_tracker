from src.sqlite.service import sqlite

import tkinter
from tkinter import *
from tkinter import ttk

from src.statistic.service import color
from src.yandex.service import login


class IssueGui:
    base_query = None
    string_query = None
    page = 1
    total_page = 0

    def __init__(self):
        self.frame_pagination = None
        self.frame_table = None
        self.frame_enter = None
        self.frame_left = None
        self.table = None
        self.root = None
        self.string_query = StringVar()
        self.string_total = StringVar()
        self.base_query = sqlite.query_get_last()
        if self.base_query:
            self.base_query = self.base_query[1]
        else:
            self.base_query = ''

        self.string_query.set(self.base_query)

    def show(self):
        pass

    def init(self, root_frame):
        self.root = Toplevel(root_frame)
        self.root.title('Issues')
        self.root.geometry('1100x500')

        self.frame_left = Frame(self.root)
        # frame_right = Frame(root)
        self.frame_enter = Frame(self.frame_left)
        self.frame_table = Frame(self.frame_left)
        self.frame_pagination = Frame(self.frame_left)

        self.frame_left.place(relx=0.0, rely=0.0, anchor='nw', relwidth=1, relheight=1)

        self.frame_enter.pack(fill='x')
        self.frame_table.pack(fill='both', expand=True)
        self.frame_pagination.pack(fill='x')

        tkinter.Button(self.frame_pagination, text='Next', command=self.next_issue).pack(side='right')
        tkinter.Button(self.frame_pagination, text='Prev', command=self.prev_issue).pack(side='right')
        tkinter.Label(self.frame_pagination,textvariable=self.string_total).pack(side='right')

        tkinter.Entry(self.frame_enter, textvariable=self.string_query).pack(side='left', fill='x', expand=True)
        tkinter.Button(self.frame_enter, text='Find', command=self.find_issue).pack(side='right')

        s = ttk.Style()
        table = ttk.Treeview(self.frame_table, style='Height.Treeview')
        s.configure('Height.Treeview', rowheight=40)

        table['columns'] = ('link', 'title', 'status', 'queue')
        table.column('#0', width=0, stretch=False)
        table.column('link', anchor='center', width=70)
        table.column('title', anchor='center', width=160)
        table.column('status', anchor='center', width=160)
        table.column('queue', anchor='center', width=160)

        table.heading("#0", text="", anchor='center')
        table.heading("link", text="link", anchor='center')
        table.heading("title", text="title", anchor='center')
        table.heading("status", text="status", anchor='center')
        table.heading("queue", text="queue", anchor='center')

        table.bind("<Double-1>", self.link_tree)

        table.tag_configure('gray', background=color)

        table.pack(fill='both', expand=True)
        self.table = table
        self.find_issue()
        self.root.mainloop()

    def link_tree(self, event=None):
        input_id = self.table.selection()
        input_item = self.table.item(input_id)['values'][0]
        if input_item:
            import webbrowser
            webbrowser.open(f"https://tracker.yandex.ru/{input_item}")
            return

    def find_issue(self):
        tmp = login.get_issue_by_query(query=str(self.string_query.get()), page=self.page)
        print(tmp.headers)
        if self.total_page == 0:
            self.total_page = int(tmp.headers['X-Total-Pages'])
        if not self.string_query.get() == self.base_query:
            sqlite.query_save(self.string_query.get())
            self.base_query = self.string_query.get()
        self.total_page = int(tmp.headers['X-Total-Pages'])
        self.string_total.set(f"Total count: {tmp.headers['X-Total-Count']}     {self.page}/{self.total_page} page")
        self.refresh_table(tmp.json())

    def next_issue(self):
        if self.page < self.total_page:
            self.page += 1
            self.find_issue()

    def prev_issue(self):
        if self.page > 1:
            self.page -= 1
            self.find_issue()

    def refresh_table(self, issue: []):
        for i in self.table.get_children():
            self.table.delete(i)

        j = 1
        for i in issue:
            self.table.insert(parent='', index='end', iid=f"{i['key']}", text=f'',
                         values=(
                             i['key'],
                             i['summary'],
                             i['status']['display'],
                             i['queue']['display']
                         ),
                         tags=f"{'gray' if j % 2 == 0 else 'white'}")
            j += 1
