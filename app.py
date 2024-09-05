import mysql.connector
from flask import Flask,request,make_response,abort,session
from flask_cors import CORS
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
app = Flask(__name__)
CORS(app)
app.secret_key = b'_5#y2L"F4Q8DsasDajwuh12z\n\xec]/'
@app.route("/login")
def login():
    print("post")
    if request.method == "OPTIONS":
        return 200
    if request.method == "POST" and auth(request.form["username"],request.form["password"]):
        # res = make_response()
        # res.set_cookie("username",hash(request.form["username"]))
        session["username"] = request.form["username"]
        print("session")
        return "oasodi"
    else:
        return abort(505)
