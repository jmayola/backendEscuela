from flask import Flask, request, jsonify, make_response, sessions, session
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
CORS(app,supports_credentials=True)

app.secret_key = b'_5#y2L"F4Q8DsasDajwuh12z\n\xec]/'

# Conexión a la base de datos
def db_connection():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="reports",
            port=3306
        )
        return db
    except mysql.connector.Error as excp:
        print(f"Error de conexión a la base de datos: {excp}")
        return None

# Ejecutar consultas en la base de datos
def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    db = db_connection()
    if db is None:
        return None

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, params)
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = None
        db.commit()
        cursor.close()
        db.close()
        return result
    except mysql.connector.Error as excp:
        print(f"Error ejecutando la consulta: {excp}")
        return None

# Autenticación de usuarios
def auth(username, passwd):
    query = "SELECT username, user_type, password FROM usuarios WHERE username = %s"
    result = execute_query(query, (username,), fetch_one=True)

    if not result or not check_password_hash(result["password"], passwd):
        return None
    return result['user_type']

# Cambiar tipo de usuario
@app.route("/user", methods=["PUT"])
def changeUser():
    username = request.json.get("username")
    user_type = request.json.get("user_type")
    return {"message": f"Changed user type to {user_type}"}, 201

@app.route("/users", methods=["GET"])
def getUsers():
    user_type = session["user_type"]
    print(user_type)
    if not user_type:
        return {"message": f"Debes de registrarte"}, 403
    if user_type == "visitor":
        return {"message": f"No puedes realizar cambios."}, 403
    if user_type == "docente":
        return execute_query("SELECT id_user,username,dni,nacimiento,user_type FROM usuarios WHERE user_type = 'visitor'",fetch_all=True), 200
    if user_type == "director":
        return execute_query("SELECT id_user,username,dni,nacimiento,user_type FROM usuarios WHERE user_type = 'visitor' OR user_type = 'docente'",fetch_all=True), 200
    if user_type == "admin":
        return execute_query("SELECT id_user,username,dni,nacimiento,user_type FROM usuarios WHERE user_type = 'visitor' OR user_type = 'docente' OR user_type = 'director'",fetch_all=True), 200
    else:
        return {"message": f"Error en el servidor."}, 500

# Inicio de sesión
@app.route("/login", methods=["POST"])
def login():
    user = request.cookies.get("session")
    if user:
        return f'Ya estas ingresado {session["username"]}', 403
    username = request.json.get("username")
    password = request.json.get("password")

    if not username or not password:
        return {"error": "Ingresa usuario y contraseña"}, 400

    user_type = auth(username, password)
    if user_type:
        res = make_response({"message": "Login successful", "user_type": user_type}, 200)
        session["username"] = username
        session["user_type"] = user_type
        return res
    else:
        return {"error": "El usuario o la contraseña son incorrectos."}, 401

# Registro de usuarios
@app.route("/register", methods=["POST"])
def register():
    if request.cookies.get("session"):
        return f"ya ha ingresado al sistema como {session['username']}", 403
    username = request.json.get("username")
    password = request.json.get("password")
    repassword = request.json.get("repassword")
    birthday = request.json.get("birthday")
    dni = request.json.get("dni")

    if not username or not birthday or not repassword or not dni:
        return {"error": "All fields are required"}, 403

    if password != repassword:
        return {"error": "Las contraseñas no coinciden"}, 400

    hashed_password = generate_password_hash(password)
    query = """
        INSERT INTO usuarios (username, password, dni, nacimiento) 
        VALUES (%s, %s, %s, %s)
    """
    params = (username, hashed_password, dni, birthday)
    result = execute_query(query, params)
    session["username"] = username
    session["user_type"] = "visitor"
    if result is None:
        return {"error": "Error registrando el usuario"}, 500
    return {"message": "Usuario registrado exitosamente"}, 201

# Inicio de sesión con Google
@app.route("/google-login", methods=["POST"])
def google_login():
    user_data = request.json
    email = user_data.get("email")
    username = user_data.get("username")
    password = generate_random_token()

    if not email or not username:
        return {"error": "Email y nombre de usuario son obligatorios"}, 400

    query = "SELECT user_email FROM users WHERE user_email = %s"
    existing_user = execute_query(query, (email,), fetch_one=True)

    if existing_user:
        return {"message": "Usuario ya registrado"}, 200

    query = """
        INSERT INTO users (user_name, user_alias, user_email, user_password, user_type)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (username, username, email, generate_password_hash(password), 'google_user')
    result = execute_query(query, params)

    if result is None:
        return {"error": "Error registrando el usuario"}, 500
    return {"message": "Usuario registrado vía Google"}, 201

# Manejo de reportes
@app.route("/reports", methods=["POST", "GET"])
def repMet():
    if request.method == "POST":
        return registerRep()
    elif request.method == "GET":
        return verRep()
    return {"error": "Ha ocurrido un error"}, 500

def registerRep():
    # Extraer datos del reporte
    data = request.json
    fields = ["lat", "lng", "calle", "altura", "localidad", "descripcion", "categoria"]
    # fields = ["lat", "lng", "calle", "altura", "localidad", "descripcion", "categoria", "escuela"]
    print(data)
    # Validar que todos los campos estén presentes
    if not all(data.get(field) for field in fields):
        return {"error": "Todos los campos son obligatorios"}, 403

    query = """
        INSERT INTO reports (calle, altura, localidad, lat, lng, descripcion, categoria, escuela) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        data["calle"],
        data["altura"],
        data["localidad"],
        data["lat"],
        data["lng"],
        data["descripcion"],
        data["categoria"],
        "EEST N°1"
        #data["escuela"]  # Se toma el valor del cuerpo de la solicitud
    )
    result = execute_query(query, params)
    print(result)
    if result is None:
        # return {"error": "Error registrando el reporte"}, 500
        return {"message": "Reporte ingresado exitosamente"}, 201
def verRep():
    query = """
    SELECT lat, lng, descripcion, escuela, fecha_reporte, categoria, user_id 
    FROM reports
    """
    result = execute_query(query, fetch_all=True)

    if result is None:
        return {"error": "Error obteniendo reportes"}, 500
    return jsonify(result), 200

# Registro de escuelas
@app.route("/register_school", methods=["POST"])
def register_school():
    # Obtener los datos de la solicitud
    school_name = request.json.get("school_name")
    address = request.json.get("address")
    city = request.json.get("city")
    phone = request.json.get("phone")
    email = request.json.get("email")

    # Validar que todos los campos estén presentes
    if not all([school_name, address, city, phone, email]):
        return {"error": "Todos los campos son obligatorios"}, 403

    # Insertar la escuela en la base de datos
    query = """
        INSERT INTO schools (school_name, address, city, phone, email) 
        VALUES (%s, %s, %s, %s, %s)
    """
    params = (school_name, address, city, phone, email)
    result = execute_query(query, params)

    # Manejo de errores o confirmación del registro
    if result is None:
        return {"error": "Error registrando la escuela"}, 500
    return {"message": "Escuela registrada exitosamente"}, 201

