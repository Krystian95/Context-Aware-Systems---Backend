import random
import string
import datetime
from datetime import datetime


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
    def generate_new_session_id(self):
        stringLength = 128
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    # Ritorna il datetime current nel formato "%Y-%m-%d %H:%M:%S.%f"
    def get_current_datetime(self):
        return datetime.now()

    # Ritorna la differenza in minuti tra due date
    def get_datetime_difference_in_minutes(self, date_from, date_to):
        return (date_to - date_from).seconds * 60
