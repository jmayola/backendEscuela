from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
app.secret_key = b'_5#y2L"F4Q8DsasDajwuh12z\n\xec]/'

# Configura CORS para permitir solicitudes desde el frontend

# Función de autenticación
def auth(username, passwd):
    """Define si un usuario puede iniciar sesión o no"""
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="reports",
            port=3306
        )
        cursor = db.cursor(dictionary=True)
        query = "SELECT username, user_type, password FROM usuarios WHERE username = %s OR password = %s"
        cursor.execute(query, (username,passwd))
        result = cursor.fetchone()
        if not result:
            return None
        cursor.close()
        db.close()

        if check_password_hash(result["password"],passwd):
            return result['user_type']
        else:
            return None
    except mysql.connector.Error as excp:
        print(f"Error de conexión a la base de datos: {excp}")
        return None

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    if not username or not password:
        return {"error": "Ingresa usuario y contraseña"}, 400
    user = auth(username, password)
    print(user)
    if user:
        session["username"] = username
        session["user_type"] = user
        return {"message": "Login successful", "user": user}, 200
    else:
        return {"error": "El usuario o la contraseña son incorrectos."}, 401

@app.route("/register", methods=["POST"])
def register():
    username= request.json.get("username")
    password= request.json.get("password")
    birthday= request.json.get("birthday")
    repassword= request.json.get("repassword")
    dni= request.json.get("dni")
    print(request.json)
    if not username or not birthday or not repassword or not dni:
        return {"error": "All fields are required"}, 403

    if password != repassword:
        return {"error": "Las contraseñas no coinciden"}, 400

    hashed_password = generate_password_hash(password)

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="reports",
            port=3306
        )
        cursor = db.cursor()
        query = """
        INSERT INTO usuarios (username, password, dni, nacimiento) 
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (username, hashed_password, dni, birthday))
        db.commit()
        cursor.close()
        db.close()
        return {"message": "User registered successfully"}, 201
    except mysql.connector.IntegrityError as excp:
        print(f"Error de integridad: {excp}")
        return {"error": "User alias or email already exists"}, 409
    except mysql.connector.Error as excp:
        print(f"Error registrando usuario: {excp}")
        return {"error": "Error registering user"}, 500

@app.route("/google-login", methods=["POST"])
def google_login():
    user_data = request.json
    email = user_data.get("email")
    username = user_data.get("username")
    password = generate_random_token()  # Genera una contraseña aleatoria

    if not email or not username:
        return {"error": "Email and username are required"}, 400

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="flask_user",
            password="1234",
            database="classpanner",
            port=3306
        )
        cursor = db.cursor()
        query = "SELECT user_email FROM users WHERE user_email = %s"
        cursor.execute(query, (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return {"message": "User already exists"}, 200

        query = """
        INSERT INTO users (user_name, user_alias, user_email, user_password, user_type)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (username, username, email, generate_password_hash(password), 'google_user'))
        db.commit()
        cursor.close()
        db.close()
        return {"message": "User registered successfully via Google"}, 201
    except mysql.connector.Error as excp:
        print(f"Error registrando usuario: {excp}")
        return {"error": "Error registering user"}, 500
    
@app.route("/escuela", methods=["POST", "GET"])
def mainEscuela():
    if request.method == "POST":
        return registrarEscuela()
    elif request.method == "GET":
        return verEscuelas()
    return {"error:" "la consulta no es valida"}, 500
    

def verEscuelas():
    schoolcue = request.args.get('cue',default="", type="string")
    schoolid = request.args.get('id',default=0, type="int")
    localidad = request.args.get('localidad',default="", type="string")
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="reports",
            port=3306
        )
        cursor = db.cursor()
        query = "SELECT * FROM escuelas WHERE cue = %s OR  id_school = %s OR localidad = %s"
        cursor.execute(query, (schoolcue,schoolid,localidad))

        return cursor.fetchall(),202
    
    except mysql.connector.Error as expc:
        return {"error":"Error al realizar la consulta: "+expc},403

def registrarEscuela ():
    school_data = request.json
    nombre = school_data.get("nombre")
    director = school_data.get("nombre")
    calle = school_data.get("calle")
    altura = school_data.get("altura")
    localidad = school_data.get("localidad")
    cue = school_data.get("cue")
    lat = school_data.get("lat")
    lng = school_data.get("lng")

    if not nombre or not lat or not lng or not calle or not altura or not localidad or not cue:
        return {"error": "Se requiere ingresar los campos"}, 400

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="reports",
            port=3306
        )
        cursor = db.cursor()
        query = "SELECT nombre FROM escuelas WHERE cue = %s"
        cursor.execute(query, (cue))
        existing_school = cursor.fetchone()

        if existing_school:
            return {"message": "La escuela ya existe"}, 200
        query = "INSERT INTO `escuelas` (`id_escuela`, `nombre`, `director`, `calle`, `altura`, `cue`, `localidad`, `lat`, `lng`) VALUES (NULL, '%s', '%s', '%s', '%i', '%s', '%s', '%f', '%f');"
        cursor.execute(query, (nombre,director,calle,altura,cue,localidad,lat,lng))
        db.commit()
        cursor.close()
        db.close()
        return {"message": "Escuela Registrada."}, 201
    except mysql.connector.Error as excp:
        print(f"Error registrando escuela: {excp}")
        return {"error": "Error registrando escuela"}, 500

def generate_random_token():
    """Genera un token aleatorio para la contraseña"""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

if __name__ == '__main__':
    app.run(debug=True)
