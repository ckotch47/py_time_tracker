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
        folder_path = f'{Path.home()}/Documents/pytimetracker'
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
            self.execute('SELECT count(id) FROM settings')
        except sqlite3.Error as e:
            if e.args[0] == 'no such table: settings':
                self.create_table()
                self.__init__()

        try:
            self.query_get_last()
        except sqlite3.Error as e:
            if e.args[0] == 'no such table: query':
                self.query_create_table()

        try:
            self.get_icon_black_or_white()
        except sqlite3.Error as e:
            if e.args[0] == 'no such table: icon_path':
                self.create_icon_path_table()

    def connect(self):
        self.connection = sqlite3.connect(self.str_db)
        self.cursor = self.connection.cursor()

    def create_path_folder(self):
        os.mkdir(self.path)

    def execute(self, sql) -> Any:
        self.cursor = self.connection.cursor()
        temp = self.cursor.execute(sql)
        self.connection.commit()
        return temp

    def create_table(self):
        sql_settings = 'create table settings \
                        ( \
                            id integer \
                                constraint settings_pk \
                                    primary key autoincrement, \
                            token text, \
                            jwt text, \
                            token_type text, \
                            org_id text \
                        );'

        self.execute(sql_settings)
        self.set_settings('', '')

    def set_settings(self, token: str, jwt: str, token_type='bearer'):
        try:
            sql = f"insert into settings VALUES (1, '{token}', '{jwt}', '{token_type}', null)"
            return self.execute(sql).fetchall()
        except:
            sql = f"delete from settings where id = 1"
            self.execute(sql)
            sql = f"insert into settings VALUES (1, '{token}', '{jwt}', '{token_type}', null)"
            return self.execute(sql).fetchall()

    def update_settings(self, token: str = None, jwt: str = None, token_type='bearer', org_id=None):
        if token:
            self.execute(f"update settings set token = '{token}' where id = 1")
        if jwt:
            self.execute(f"update settings set jwt = '{jwt}' where id = 1")
        if org_id:
            self.execute(f"update settings set org_id = '{org_id}' where id = 1")
        self.execute(f"update settings set token_type = '{token_type}' where id = 1")
        return self.get_settings()

    def get_settings(self):
        return self.execute('select * from settings where id = 1').fetchall()

    def query_get_last(self):
        sql = 'select * from query order by id desc limit 1'
        return self.execute(sql).fetchone()

    def query_save(self, q):
        sql = f"insert into query VALUES (NULL, '{q}')"
        return self.execute(sql)

    def query_create_table(self):
        sql = "create table query \
                        ( \
                            id integer \
                                constraint query_pk \
                                    primary key autoincrement,\
                            query text \
                        ); "

        self.execute(sql)

    def get_icon_black_or_white(self):
        sql = 'select * from icon_path where id=1'
        return self.execute(sql).fetchone()

    def create_icon_path_table(self):
        sql = "create table icon_path \
                                ( \
                                    id integer \
                                        constraint query_pk \
                                            primary key autoincrement,\
                                    path text \
                                ); "
        self.execute(sql)

        sql = f"insert into icon_path VALUES (1, 'time')"
        self.execute(sql)

    def revert_icon(self):
        icon = self.get_icon_black_or_white()[1]
        icon_final = None
        if icon == 'time':
            icon_final = 'time_black'
        else:
            icon_final = 'time'

        self.execute(f"update icon_path set path = '{icon_final}' where id = 1")
        return icon_final

sqlite = SQLite()