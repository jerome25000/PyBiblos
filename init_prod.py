import sqlite3 as sql

with open("prod.sql") as file:
    data=file.read()
    conn = sql.connect('prod.db')
    conn.executescript(data)

