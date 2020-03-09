import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

# https://firebase.google.com/docs/admin/setup#initialize-sdk
cred = credentials.Certificate("context-aware-systems-firebase-adminsdk-7b688-fb6fc1ce75.json")
firebase_admin.initialize_app(cred)

# This registration token comes from the client FCM SDKs.
registration_token = 'da6o5rofaUApmlrZ0aoE1s:APA91bE2bS9HM7wad5gm_7qU8lgQHPApX3-dUrO6oZ47suusGBzn7UtDmj4T6UPxuLyNFBMONvCb3i5zJXnLRNtKn_Az7o06vmdkBLZkLqjO-GeQQlUsqoNB1OjMZQjF_9bbzUWyoa2P'

# https://firebase.google.com/docs/cloud-messaging/send-message
# https://firebase.google.com/docs/reference/admin/python/firebase_admin.messaging#apnsconfig
message = messaging.Message(
    token=registration_token,
    # https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/PayloadKeyReference.html#//apple_ref/doc/uid/TP40008194-CH17-SW5
    apns=messaging.APNSConfig(
        payload=messaging.APNSPayload(
            aps=messaging.Aps(
                alert=messaging.ApsAlert(
                    title="Sei entrato in una zona d'interesse per [walk]",
                    body='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
                ),
                badge=1,
                sound='bingbong.aiff'
            ),
        ),
    ),
)

# Send a message to the device corresponding to the provided registration token.
response = messaging.send(message)
# Response is a message ID string.
print('Successfully sent message:', response)
