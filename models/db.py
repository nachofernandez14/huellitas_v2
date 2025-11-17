import sqlite3
from sqlite3 import Connection, Cursor

class Database():
    def __init__(self, db_path = 'database/negocio.db'):
        self.db_path = db_path
        self.connection: Connection = None
        self.cursor: Cursor = None
        self.connect()



    def connect(self):
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def execute(self, query, params:tuple=()):
        #Ejecuta una consulta SQL
        self.cursor.execute(query, params)
        q = query.lstrip().upper()
        if q.startswith("INSERT") or q.startswith("UPDATE") or q.startswith("DELETE"):
            self.connection.commit()
        return self.cursor
    
    def fetchall(self):
        return self.cursor.fetchall()
    def fetchone(self):
        return self.cursor.fetchone()
    
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
        