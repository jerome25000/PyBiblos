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
        with open("test.sql") as file:
            data=file.read()
            self.conn.executescript(data)
        '''
        self.executeSql('DROP TABLE AUTHOR')
        self.executeSql('CREATE TABLE AUTHOR (ID NUM, UPDATE_DATE DATE, DATA TEXT)')
        self.executeSql('DROP TABLE BOOK')
        self.executeSql('CREATE TABLE BOOK (ID NUM, UPDATE_DATE DATE, DATA TEXT)')
        '''

if __name__ == '__main__':
    dbManager = DbManager('test.db')

    dbManager.executeSql('DROP TABLE DATA')
    dbManager.executeSql('CREATE TABLE DATA (id num, data text, update_date date)')

    print('passed!')

    data = {'a': 5, 'b': 10, 'c': 'hello'}
    data2 = {'a': 10, 'b': 20, 'c': 'hello2'}
    id = 10
    ret = dbManager.update('INSERT INTO DATA (ID, DATA, UPDATE_DATE) VALUES (?,?,?)', (id, json.dumps(data), datetime.datetime.now()))
    print('rowId=%d' %(ret))
    id = 11
    ret=dbManager.update('INSERT INTO DATA (ID, DATA, UPDATE_DATE) VALUES (?,?,?)', (id, json.dumps(data2), datetime.datetime.now()))
    print('rowId=%d' %(ret))

    rows = dbManager.select("SELECT id, data, update_date from DATA")

    for row in rows:
        print('{} {} {}'.format(row[0], row[1], row[2]))

    dbManager.commit()
    dbManager.close()

