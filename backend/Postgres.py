import psycopg2


# Postgres class allows Python to connect to the Postgres server and
# commit queries.
class Postgres:
    connection = None
    cursor = None

    def __init__(self):
        # Database connection
        try:
            self.connection = psycopg2.connect(user="postgres", database="db_llr")
            # self.connection = psycopg2.connect(user="postgres", password="ih0SAS@raif", host="localhost", port="62445", database="db_llr")

            # Open a cursor to perform database operations
            self.cursor = self.connection.cursor()

            print("Successfully connected to POSTGRES database")
            # print(psycopg2)
        except:
            print("ERROR connection to POSTGRES database")

    def create_new_user(self, registration_token):
        try:
            query = "INSERT INTO public.user (registration_token) VALUES (%s) RETURNING user_id"
            params = (registration_token,)
            self.cursor.execute(query, params)
            self.connection.commit()
            last_user_id = self.cursor.fetchone()[0]
            print("Successfully created new user with id:", last_user_id)
            return last_user_id
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into mobile table:", error)

    def check_user_exists(self, user_id):
        self.cursor.execute('SELECT * from table where id = %(user_id)', {'user_id': user_id})

    def do_sample_query(self):
        self.cursor.execute("SELECT * FROM public.user")
        print(self.cursor.fetchall())

    def close_connection(self):
        # Close communication with the database
        self.cur.close()
        self.connection.close()


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
