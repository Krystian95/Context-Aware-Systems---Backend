# https://gist.github.com/bradmontgomery/2219997

import argparse
import json
import cgi
from http.server import HTTPServer, BaseHTTPRequestHandler
from backend.Postgres import Postgres
from backend.Firebase import Firebase
from backend.User import User
from backend.Utils import Utils


def format_response(response_json):
    return json.dumps(response_json).encode(encoding='UTF-8')


def print_json(title, json_to_print):
    print(title + ": " + json.dumps(json_to_print, indent=4))


class Server(BaseHTTPRequestHandler):
    postgres = Postgres()
    firebase_sdk = Firebase()
    user = User(postgres)
    utils = Utils()

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
        response = {}

        check_params = self.check_parameters_exists(message, ["action"])
        if check_params is not True:
            response = check_params
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

    def check_parameters_exists(self, params, params_needed):
        check_params = self.utils.check_parameters_exists(params, params_needed)
        if check_params is True:
            return True
        else:
            self.send_response(400)
            self.end_headers()
            return check_params

    def action_register(self, message):
        check_params = self.utils.check_parameters_exists(message, ["registration_token"])
        if check_params is True:
            return self.user.register(message["registration_token"])
        else:
            return check_params

    def action_communicate_position(self, message):
        check_params = self.utils.check_parameters_exists(message, ["session_id", "longitude", "latitude", "activity"])
        if check_params is True:
            validate_session = self.user.validate_session_id(message["session_id"])
            if validate_session is True:
                return self.user.communicate_position(message)
            else:
                return validate_session
        else:
            return check_params


    def send_test_notification(self, message):
        return self.send_notification(message['device_operating_system'], message['registration_token'],
                                      message['title'], message['body'])

    def send_notification(self, device_operating_system, registration_token, title, body):
        return self.firebase_sdk.send_notification(device_operating_system, registration_token, title, body)

    def test_query(self):
        self.postgres.do_sample_query()
        return {
            "result": True
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
