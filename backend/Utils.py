import random
import string
import datetime
from datetime import datetime
import numpy as np


class Utils:
    datetime_format = "%Y-%m-%d %H:%M:%S.%f"

    # Controlla che tutti i parametri richiesti siano presenti nel messaggio
    def check_parameters_exists(self, params, params_needed):
        for param in params_needed:
            if param not in params:
                return {
                    "result": False,
                    "type": "Error",
                    "message": "Mandatory parameter missing: {" + param + "}.",
                }
        return True

    # Genera un nuovo session_id
    def generate_new_session_id(self, existing_session):
        session_id = None
        session_id_free = False

        while session_id_free is not True:
            session_id = self.get_random_string(128)
            if len(existing_session) > 1:
                values = np.array(existing_session)
                existing_session_ids = values[..., 0]
                if session_id not in existing_session_ids:
                    session_id_free = True
            else:
                session_id_free = True

        return session_id

    # Genera una string casuale della lunghezza richiesta
    def get_random_string(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    # Ritorna il datetime current nel formato "%Y-%m-%d %H:%M:%S.%f"
    def get_current_datetime(self):
        return datetime.now()

    # Ritorna la differenza in minuti tra due date
    def get_datetime_difference_in_minutes(self, date_from, date_to):
        return (date_to - date_from).seconds / 60
