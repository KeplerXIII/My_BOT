import sqlite3
from .tables import query_tables, query_users


class Database():
    '''Класс базы данных SQLite'''
    
    def __init__(self, db_name):
        '''Метод инициализации'''
        self.query_users = query_users
        self.query_tables = query_tables
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.execute_new(self.query_users)
        self.execute_new(self.query_tables)

    def execute(self, query, params):
        '''Метод выполнения SQL-запросов'''
        self.cur.execute(query, params)
        self.conn.commit()
    
    def execute_new(self, query):
        '''Метод выполнения SQL-запросов'''
        self.cur.execute(query)
        self.conn.commit()

    def commit(self):
        '''Метод сохранения изменений'''
        self.conn.commit()

    def close(self):
        '''Метод закрытия соединения с базой данных'''
        self.conn.close()

    def get_all(self, table_name):
        '''Метод получения всех записей из таблицы'''
        self.execute(f"SELECT * FROM {table_name}")
        return self.cur.fetchall()
    
    def get_table_ids(self, tg_id):
        self.execute(f'SELECT TRELLO_BOARD_ID FROM tables WHERE TG_ID = ?', (tg_id,))
        return self.cur.fetchall()
    
    def add_table(self, tg_id, board_id):
        self.execute(f'INSERT INTO tables (TG_ID, TRELLO_BOARD_ID) VALUES (?, ?)', (tg_id, board_id,))

    def remove_table(self, tg_id, board_id):
        self.execute(f'DELETE FROM tables WHERE TG_ID = ? AND TRELLO_BOARD_ID = ?', (tg_id, board_id,))

    def get_api_key(self, tg_id):
        self.execute(f'SELECT TRELLO_API FROM users WHERE TG_ID = ?', (tg_id,))
        return self.cur.fetchone()
    
    def get_api_token(self, tg_id):
        self.execute(f'SELECT TRELLO_TOKEN FROM users WHERE TG_ID = ?', (tg_id,))
        return self.cur.fetchone()

    def add_record(self, table_name: str, record):
        '''Метод добавления записи в таблицу'''
        placeholders = ', '.join(['?' for _ in range(len(record))])
        self.execute(f"INSERT INTO {table_name} (TG_ID, TRELLO_API, TRELLO_TOKEN, STATUS, NAME) VALUES ({placeholders})", record)
    
    def add_api_trello(self, api_key: str, tg_id: int):
        self.execute(f"UPDATE users SET TRELLO_API = ? WHERE TG_ID = ?", (api_key, tg_id,))
    
    def add_token_trello(self, api_token: str, tg_id: int):
        self.execute(f"UPDATE users SET TRELLO_TOKEN = ? WHERE TG_ID = ?", (api_token, tg_id,))
    
    def check_user(self, TG_ID: int, table: str) -> bool:
        "Проверяем есть ли запись в таблице"
        with self.conn:
            return bool(len(self.cur.execute(f"SELECT * FROM '{table}' WHERE TG_ID = ?", (TG_ID,)).fetchall()))
    
    def check_api(self, TG_ID: int, table: str) -> bool:
        "Проверяем есть ли запись в таблице"
        with self.conn:
            return not str(self.cur.execute(f"SELECT TRELLO_API FROM '{table}' WHERE TG_ID = ?", (TG_ID,)).fetchone()[0]) == 'token'
    
    def check_token(self, TG_ID: int, table: str) -> bool:
        "Проверяем есть ли запись в таблице"
        with self.conn:
            return not str(self.cur.execute(f"SELECT TRELLO_TOKEN FROM '{table}' WHERE TG_ID = ?", (TG_ID,)).fetchone()[0]) == 'token'

