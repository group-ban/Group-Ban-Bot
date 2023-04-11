import mysql.connector as connector
from config import ConfigParser

with open("../config.json", "r") as _file:
	config = ConfigParser(_file.read())

db = connector.connect(**config.DATABASE)
cursor = db.cursor()

# cursor.execute("DELETE FROM files")
cursor.execute("SELECT * FROM files")
print(cursor.fetchall())
db.commit()
cursor.close()
db.close()