from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import json

# Look up the full hostname using gethostbuaddr() is too slow.
import BaseHTTPServer
def not_insance_address_string(self):
    host, port = self.client_address[:2]
    # Just only return host.
    return '%s (no getfqdn)' % host
BaseHTTPServer.BaseHTTPRequestHandler.address_string = not_insance_address_string

class Handler(BaseHTTPRequestHandler):
    content = {}
    intvl = 10
    pollsters = []
    
    # timestamp of get from host
    ts_get = None

    def do_GET(self):
        if self.path == '/getdata':
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            print '%s - %s' %(Handler.content['timestamp'], Handler.ts_get)
            if Handler.content['timestamp'] != Handler.ts_get:
                Handler.content['status'] = 'NORMAL'
                Handler.ts_get = Handler.content['timestamp']
            else:
                Handler.content['status'] = 'POLLING_TIMEOUT'
                Handler.content['data'] = {}
            obj_str = json.dumps(Handler.content)
            self.send_header("Content-Length", str(len(obj_str)))
            self.end_headers()
            self.wfile.write(obj_str.encode())
            self.wfile.write('\n')
        elif self.path == '/getintvl':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(Handler.intvl)
            self.wfile.write('\n')
        elif self.path == '/getpollsters':
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            poll_str = json.dumps(Handler.pollsters)
            self.send_header("Content-Length", str(len(poll_str)))
            self.end_headers()
            self.wfile.write(poll_str.encode())
            self.wfile.write('\n')
        elif self.path == '/rstsvr':
            pingPopen = subprocess.Popen(args='python PollManager.py restart', shell=True)
            self.send_response(200)
            self.end_headers()
            self.wfile.write('Restart server ok!')
            self.wfile.write('\n')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/setdata':
            length = self.headers['content-length']
            data = self.rfile.read(int(length))
            Handler.content = eval(data.decode())
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(Handler.content))
            self.wfile.write('\n')
        elif self.path == '/setintvl':
            length = self.headers['content-length']
            data = self.rfile.read(int(length))
            Handler.intvl = eval(data.decode())
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(Handler.intvl))
            self.wfile.write('\n')
        elif self.path == '/setpollsters':
            length = self.headers['content-length']
            data = self.rfile.read(int(length))
            Handler.pollsters = eval(data.decode())
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(Handler.pollsters))
            self.wfile.write('\n')
        else:
            self.send_response(404)
            self.end_headers()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    server = ThreadedHTTPServer(('0.0.0.0', 8655), Handler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
