class User:
    postgres = None

    def __init__(self, postgres):
        self.postgres = postgres

    def register(self, registration_token):
        user_id = self.postgres.create_new_user(registration_token)
        
        if user_id is not None:
            return {
                "result": True,
                "user_id": user_id
            }
        else:
            return {
                    "result": False,
                    "type": "Error",
                    "message": "User registration has failed."
                }
