import psycopg2


class Postgres:
    conn = None
    cur = None

    def __init__(self):
        # Database connection
        try:
            self.conn = psycopg2.connect("dbname=cristian user=postgres")
            # Open a cursor to perform database operations
            self.cur = self.conn.cursor()
        except:
            print("ERROR connection to database")

    def check_user_exists(self, user_id):
        self.cursor.execute('SELECT * from table where id = %(user_id)d', {'user_id': user_id})

    def make_sample_query(self):
        self.cur.execute("SELECT * FROM test;")
        print(self.cur.fetchall())

    def close_connection(self):
        # Close communication with the database
        self.cur.close()
        self.conn.close()


# Execute a command: this creates a new table
'''cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")'''

# Pass data to fill a query placeholders and let Psycopg perform
# the correct conversion (no more SQL injections!)
'''cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)",
            (100, "abcdef"))'''

# Query the database and obtain data as Python objects
'''
cur.execute("SELECT * FROM test;")
print(cur.fetchall())
'''

'''
cur.fetchone()
(1, 100, "abc'def")
'''

# Make the changes to the database persistent
'''conn.commit()'''
