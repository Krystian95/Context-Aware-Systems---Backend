from backend.Utils import Utils


class User:
    postgres = None
    firebase_sdk = None
    utils = Utils()
    # Memorizza le sessioni attive
    live_sessions = []
    minutes_to_wait_before_generate_new_session = {
        "walk": 6,
        "bike": 5,
        "car": 4
    }

    def __init__(self, postgres, firebase_sdk):
        self.postgres = postgres
        self.firebase_sdk = firebase_sdk

    # Verifica che una session_id sia valida
    def validate_session_id(self, session_id):
        print("live_sessions - BEFORE validate_session_id():")
        self.utils.print_array_of_json("Live sessions", self.live_sessions)
        for session in self.live_sessions:
            if session["session_id"] == session_id:
                return True

        return {
            "result": False,
            "type": "Error",
            "message": "The {session_id} provived is not valid. Please register again."
        }

    # Calcola la freschezza di una sessione.
    # Se l'ultimo update rilevato risale a più di x minuti fa
    # genera un nuovo session_id
    def check_freshness_session(self, session_id, activity):
        for session in self.live_sessions:
            if session["session_id"] == session_id:
                date_from = session["date_time"]
                date_to = self.utils.get_current_datetime()
                diff_in_minutes = self.utils.get_datetime_difference_in_minutes(date_from, date_to)
                if diff_in_minutes > self.minutes_to_wait_before_generate_new_session[activity]:  # Old session -> destroy and create new session for the same user_id
                    user_id = session["user_id"]
                    self.remove_session_by_user_id(user_id)
                    new_session_id = self.register_new_session(user_id)
                    print("NEW session_id GENERATED: " + new_session_id)
                    return new_session_id

        return False

    # Restituisce l'user_id di una specifica session_id
    def get_user_id_by_session_id(self, session_id):
        for session in self.live_sessions:
            if session["session_id"] == session_id:
                return session["user_id"]

        return None

    # Restituisce l'ultima posizione comunicata di una specifica session_id
    def get_previous_position_by_session_id(self, session_id):
        for session in self.live_sessions:
            if session["session_id"] == session_id:
                return session["previous_position"]

        return None

    # Elimina l'eventuale sessione già esistente di 'new_user_id'
    def remove_session_by_user_id(self, user_id):
        for session in self.live_sessions:
            if session["user_id"] == user_id:
                self.live_sessions.remove(session)
                return True

        return False

    # Aggiorna il datetime di ultimo utilizzo di una sessione
    def update_session_datetime(self, session_id):
        for session in self.live_sessions:
            if session["session_id"] == session_id:
                session["date_time"] = self.utils.get_current_datetime()
                return True

        return False

    # Memorizza l'ultima posizione comunicata
    def save_last_message_in_session(self, session_id, last_message):
        for session in self.live_sessions:
            if session["session_id"] == session_id:
                session["previous_position"] = last_message
                return True

        return False

    # Memorizza l'activity corrente
    def save_current_activity_in_session(self, session_id, current_activity):
        for session in self.live_sessions:
            if session["session_id"] == session_id:
                session["current_activity"] = current_activity
                return True

        return False

    # Ritorna l'activity memorizzata nella sessione
    def get_activity_in_session(self, session_id):
        for session in self.live_sessions:
            if session["session_id"] == session_id:
                return session["current_activity"]

        return False

    # Memorizza l'id del geofence attivato (se esiste)
    def save_current_geofence_triggered_in_session(self, session_id, id_geofence_triggered):
        for session in self.live_sessions:
            if session["session_id"] == session_id:
                session["current_id_geofence_triggered"] = id_geofence_triggered
                return True

        return False

    # Ritorna l'id del geofence attivato (se esiste) memorizzato nella sessione
    def get_id_geofence_triggered_in_session(self, session_id):
        for session in self.live_sessions:
            if session["session_id"] == session_id:
                return session["current_id_geofence_triggered"]

        return False

    # Ritorna se il geofence corrente è già stato triggerato
    def get_current_geofence_is_already_triggered_in_session(self, session_id):
        for session in self.live_sessions:
            if session["session_id"] == session_id:
                return session["current_geofence_is_already_triggered"]

        return False

    # Ritorna l'id del gruppo che ha già triggerato il geofence
    def get_current_geofence_triggered_by_group_id_in_session(self, session_id):
        for session in self.live_sessions:
            if session["session_id"] == session_id:
                return session["current_geofence_triggered_by_group_id"]

        return False

    # Salva se il geofence corrente è stato triggerato
    def save_current_geofence_is_already_triggered_in_session(self, session_id, group_id, is_already_triggered):
        for session in self.live_sessions:
            if session["session_id"] == session_id:
                session["current_geofence_triggered_by_group_id"] = group_id
                session["current_geofence_is_already_triggered"] = is_already_triggered
                return True

        return False

    # Registra una nuova sessione per uno specifico utente
    def register_new_session(self, user_id, old_position=[]):
        self.remove_session_by_user_id(user_id)
        session_id = self.utils.generate_new_session_id(self.live_sessions)
        now = self.utils.get_current_datetime()
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "date_time": now,
            "current_activity": None,
            "current_id_geofence_triggered": None,
            "current_geofence_is_already_triggered": False,
            "current_geofence_triggered_by_group_id": None,
            "previous_position": old_position,
        }
        self.live_sessions.append(session)
        print("live_sessions - AFTER register_new_session():")
        self.utils.print_array_of_json("Live sessions", self.live_sessions)
        return session_id

    # Riceve il registration_token e verifica se esiste già nel db,
    # se non esiste crea il nuovo utente.
    # In ogni caso ritorna un nuovo session_id
    def register(self, registration_token):

        # Check if the user is already registered, in this case return the user_id
        user_id = self.postgres.get_user_id_by_registration_token(registration_token)

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
            new_session_id = self.register_new_session(user_id)
            return {
                "result": True,
                "message": "A user is already registered for the same registration_token.",
                "session_id": new_session_id
            }

    # Inserisce la nuova posizione inviata dal dispositivo
    def communicate_position(self, message):

        message["session_id"] = message["properties"]["session_id"]
        message["activity"] = message["properties"]["activity"]
        message["position_id_device"] = message["properties"]["position_id_device"]
        message["position_id_group"] = message["properties"]["position_id_group"]
        message["latitude"] = message["geometry"]["coordinates"][0]
        message["longitude"] = message["geometry"]["coordinates"][1]
        
        user_id = self.get_user_id_by_session_id(message["session_id"])
        session_id = message["session_id"]

        if user_id is not None:
            # Activity changed
            last_position_changed = self.check_changed_activity(message["activity"], message["session_id"])
            if last_position_changed is not None:
                print("ACTIVITY CHANGED!")
                session_id = self.register_new_session(user_id, last_position_changed)
                # Inserisco un nuovo punto fittizio con: coordinate nuove ed activity e session_id vecchi
                self.postgres.insert_new_position(user_id, message["longitude"], message["latitude"],
                                                  last_position_changed["activity"],
                                                  last_position_changed["session_id"],
                                                  is_auto_generated=True)
            # New position
            position_id = self.postgres.insert_new_position(user_id, message["longitude"], message["latitude"],
                                                            message["activity"],
                                                            session_id,
                                                            is_auto_generated=None)

            if position_id is not None:
                # Notification
                geofence_triggered = self.postgres.position_inside_geofence(position_id, message["activity"])

                print("User is inside geofence:")
                print(geofence_triggered)

                if geofence_triggered is not None:
                    geofence_triggered_id = geofence_triggered[0]
                    previous_activity = self.get_activity_in_session(session_id)
                    previous_id_geofence_triggered = self.get_id_geofence_triggered_in_session(session_id)
                    last_position = self.get_previous_position_by_session_id(session_id)

                    print(last_position)

                    if last_position:
                        previous_position_id_group = last_position["properties"]["position_id_group"]
                    else:
                        previous_position_id_group = None

                    current_geofence_is_already_triggered = self.get_current_geofence_is_already_triggered_in_session(session_id)
                    current_geofence_triggered_by_group_id = self.get_current_geofence_triggered_by_group_id_in_session(session_id)

                    if (previous_activity is None or message["activity"] != previous_activity or geofence_triggered_id != previous_id_geofence_triggered) or ((current_geofence_is_already_triggered and current_geofence_triggered_by_group_id == message["position_id_group"]) and (previous_position_id_group == message["position_id_group"] or previous_position_id_group is None)):
                        self.save_current_geofence_is_already_triggered_in_session(session_id, message["position_id_group"], True)
                        geofence_triggered_message = geofence_triggered[1]
                        registration_token = self.postgres.get_registration_token_by_user_id(user_id)
                        response = self.firebase_sdk.send_notification("ios", registration_token,
                                                                       geofence_triggered_message, message["position_id_device"])
                        self.utils.print_json(response, "send_notification()")
                        self.save_current_geofence_triggered_in_session(session_id, geofence_triggered_id)
                        self.postgres.update_id_geofence_triggered_position(position_id, geofence_triggered_id)
                else:
                    self.save_current_geofence_triggered_in_session(session_id, None)
                    self.save_current_geofence_is_already_triggered_in_session(session_id, message["position_id_group"], False)

                self.save_current_activity_in_session(session_id, message["activity"])
                self.save_last_message_in_session(session_id, message)
                self.update_session_datetime(message["session_id"])

                return {
                    "result": True,
                    "message": "Position successfully inserted.",
                    "session_id": session_id,
                    "position_id_device": message["position_id_device"]
                }
            else:
                return {
                    "result": False,
                    "type": "Error",
                    "message": "Inserting position has failed."
                }

    def check_changed_activity(self, current_activity, session_id):
        last_position = self.get_previous_position_by_session_id(session_id)

        if last_position is not None and len(last_position) > 0:
            last_activity = last_position["activity"]
            if last_activity != current_activity:
                return last_position

        return None
