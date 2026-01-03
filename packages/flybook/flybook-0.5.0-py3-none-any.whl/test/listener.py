from flybook.listener import Listener
import dotenv
import os
import threading
import http.server
import socketserver

# 将POST请求的body打印出来


class POSTRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        print(post_data)
        self.send_response(200)
        self.end_headers()


dotenv.load_dotenv(".env.test")

PORT = int(os.getenv("LISTENER_PORT"))

listener = Listener(os.getenv("BOT_APP_ID"), os.getenv("BOT_APP_SECRET"),
                    f"http://localhost:{PORT}")
listener_thread = threading.Thread(target=listener)
listener_thread.start()


Handler = POSTRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.handle_request()
