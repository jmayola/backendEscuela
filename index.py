import mysql.connector
import http.server
import http.cookies
import http.cookiejar
import json
def setCookieH():
    
    return cookie

def setCookie(name):
    cookie = http.cookies.SimpleCookie()
    cookie["cookie-id"] = hash(name)
    cookie["cookie-id"]["path"] = "/"
    cookie["cookie-id"]["max-age"] = 3600
    cookie["cookie-id"]["domain"] = "http://localhost:5173"
    return cookie.output()
print(setCookie("peña"))
cookies = http.cookiejar.CookieJar().
cookie = http.cookiejar.CookieJar().add_cookie_header(setCookie("peña"))

print(cookies)
print(cookie)

# database connection
def auth(username,passwd):
    """ Defines if a user can loggin or not """
    try:
        db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="reports",
                port=3306
                )
        cursor = db.cursor()
        cursor.execute("select username from users where username=%s && password=%s",(username,passwd))
        result = cursor.fetchone()
        if result is not None:
            return True
        else:
            return False
    except mysql.connector.Error as excp:
        print(excp)
        return False

# handler for requests
class handler(http.server.BaseHTTPRequestHandler):
    def _send_cors_headers(self):
      """ Sets headers required for CORS """
      self.send_header("Access-Control-Allow-Origin", "*")
      self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
      self.send_header("Access-Control-Allow-Headers", "Content-Length,Content-Type")
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    def do_HEAD(self):
        self._set_headers()
    def do_GET(self):
        print(self.headers)
        print(self.data)
        print(list(self))
    def do_POST(self):
        sizeH = self.headers['content-length']
        data = json.loads(self.rfile.read(int(sizeH)))
        print(data)
        if auth(data["username"],data["password"]):
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("content-type","application/json,text/plain,*/*")
            setCookieH()
            self.end_headers()
            self.wfile.write(bytes("Ingreso Exitoso","utf_8"))
        else:
            self.send_response(501)

    def do_OPTIONS(self):
        print("handle option:")
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
# server starter
with http.server.HTTPServer(('localhost',3000),handler) as httpd:
    httpd.serve_forever()

