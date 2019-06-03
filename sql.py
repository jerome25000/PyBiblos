import sqlite3 as sql
import json
import datetime

class DbManager:
    def __init__(self, dbfilename) :
        print("Opening database %s" %(dbfilename))
        self.conn = sql.connect(dbfilename)
        self.cursor = self.conn.cursor()

    def executeSql(self, sqlCmd):
        try:    
            self.cursor.execute(sqlCmd)
        except sql.OperationalError as e:
            print("Sqlite error : %s" %(str(e)))
            pass

    def insert(self, sqlCmd, *argv):
        try:    
            self.cursor.execute(sqlCmd, *argv)
            return self.cursor.lastrowid
        except sql.OperationalError as e:
            print("Sqlite error : %s" %(str(e)))
            pass
    
    def select(self, sqlCmd):
        try:    
            self.cursor.execute(sqlCmd)
            return self.cursor.fetchall()
        except sql.OperationalError as e:
            print("Sqlite error : %s" %(str(e)))
            pass

    def commit(self) :
        self.conn.commit()

    def close(self) :
        self.conn.close()        

dbManager = DbManager('test.db')

dbManager.executeSql('DROP TABLE DATA')
dbManager.executeSql('CREATE TABLE DATA (id num, data text, update_date date)')

print('passed!')

data = {'a': 5, 'b': 10, 'c': 'hello'}
data2 = {'a': 10, 'b': 20, 'c': 'hello2'}
id=10
ret = dbManager.insert('INSERT INTO DATA (ID, DATA, UPDATE_DATE) VALUES (?,?,?)', (id, json.dumps(data), datetime.datetime.now()))
print('rowId=%d' %(ret))
id=11
ret=dbManager.insert('INSERT INTO DATA (ID, DATA, UPDATE_DATE) VALUES (?,?,?)', (id, json.dumps(data2), datetime.datetime.now()))
print('rowId=%d' %(ret))

rows = dbManager.select("SELECT id, data, update_date from DATA")

print(len(rows))
for row in rows :
	print('{} {} {}'.format(row[0], row[1], row[2]))

dbManager.commit()
dbManager.close()

