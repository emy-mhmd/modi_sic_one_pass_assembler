import http.server
import socketserver
import json
import onepass as p

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/get_variable':
            # Initialize the onepass objects
            f = p.File()
            one = p.Onepass()
            
            # Read the file and process data with onepass
            f.read_file()
            my_hteRecord = one.read_line(f)
            my_symbolTable = one.symboltable
            
            # Send both variables as JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response_data = {
                'my_variable': my_hteRecord,
                'my_symbolTable': my_symbolTable
            }
            self.wfile.write(json.dumps(response_data).encode())
        else:
            # Serve the static HTML file
            super().do_GET()

if __name__ == "__main__":
    PORT = 8000
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"click here ---> http://127.0.0.1:8000/" )
        httpd.serve_forever()
#Serving on port {PORT} 