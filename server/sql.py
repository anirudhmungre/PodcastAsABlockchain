from config import config
from psycopg2 import connect, DatabaseError, Binary

class SQL(object):
    def __init__(self):
        self.params = config()
    
    def insert(self, tablename, values) -> str:
        """
        Inserts a data row into a table
        :param tablename: <str> The name of the table to insert into
        :param values: <dict> Holds the data to be inserted
        :return: <str> The id of the inserted podcast
        """
        # values = ','.join([f"'{x}'" for x in row.values()])
        sql = f'INSERT INTO {tablename} VALUES(default, %s, %s, %s, default) RETURNING id, date;'
        podcast_id = None
        try:
            # Connect to the DB
            conn = connect(**self.params)
            # Create cursor to perform actions
            cur = conn.cursor()
            # Execute the query
            cur.execute(sql, (values['title'], values['media'], values['posterKey']))
            # Get the generated id back
            podcast_id, date = cur.fetchone()[:2]
            # Commit changes to DB
            conn.commit()
            # Close connection
            cur.close()
        except (Exception, DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return podcast_id, date
    
    def select(self, tablename, id=None) -> list:
        """ query parts from the parts table """
        conn = None
        rows = None
        sql = None
        if id is None:
            sql = f'SELECT id, title, media, posterKey, date FROM {tablename} ORDER BY date DESC'
        else:
            sql = f'SELECT media FROM {tablename} WHERE id=\'{id}\''

        try:
            conn = connect(**config())
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            cur.close()
        except (Exception, DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return rows
    

