import sqlite3 as sql
import json
import datetime
import threading

class DbManager:
    def __init__(self, dbfilename):
        print("Opening database %s" % (dbfilename))
        self.conn = sql.connect(dbfilename, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()

    def executeSql(self, sqlCmd):
        try:
            self.lock.acquire(True)
            self.cursor.execute(sqlCmd)
        except sql.OperationalError as e:
            print("Sqlite error : %s" % (str(e)))
            pass
        finally: 
            self.lock.release()

    def update(self, sqlCmd, params):
        try:
            self.lock.acquire(True)
            self.cursor.execute(sqlCmd, params)
            self.commit()
            return self.cursor.lastrowid
        except sql.OperationalError as e:
            print("Sqlite error : %s" % (str(e)))
            pass
        finally:
            self.lock.release()

    def partialUpdate(self, sqlCmd, initialData, data, dateModif, id):
        try:
            self.lock.acquire(True)
            
            for key in data:
                initialData[key] = data[key]

            print(json.dumps(initialData))

            self.cursor.execute(sqlCmd, [json.dumps(initialData), dateModif, id])
            self.commit()
            return self.cursor.lastrowid
        except sql.OperationalError as e:
            print("Sqlite error : %s" % (str(e)))
            pass
        finally:
            self.lock.release()

    def getMaxId(self, tablename):
        try:
            self.lock.acquire(True)
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
        finally:
            self.lock.release()

    def select(self, sqlCmd):
        try:
            self.lock.acquire(True)
            self.cursor.execute(sqlCmd)
            return self.cursor.fetchall()
        except sql.OperationalError as e:
            print("Sqlite error : %s" % (str(e)))
            pass
        finally:
            self.lock.release();

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
