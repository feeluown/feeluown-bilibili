import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from PyQt5.QtCore import QThread
from urllib3.util import parse_url


class GeetestHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = parse_url(self.path)
        match url.path:
            case '/challenge':
                self.send_response(200, "OK")
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with (Path(__file__).parent / 'index.html').open('r') as f:
                    self.wfile.write(f.read().encode())
                    self.wfile.flush()
                return
            case '/back':
                data = parse_qs(url.query)
                validate = data['validate'][0]
                seccode = data['seccode'][0]
                challenge = data['challenge'][0]
                token = data['token'][0]
                type_ = data['type'][0]
                self.server._instance.auth_success.emit(
                    validate, seccode, challenge, token, type_)
                self.send_response(200, "OK")
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write("You can safely close now!".encode())
                self.wfile.flush()
                return
        self.send_response(404, "Not Found")
        self.end_headers()


class GeetestHttpServer(HTTPServer):
    def __init__(self, address, handler, instance):
        super().__init__(address, handler)
        self._instance = instance


class GeetestAuthServer(QThread):
    def __init__(self, port: int, instance):
        super().__init__()
        self._port = port
        self._instance = instance

    def run(self) -> None:
        self._server = GeetestHttpServer(('', self._port), GeetestHttpHandler, self._instance)
        self._server.serve_forever()

    def stop(self):
        self._server.shutdown()


if __name__ == '__main__':
    thread = GeetestAuthServer(12900)
    thread.start()
    time.sleep(100000)
