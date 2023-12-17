import http.server
import threading
import webbrowser
import time
import sys

PORT = 8000
DIRECTORY = "ui/dist"
URL = f'http://localhost:{PORT}'

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    httpd = http.server.HTTPServer(("", PORT), Handler)
    httpd.serve_forever()

def show_result():
    threading.Thread(target=start_server).start()
    webbrowser.open_new(URL)

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)
