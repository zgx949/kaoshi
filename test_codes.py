import sqlite3

conn = sqlite3.connect('db.sqlite3')
print("Opened database successfully")
cursor = conn.cursor()
sql = "select * from ccenpx_user"
cursor.execute(sql)
values = cursor.fetchall()
print(values)
cursor.close()
conn.commit()
conn.close()
