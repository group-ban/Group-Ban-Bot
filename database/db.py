import mysql.connector as connector

__all__ = ("DB", )

class DB:
    def __init__(self, database_key):
        self.database_key = database_key
        self.db = connector.connect(**database_key)
    def cursor(self):
        return self.db.cursor(buffered=True)
        
    def commit(self):
        self.db.commit()

    def newdb(self):
        self.db = connector.connect(**self.database_key)
        return self.db
        
    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()