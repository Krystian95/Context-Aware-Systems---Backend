from backend.Utils import Utils


class User:
    postgres = None
    utils = Utils()

    def __init__(self, postgres):
        self.postgres = postgres

    # Riceve il registration_token e verifica se esiste già nel db,
    # se non esiste crea il nuovo utente.
    # In ogni caso ritorna un nuovo session_id
    def register(self, registration_token):

        # Check if the user is already registered, in this case return the user_id
        user_id = self.postgres.find_user_by_registration_token(registration_token)
        session_id = self.utils.generate_new_session_id()

        if user_id is None:
            new_user_id = self.postgres.create_new_user(registration_token)

            if new_user_id is not None:
                return {
                    "result": True,
                    "message": "User successfully registered.",
                    "session_id": session_id,
                    "user_id": new_user_id
                }
            else:
                return {
                    "result": False,
                    "type": "Error",
                    "message": "User registration has failed."
                }
        else:
            return {
                "result": True,
                "message": "A user is already registered for the same registration_token.",
                "session_id": session_id,
                "user_id": user_id[0]
            }

    # Inserisce la nuova posizione inviata dal dispositivo
    def communicate_position(self, message):

        position_id = self.postgres.insert_new_position(message["longitude"], message["latitude"], message["activity"],
                                                        message["session_id"])

        if position_id is not None:
            return {
                "result": True,
                "message": "Position successfully inserted."
            }
        else:
            return {
                "result": False,
                "type": "Error",
                "message": "Inserting position has failed."
            }
