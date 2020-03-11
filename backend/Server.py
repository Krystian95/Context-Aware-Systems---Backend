# https://gist.github.com/bradmontgomery/2219997

import argparse
import cgi
import json
import cgi
from http.server import HTTPServer, BaseHTTPRequestHandler
from backend.Postgres import Postgres


def format_response(response_json):
    return json.dumps(response_json).encode(encoding='UTF-8')


def print_json(title, json_to_print):
    print(title + " = " + json.dumps(json_to_print, indent=4))


class Server(BaseHTTPRequestHandler):

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

        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))

        print("message = " + json.dumps(message, indent=4))
        response = None

        if "action" not in message:
            response = {
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
            else:
                response = {
                    "type": "Error",
                    "message": "Operation '" + action + "' not recognized"
                }
                self.send_response(400)
                self.end_headers()

        response['message'] = "Position correctly received and saved"

        print_json("response", response)

        self._set_headers()
        self.wfile.write(format_response(response))

    # Riceve il registration_token e verifica se esiste già nel db.
    # Se esiste già ritorna l'id utente del rispettivo registration_token,
    # altrimenti crea una nuova entry nel db e ritorna il suo id.
    def action_register(self, params):

        postgres = Postgres()
        postgres.make_sample_query()

        response = {
            "result": "true",
            "user_id": "a4tvety5byrty5rs4e"
        }
        return response

    # Salva nel db la entry che gli viene comunicata.
    def action_communicate_position(self, params):
        response = {
            "result": "true"
        }
        return response


def run(server_class=HTTPServer, handler_class=Server, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
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
