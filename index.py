import mysql.connector
import http.server
import socketserver
class handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.headers)
with http.server.HTTPServer(('localhost',3000),handler) as httpd:
    print(httpd.server_name)
    httpd.serve_forever()
db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="reports",
        port=3306
        )
cursor = db.cursor()
cursor.execute("select * from users")
result = cursor.fetchall()
for x in result:
    print(x)

