import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin import exceptions


# Firebase class allows Python to communicate with the Google's Firebase service
# to send notifications
# https://firebase.google.com/docs/cloud-messaging/send-message
# https://firebase.google.com/docs/reference/admin/python/firebase_admin.messaging#apnsconfig
class Firebase:

    def __init__(self):
        # Client inizialization
        try:
            # https://firebase.google.com/docs/admin/setup#initialize-sdk
            cred = credentials.Certificate("context-aware-systems-firebase-adminsdk-7b688-fb6fc1ce75.json")
            firebase_admin.initialize_app(cred)
            print("Successfully connected to Firebase service")
            # print(firebase_admin)
        except:
            print("ERROR connecting to Firebase service")

    def send_notification(self, device_operating_system, registration_token, body):

        body = (bytes(body, 'utf-8')).decode("utf-8")

        if device_operating_system == "ios":
            try:
                message = messaging.Message(
                    token=registration_token,  # This registration token comes from the client FCM SDKs.
                    apns=messaging.APNSConfig(
                        # https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/PayloadKeyReference.html#//apple_ref/doc/uid/TP40008194-CH17-SW5
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                alert=messaging.ApsAlert(
                                    title="C'è un nuovo messaggio per te",
                                    body=body
                                ),
                                badge=1,
                                sound='bingbong.aiff'
                            ),
                        ),
                    ),
                )

                # Send a message to the device corresponding to the provided registration token.
                response = messaging.send(message)
                return {
                    "result": True,
                    "message": "Notification successfully sent to " + response + ".",
                    "notification": {
                        "device_operating_system": device_operating_system,
                        "registration_token": registration_token,
                        "body": body
                    }
                }

            except messaging.UnregisteredError as ex:
                print('Registration token has been unregistered')
                print("UnregisteredError error: ", sys.exc_info()[0])
            except exceptions.InvalidArgumentError as ex:
                print('One or more arguments are invalid (maybe registration_token?)')
                print("InvalidArgumentError error: ", sys.exc_info()[0])
            except exceptions.FirebaseError as ex:
                print('Something else went wrong')
                print("FirebaseError error: ", sys.exc_info()[0])
            except:
                print("Unexpected error: ", sys.exc_info()[0])
                return {
                    "result": False,
                    "type": "Error",
                    "message": "Notification sending failed."
                }
        else:
            return {
                "result": False,
                "type": "Error",
                "message": "Device's operating system not supported."
            }
