import http.server
import socketserver
import urllib.request

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            # Forward the request to the target server
            url = self.path
            with urllib.request.urlopen(url) as response:
                self.send_response(response.status)
                self.send_header('Content-type', response.headers['Content-Type'])
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_error(500, f"Error: {e}")

    def do_POST(self):
        try:
            # Forward the request to the target server
            url = self.path
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            req = urllib.request.Request(url, data=post_data, method='POST')
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                self.send_header('Content-type', response.headers['Content-Type'])
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_error(500, f"Error: {e}")

def run(server_class=http.server.HTTPServer, handler_class=ProxyHTTPRequestHandler, port=8888):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting proxy server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()