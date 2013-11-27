import BaseHTTPServer

class SpotifyHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    data_function = lambda: ""

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.data_function())
