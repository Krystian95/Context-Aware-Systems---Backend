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

    def insert_new_position(self, user_id, longitude, latitude, activity, session_id):
        try:
            query = "INSERT INTO public.position (user_id, longitude, latitude, activity, session_id) VALUES (%s, %s, %s, %s, %s) RETURNING id"
            params = (user_id, longitude, latitude, activity, session_id)
            self.cursor.execute(query, params)
            self.connection.commit()
            last_user_id = self.cursor.fetchone()[0]
            print("Successfully created new position with id:", last_user_id)
            return last_user_id
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into position table:", error)

    def find_user_by_registration_token(self, registration_token):
        query = "SELECT user_id FROM public.user WHERE registration_token = %s"
        params = (registration_token,)
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.fetchone()

    def do_sample_query(self):
        self.cursor.execute("SELECT * FROM public.user")
        print(self.cursor.fetchall())

    def close_connection(self):
        # Close communication with the database
        self.cur.close()
        self.connection.close()
