import sqlite3 as sql
import json
import datetime


class DbManager:
    def __init__(self, dbfilename):
        print("Opening database %s" % (dbfilename))
        self.conn = sql.connect(dbfilename, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def executeSql(self, sqlCmd):
        try:
            self.cursor.execute(sqlCmd)
        except sql.OperationalError as e:
            print("Sqlite error : %s" % (str(e)))
            pass

    def update(self, sqlCmd, params):
        try:
            for p in params:
                print(p)
            self.cursor.execute(sqlCmd, params)
            self.commit()
            return self.cursor.lastrowid
        except sql.OperationalError as e:
            print("Sqlite error : %s" % (str(e)))
            pass

    def getMaxId(self, tablename):
        try:
            print("getMaxId for %s" % (tablename))
            self.cursor.execute('SELECT MAX(ID) FROM %s' % (tablename))
            maxId = self.cursor.fetchall()[0][0]
            if not maxId:
                return 0
            else:
                return maxId
        except sql.OperationalError as e:
            print("Sqlite error : %s" % (str(e)))
            return 0

    def select(self, sqlCmd):
        try:
            self.cursor.execute(sqlCmd)
            return self.cursor.fetchall()
        except sql.OperationalError as e:
            print("Sqlite error : %s" % (str(e)))
            pass

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def createDb(self, sqlFilename):
        with open(sqlFilename) as file:
            print("Creating DB with script %s" % (sqlFilename))
            data=file.read()
            self.conn.executescript(data)
            print("Script %s executed!" % (sqlFilename))
