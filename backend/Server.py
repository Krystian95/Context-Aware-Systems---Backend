# https://gist.github.com/bradmontgomery/2219997

import argparse
import cgi
import json
import cgi
from http.server import HTTPServer, BaseHTTPRequestHandler
from backend.Postgres import Postgres
from backend.Firebase import Firebase


def format_response(response_json):
    return json.dumps(response_json).encode(encoding='UTF-8')


def print_json(title, json_to_print):
    print(title + " = " + json.dumps(json_to_print, indent=4))


class Server(BaseHTTPRequestHandler):
    postgres = Postgres()
    firebase_sdk = Firebase()

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({'message': 'Hello world!'}))

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))

        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        # read the message and convert it into a dictionary
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))

        print("message = " + json.dumps(message, indent=4))
        response = None

        if "action" not in message:
            response = {
                "result": False,
                "type": "Error",
                "message": "Parameter 'action' not specified"
            }
            self.send_response(400)
            self.end_headers()
        else:
            action = message['action']
            if action == "register":
                response = self.action_register(message)
            elif action == "communicate-position":
                response = self.action_communicate_position(message)
            elif action == "test-query":
                response = self.test_query()
            elif action == "test-notification":
                response = self.send_test_notification(message)
            else:
                response = {
                    "result": False,
                    "type": "Error",
                    "message": "Operation '" + action + "' not recognized"
                }
                self.send_response(400)
                self.end_headers()

        print_json("response", response)

        self._set_headers()
        self.wfile.write(format_response(response))

    # Riceve il registration_token e verifica se esiste già nel db.
    # Se esiste già ritorna l'id utente del rispettivo registration_token,
    # altrimenti crea una nuova entry nel db e ritorna il suo id.
    def action_register(self, params):

        response = {
            "result": True,
            "user_id": "a4tvety5byrty5rs4e"
        }
        return response

    # Salva nel db la entry che gli viene comunicata.
    def action_communicate_position(self, params):
        response = {
            "result": True,
            'message': "Position correctly received and saved"
        }
        return response

    def send_test_notification(self, message):
        device_operating_system = "ios"
        title = "Sei entrato in una zona d'interesse per [walk]"
        body = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        return self.send_notification(device_operating_system, message['registration_token'], title, body)

    def send_notification(self, device_operating_system, registration_token, title, body):
        return self.firebase_sdk.send_notification(device_operating_system, registration_token, title, body)

    def test_query(self):
        self.postgres.do_sample_query()
        return {
            "result": True,
            'message': "Position correctly received and saved"
        }


def run(server_class=HTTPServer, handler_class=Server, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Python HTTP server listening on {addr}:{port}\n")
    httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)
