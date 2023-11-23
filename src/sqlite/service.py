import sqlite3
import os
import sys
from pathlib import Path
from typing import Any


def get_path() -> str:
    folder_path: str
    if sys.platform == 'darwin' or sys.platform == 'win32':
        folder_path = f'{Path.home()}/documents/pytimetracker'
    else:
        folder_path = f'{Path.home()}/temp/pytimetracker'
    return folder_path


class SQLite:
    path: str = get_path()

    def __call__(self):
        self.cursor = self.connection.cursor()

    def __init__(self):
        self.cursor = None
        self.connection = None
        self.cursor: sqlite3.Cursor
        self.connection: sqlite3.Connection
        self.str_db: str = f'{self.path}/data.db'

        try:
            self.connect()
        except sqlite3.OperationalError as e:
            if e.args[0] == 'unable to open database file':
                self.create_path_folder()
                self.__init__()

        try:
            self.cursor.execute('SELECT count(id) FROM data')
        except sqlite3.Error as e:
            if e.args[0] == 'no such table: data':
                self.create_table()
                self.__init__()

    def connect(self):
        self.connection = sqlite3.connect(self.str_db)
        self.cursor = self.connection.cursor()

    def create_path_folder(self):
        os.mkdir(self.path)

    def execute(self, sql) -> Any:
        temp = self.cursor.execute(sql)
        self.connection.commit()
        return temp

    def create_table(self):
        sql = 'create table data \
                ( \
                    id integer \
                        constraint data_pk \
                            primary key autoincrement, \
                    time integer, \
                    name text, \
                    data_at integer \
                );'
        self.execute(sql)

    def save(self, time: str, name: str, date_at: int) -> dict:
        sql = f"insert into data values (NULL, '{time}', '{name}', '{date_at}')"
        self.execute(sql)
        sql_get_last = f'select * from data order by id desc limit 1'
        return self.execute(sql_get_last).fetchall()[0]

    def get(self) -> list:
        sql = 'select * from data order by id desc'
        return self.execute(sql).fetchall()
