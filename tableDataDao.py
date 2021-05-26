# Generic database containing : ID : num, UPDATE_DATE : date, DATA : text (json)
import datetime
import json

JSON_EXTRACT_FORMAT = "json_extract(DATA, '$.%s') = '%s'"

class TableDataDao():

    def __init__(self, tableName):
        self.tableName = tableName

    def init(self, dbManager):
        self.maxId = dbManager.getMaxId(self.tableName)
        self.dbManager = dbManager
        print('MaxId =%d for table=%s' % (self.maxId, self.tableName))

    def get(self, id):
        row = self.dbManager.select('SELECT DATA FROM %s WHERE ID = %d' % (self.tableName, id))
        if row:
            return json.loads(row[0][0])
        else:
            return None

    '''
    ' Get with criteria, criteriaDict : key = json field name, value = value to test, example : title : 'mybook'
    '''
    def getWithCriteria(self, criteriaDict):

        where = "AND ".join(map(lambda c : JSON_EXTRACT_FORMAT %(c, criteriaDict[c]), criteriaDict))
        print(where)
        row = self.dbManager.select('SELECT DATA FROM %s WHERE %s' % (self.tableName, where))
        if row:
            return json.loads(row[0][0])
        else:
            return None       

    def count(self):
        result = self.dbManager.select('SELECT COUNT(*) FROM %s' % (self.tableName))
        return result[0][0]

    def getAll(self, limit=50, offset=0):
        rows = self.dbManager.select('SELECT DATA FROM %s ORDER BY ID LIMIT %d OFFSET %d' % (self.tableName, limit, offset))
        if rows:
            return list(map(lambda r: json.loads(r[0]), rows))
        else:
            return None

    def create(self, data):
        sqlText = 'INSERT INTO %s (ID, DATA, UPDATE_DATE) VALUES (?,?,?)' % (self.tableName)
        id = self.maxId + 1
        data['id'] = id
        self.maxId = self.dbManager.update(sqlText, [id, json.dumps(data), datetime.datetime.now()])
        return data

    def delete(self, id):
        sqlText = 'DELETE FROM %s WHERE ID = ?' % (self.tableName)
        self.dbManager.update(sqlText, [id])

    def update(self, id, data):
        initialData = self.get(id)
        if not initialData :
            return None
        sqlText = 'UPDATE %s SET DATA = ?, UPDATE_DATE = ? WHERE ID = ?' % (self.tableName)
        return self.dbManager.partialUpdate(sqlText, initialData, data, datetime.datetime.now(), id)
