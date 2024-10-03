from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string

app = Flask(__name__)
CORS(app)
app.secret_key = b'_5#y2L"F4Q8DsasDajwuh12z\n\xec]/'

# Función de autenticación
def auth(username, passwd):
    """Define si un usuario puede iniciar sesión o no"""
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="flask_user",
            password="cosa222",
            database="classpanner",
            port=3306
        )
        cursor = db.cursor(dictionary=True)
        query = "SELECT username, user_type, password FROM usuarios WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        cursor.close()
        db.close()

        print(f"Auth result for {username}: {result}")  # Debugging

        if not result or not check_password_hash(result["password"], passwd):
            return None
        return result['user_type']
    except mysql.connector.Error as excp:
        print(f"Error de conexión a la base de datos: {excp}")
        return None

@app.route("/user", methods=["PUT"])
def changeUser():
    username = request.json.get("username")
    user_type = request.json.get("user_type")
    print(f"Changing user {username} to type {user_type}")  # Debugging
    print(session.values())
    return {"message": f"Changed user type to {user_type}"}, 201

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    print(f"Login attempt for {username}")  # Debugging

    if not username or not password:
        return {"error": "Ingresa usuario y contraseña"}, 400

    user = auth(username, password)
    if user:
        session["username"] = username
        session["user_type"] = user
        print(f"Login successful for {username}, user type: {user}")  # Debugging
        return {"message": "Login successful", "user": user}, 200
    else:
        print(f"Login failed for {username}")  # Debugging
        return {"error": "El usuario o la contraseña son incorrectos."}, 401

@app.route("/register", methods=["POST"])
def register():
    username = request.json.get("username")
    password = request.json.get("password")
    birthday = request.json.get("birthday")
    repassword = request.json.get("repassword")
    dni = request.json.get("dni")

    print(f"Register attempt for {username}")  # Debugging

    if not username or not birthday or not repassword or not dni:
        return {"error": "All fields are required"}, 403

    if password != repassword:
        return {"error": "Las contraseñas no coinciden"}, 400

    hashed_password = generate_password_hash(password)

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="flask_user",
            password="cosa222",
            database="classpanner",
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
        print(f"User {username} registered successfully")  # Debugging
        return {"message": "User registered successfully"}, 201
    except mysql.connector.IntegrityError:
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

    print(f"Google login attempt for {username}, email: {email}")  # Debugging

    if not email or not username:
        return {"error": "Email and username are required"}, 400

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="flask_user",
            password="cosa222",
            database="classpanner",
            port=3306
        )
        cursor = db.cursor()
        query = "SELECT user_email FROM users WHERE user_email = %s"
        cursor.execute(query, (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"User already exists: {existing_user}")  # Debugging
            return {"message": "User already exists"}, 200

        query = """
        INSERT INTO users (user_name, user_alias, user_email, user_password, user_type)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (username, username, email, generate_password_hash(password), 'google_user'))
        db.commit()
        cursor.close()
        db.close()
        print(f"User {username} registered successfully via Google")  # Debugging
        return {"message": "User registered successfully via Google"}, 201
    except mysql.connector.Error as excp:
        print(f"Error registrando usuario: {excp}")
        return {"error": "Error registering user"}, 500

@app.route("/escuela", methods=["POST", "GET"])
def mainEscuela():
    if request.method == "POST":
        print("POST request to /escuela")  # Debugging
        return registrarEscuela()
    elif request.method == "GET":
        print("GET request to /escuela")  # Debugging
        return verEscuelas()
    return {"error": "la consulta no es valida"}, 500

def registerRep():
    lat = request.json.get("lat")
    lng = request.json.get("lng")
    print(f"lat: {lat}, lng: {lng}")
    # Lugar
    calle = request.json.get("calle")
    altura = request.json.get("altura")
    localidad = request.json.get("localidad")
    # Mapa
    lat = request.json.get("lat")
    lng = request.json.get("lng")
    # Categoria
    descripcion = request.json.get("reporte")
    categoria = request.json.get("categoria")
    escuela = "prueba"

    print(f"Registering report: {calle}, {altura}, {localidad}, {lat}, {lng}, {descripcion}, {categoria}, {escuela}")  # Debugging

    if not lat or not categoria or not descripcion or not lng or not localidad or not altura or not calle or not escuela:
        return {"error": "Se requiere ingresar todos los campos"}, 403

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="flask_user",
            password="cosa222",
            database="classpanner",
            port=3306
        )
        cursor = db.cursor()
        query = """
        INSERT INTO reports (calle, altura, localidad, lat, lng, descripcion, categoria, escuela) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (calle, altura, localidad, lat, lng, descripcion, categoria, escuela))
        db.commit()
        cursor.close()
        db.close()
        print("Report registered successfully")  # Debugging
        return {"message": "Reporte Ingresado"}, 201
    except mysql.connector.Error as excp:
        print(f"Error ingresando el reporte: {excp}")
        return {"error": "Error registrando el reporte"}, 500

def verRep():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="flask_user",
            password="cosa222",
            database="classpanner",
            port=3306
        )
        cursor = db.cursor()
        query = "SELECT lat, lng, descripcion FROM reports"
        cursor.execute(query)
        res = cursor.fetchall()
        cursor.close()
        db.close()
        print(f"Retrieved reports: {res}")  # Debugging
        return jsonify(res), 201
    except mysql.connector.Error as excp:
        print(f"Error ingresando el reporte: {excp}")
        return {"error": "Error registrando el reporte"}, 500

@app.route("/reports", methods=["POST", "GET"])
def repMet():
    if request.method == "POST":
        print("POST request to /reports")  # Debugging
        return registerRep()
    elif request.method == "GET": 
        print("GET request to /reports")  # Debugging
        return verRep()
    return {"error": "ha habido un error"}, 500

def verEscuelas():
    schoolcue = request.args.get('cue', default="", type="string")
    schoolid = request.args.get('id', default=0, type="int")
    localidad = request.args.get('localidad', default="", type="string")
    
    print(f"Querying schools with cue: {schoolcue}, id: {schoolid}, localidad: {localidad}")  # Debugging

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="flask_user",
            password="cosa222",
            database="classpanner",
            port=3306
        )
        cursor = db.cursor(dictionary=True)
        if schoolcue:
            query = "SELECT * FROM schools WHERE cue = %s"
            cursor.execute(query, (schoolcue,))
        elif schoolid:
            query = "SELECT * FROM schools WHERE id = %s"
            cursor.execute(query, (schoolid,))
        elif localidad:
            query = "SELECT * FROM schools WHERE localidad = %s"
            cursor.execute(query, (localidad,))
        else:
            query = "SELECT * FROM schools"
            cursor.execute(query)

        res = cursor.fetchall()
        cursor.close()
        db.close()
        print(f"Retrieved schools: {res}")  # Debugging
        return jsonify(res), 200
    except mysql.connector.Error as excp:
        print(f"Error obteniendo las escuelas: {excp}")
        return {"error": "Error obteniendo las escuelas"}, 500

@app.route("/escuelas", methods=["POST"])
def registrar_escuela():
  print("registrar_escuela llamado")
  print("Request JSON:", request.json)
  nombre = request.json.get("nombreEstablecimiento")
  director = request.json.get("director")
  calle = request.json.get("calle")
  altura = request.json.get("altura")
  localidad = request.json.get("localidad")
  cue = request.json.get("cue")
  latitud = request.json.get("latitud")
  longitud = request.json.get("longitud")
  docentes = request.json.get("docentes")
  cursos = request.json.get("cursos")

  print(f"Registering school: {nombre}, director: {director}, calle: {calle}, altura: {altura}, localidad: {localidad}, cue: {cue}, latitud: {latitud}, longitud: {longitud}, docentes: {docentes}, cursos: {cursos}")

  if not nombre or not director or not calle or not altura or not localidad or not cue or not latitud or not longitud:
    print("Error: Campos requeridos no ingresados")
    return {"error": "Se requiere ingresar todos los campos"}, 403

  try:
    db = mysql.connector.connect(
      host="localhost",
      user="flask_user",
      password="cosa222",
      database="classpanner",
      port=3306
    )
    print("Conexión a la base de datos establecida")
    cursor = db.cursor()
    query = """
    INSERT INTO escuelas (nombre, director, calle, altura, localidad, cue, lat, lng) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    print("Ejecutando query")
    cursor.execute(query, (nombre, director, calle, altura, localidad, cue, latitud, longitud))
    print("Query ejecutado")
    db.commit()
    print("Cambios confirmados")
    cursor.close()
    db.close()
    print("Conexión a la base de datos cerrada")
    print("School registered successfully")
    return {"message": "Escuela registrada correctamente"}, 201
  except mysql.connector.Error as excp:
    print(f"Error registrando la escuela: {excp}")
    return {"error": "Error registrando la escuela"}, 500# Generador de token aleatorio
def generate_random_token(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

if __name__ == "__main__":
    app.run(debug=True)
