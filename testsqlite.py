import sqlite3 as sql

with open("test.sql") as file:
    data=file.read()
    conn = sql.connect('test2.db')
    conn.executescript(data)

