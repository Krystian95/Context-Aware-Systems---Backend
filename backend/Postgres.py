import psycopg2


# Postgres class allows Python to connect to the Postgres server and
# commit queries.
class Postgres:
    connection = None
    cursor = None

    def __init__(self):
        # Database connection
        try:
            self.connection = psycopg2.connect(user="postgres", password="ih0SAS@raif", database="db_llr")
            # self.connection = psycopg2.connect(user="postgres", password="ih0SAS@raif", host="localhost", port="62445", database="db_llr")

            # Open a cursor to perform database operations
            self.cursor = self.connection.cursor()

            print("Successfully connected to POSTGRES database")
            # print(psycopg2)
        except:
            print("ERROR connection to POSTGRES database")

    # Crea un nuovo utente
    def create_new_user(self, registration_token):
        try:
            query = '''
                INSERT INTO public.user
                (registration_token)
                VALUES
                (%s)
                RETURNING user_id
            '''
            params = (registration_token,)
            self.cursor.execute(query, params)
            self.connection.commit()
            last_user_id = self.cursor.fetchone()[0]
            print("Successfully created new user with id:", last_user_id)
            return last_user_id
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into mobile table:", error)

    # Inserisce una nuova posizione
    def insert_new_position(self, user_id, longitude, latitude, activity, session_id, is_auto_generated):
        try:
            query = '''
                INSERT INTO public.position
                (user_id, longitude, latitude, activity, session_id, auto_generated)
                VALUES
                (%s, %s, %s, %s, %s, %s)
                RETURNING id
            '''
            params = (user_id, longitude, latitude, activity, session_id, is_auto_generated)
            self.cursor.execute(query, params)
            self.connection.commit()
            last_position_id = self.cursor.fetchone()[0]
            print("Successfully created new position with id:", last_position_id)
            query = "listen qgis; notify qgis, 'added_path';"
            self.cursor.execute(query)
            self.connection.commit()
            return last_position_id
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into position table:", error)

    # Ritorna il messaggio di un geofence, None altrimenti
    def position_inside_geofence(self, position_id, activity):

        if activity == "walk":
            query = """
                SELECT
                    gid,
                    geofence.message
                FROM public.position, public.geofence_walk as geofence
                WHERE 
                    ST_Contains(geofence.geom, position.geom) = TRUE AND
                    position.id = %s
            """
        elif activity == "bike":
            query = """
                SELECT
                    gid,
                    geofence.message
                FROM public.position, public.geofence_bike as geofence
                WHERE 
                    ST_Contains(geofence.geom, position.geom) = TRUE AND
                    position.id = %s
            """
        elif activity == "car":
            query = """
                SELECT
                    gid,
                    geofence.message
                FROM public.position, public.geofence_car as geofence
                WHERE 
                    ST_Contains(geofence.geom, position.geom) = TRUE AND
                    position.id = %s
            """

        params = (position_id,)
        self.cursor.execute(query, params)
        self.connection.commit()
        geofence = self.cursor.fetchone()
        print("geofence:")
        print(geofence)
        if geofence is None:
            return None
        else:
            return geofence

    # Ritorna l'id un utente registrato (se esiste) cercandolo con il registration_token
    def get_user_id_by_registration_token(self, registration_token):
        query = '''
            SELECT user_id
            FROM public.user
            WHERE registration_token = %s
        '''
        params = (registration_token,)
        self.cursor.execute(query, params)
        self.connection.commit()
        result = self.cursor.fetchone()
        if result is None:
            return None
        else:
            return result[0]

    # Ritorna il registration_token di un utente registrato (se esiste) cercandolo con il suo id
    def get_registration_token_by_user_id(self, user_id):
        query = '''
            SELECT registration_token
            FROM public.user
            WHERE user_id = %s
        '''
        params = (user_id,)
        self.cursor.execute(query, params)
        self.connection.commit()
        result = self.cursor.fetchone()
        if result is None:
            return None
        else:
            return result[0]

    # Verifica se per una data session_id e activity un
    def geofence_already_triggered(self, session_id, activity):
        query = '''
            SELECT session_id, geofence_triggered
            FROM public.position
            WHERE session_id = %s AND activity = %s 
            GROUP BY session_id, geofence_triggered
        '''
        params = (session_id, activity,)
        self.cursor.execute(query, params)
        self.connection.commit()
        result = self.cursor.fetchone()
        print(result)
        if result[1] is True:
            return True
        else:
            return False

    def do_sample_query(self):
        self.cursor.execute("SELECT * FROM public.user")
        print(self.cursor.fetchall())

    # Close communication with the database
    def close_connection(self):
        self.cur.close()
        self.connection.close()
