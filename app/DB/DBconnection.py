import psycopg2
from psycopg2.extras import RealDictCursor
from DB.DBcredentials import dbuser, dbpass, dbname, dbhost


class PostgresDatabase:
    def __init__(self):
        self.connection = psycopg2.connect(user = dbuser,
                                           password = dbpass,
                                           host = dbhost,
                                           port = "5432",
                                           database = dbname,
                                           cursor_factory=RealDictCursor)
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def commit(self):
        self.connection.commit()
    
    def rollback(self):
        self.connection.rollback()
            
    def close(self, commit=True):
        if commit:
            self.commit()
        self.cursor.close()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()