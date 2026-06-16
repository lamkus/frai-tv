import http.server, socketserver, os
os.chdir(r'D:/remaike.TV/thumbnails_pilot')
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Private-Network','true')
        self.send_header('Access-Control-Allow-Methods','GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','*')
        super().end_headers()
    def do_OPTIONS(self):
        self.send_response(204); self.end_headers()
    def log_message(self,*a): pass
socketserver.TCPServer(('127.0.0.1',8766), H).serve_forever()
