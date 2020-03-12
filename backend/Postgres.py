import psycopg2


# Postgres class allows Python to connect to the Postgres server and
# commit queries.
class Postgres:
    conn = None
    cur = None

    def __init__(self):
        # Database connection
        try:
            self.conn = psycopg2.connect("dbname=db_llr user=postgres")
            # Open a cursor to perform database operations
            self.cur = self.conn.cursor()
            print("Successfully connected to POSTGRES database")
            # print(psycopg2)
        except:
            print("ERROR connection to POSTGRES database")

    def check_user_exists(self, user_id):
        self.cursor.execute('SELECT * from table where id = %(user_id)d', {'user_id': user_id})

    def do_sample_query(self):
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
