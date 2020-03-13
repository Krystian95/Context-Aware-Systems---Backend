import random
import string


class Utils:

    def check_parameters_exists(self, params, params_needed):
        for param in params_needed:
            print("Checking param:", param)
            if param not in params:
                print("Param NOT existing:", param)
                return {
                    "result": False,
                    "type": "Error",
                    "message": "Mandatory parameter missing: {" + param + "}.",
                }
        print("ALL prams exist")
        return True

    # Generates a session_id(random string of 128 chars)
    def generate_new_session_id(self):
        stringLength = 128
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))
