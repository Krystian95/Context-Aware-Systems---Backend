
# https://gist.github.com/bradmontgomery/2219997

import argparse
import cgi
from http.server import HTTPServer, BaseHTTPRequestHandler


def print_post_params(form):
    for key in form.keys():
        print(key + " = " + form.getvalue(key))


def format_response(response):
    return str(response).encode("utf-8")


class Server(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(format_response(200))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )

        action = form.getvalue("action")
        params = form

        if action == "register":
            self.action_register(params)
        elif action == "communicate-position":
            self.action_communicate_position(params)
        else:
            print("Requested operation not recognized")

        self._set_headers()
        self.wfile.write(format_response(200))

    def action_register(self, params):
        print_post_params(params)

    def action_communicate_position(self, params):
        print_post_params(params)

        
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
