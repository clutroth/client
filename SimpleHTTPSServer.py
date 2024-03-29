import BaseHTTPServer, SimpleHTTPServer
import ssl

# openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout cert.pem
httpd = BaseHTTPServer.HTTPServer(('', 2812), SimpleHTTPServer.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket (httpd.socket, server_side=True, certfile='./cert.pem', keyfile='./cert.pem', ssl_version=ssl.PROTOCOL_SSLv3)
httpd.serve_forever()
