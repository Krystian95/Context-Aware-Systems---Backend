from backend.Utils import Utils


class User:
    postgres = None
    utils = Utils()
    live_sessions = []

    def __init__(self, postgres):
        self.postgres = postgres

    # Verifica che una session_id sia valida
    def validate_session_id(self, session_id):
        print("live_sessions - BEFORE validate_session_id():")
        print(self.live_sessions)
        for session in self.live_sessions:
            if session[0] == session_id:
                return True

        return {
            "result": False,
            "type": "Error",
            "message": "The {session_id} provived is not valid. Please register again."
        }

    # Calcola la freschezza di una sessione.
    # Se l'ultimo update rilevato risale a più di 5 minuti fa
    # genera un nuovo session_id
    def check_freshness_session(self, session_id):
        for session in self.live_sessions:
            if session[0] == session_id:
                date_from = session[2]
                date_to = self.utils.get_current_datetime()
                diff_in_minutes = self.utils.get_datetime_difference_in_minutes(date_from, date_to)
                if diff_in_minutes > 5:  # Old session -> destroy and create new session for the same user_id
                    user_id = session[1]
                    self.remove_session_by_user_id(user_id)
                    new_session_id = self.register_new_session(user_id)
                    print("NEW session_id GENERATED: " + new_session_id)
                    return new_session_id

        return False

    # Restituisce l'user_id di una specifica session_id
    def get_user_id_by_session_id(self, session_id):
        for session in self.live_sessions:
            if session[0] == session_id:
                return session[1]

        return None

    # Elimina l'eventuale sessione già esistente di 'new_user_id'
    def remove_session_by_user_id(self, user_id):
        for session in self.live_sessions:
            if session[1] == user_id:
                self.live_sessions.remove(session)

    # Aggiorna il datetime di ultimo utilizzo di una sessione
    def update_session_datetime(self, session_id):
        for session in self.live_sessions:
            if session[0] == session_id:
                session[2] = self.utils.get_current_datetime()
                return True

        return False

    # Aggiunge la nuova sessione a quelle attive
    def register_new_session(self, new_user_id):
        self.remove_session_by_user_id(new_user_id)
        new_session_id = self.utils.generate_new_session_id(self.live_sessions)
        now = self.utils.get_current_datetime()
        self.live_sessions.append([new_session_id, new_user_id, now])
        print("live_sessions - AFTER register_new_session():")
        print(self.live_sessions)
        return new_session_id

    # Riceve il registration_token e verifica se esiste già nel db,
    # se non esiste crea il nuovo utente.
    # In ogni caso ritorna un nuovo session_id
    def register(self, registration_token):

        # Check if the user is already registered, in this case return the user_id
        user_id = self.postgres.find_user_by_registration_token(registration_token)

        if user_id is None:
            new_user_id = self.postgres.create_new_user(registration_token)

            if new_user_id is not None:
                new_session_id = self.register_new_session(new_user_id)
                return {
                    "result": True,
                    "message": "User successfully registered.",
                    "session_id": new_session_id
                }
            else:
                return {
                    "result": False,
                    "type": "Error",
                    "message": "User registration has failed."
                }
        else:
            new_session_id = self.register_new_session(user_id[0])
            return {
                "result": True,
                "message": "A user is already registered for the same registration_token.",
                "session_id": new_session_id
            }

    # Inserisce la nuova posizione inviata dal dispositivo
    def communicate_position(self, message):

        user_id = self.get_user_id_by_session_id(message["session_id"])

        if user_id is not None:
            position_id = self.postgres.insert_new_position(user_id, message["longitude"], message["latitude"],
                                                            message["activity"],
                                                            message["session_id"])
            if position_id is not None:
                self.update_session_datetime(message["session_id"])
                return {
                    "result": True,
                    "message": "Position successfully inserted.",
                    "session_id": message["session_id"]
                }
            else:
                return {
                    "result": False,
                    "type": "Error",
                    "message": "Inserting position has failed."
                }
