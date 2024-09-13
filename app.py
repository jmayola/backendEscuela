from flask import Flask, request, make_response, session
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash  # Para encriptar contraseñas

app = Flask(__name__)
CORS(app)
app.secret_key = b'_5#y2L"F4Q8DsasDajwuh12z\n\xec]/'

# Función de autenticación
def auth(user_alias, passwd):
    """Define si un usuario puede iniciar sesión o no"""
    try:
        # Conexión a la base de datos MariaDB
        db = mysql.connector.connect(
            host="localhost",
            user="flask_user",  
            password="1234",  
            database="classpanner",
            port=3306
        )
        cursor = db.cursor(dictionary=True)
        query = "SELECT user_alias, user_password, user_type FROM users WHERE user_alias = %s"
        cursor.execute(query, (user_alias,))
        result = cursor.fetchone()
        cursor.close()
        db.close()

        # Verifica la contraseña y el rol
        if result and check_password_hash(result['user_password'], passwd):
            return result['user_type']
        else:
            return None
    except mysql.connector.Error as excp:
        print(f"Error de conexión a la base de datos: {excp}")
        return None

# Ruta para el login
@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    if request.method == "POST":
        user_alias = request.form.get("user_alias")
        password = request.form.get("password")

        # Validación de entradas
        if not user_alias or not password:
            return "User alias and password are required", 400

        role = auth(user_alias, password)
        if role:
            session["user_alias"] = user_alias
            session["role"] = role
            return {"message": "Login successful", "role": role}, 200
        else:
            return "Unauthorized", 401

# Ruta para el registro de nuevos usuarios
@app.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    if request.method == "POST":
        user_name = request.form.get("user_name")
        user_lastname = request.form.get("user_lastname")
        user_alias = request.form.get("user_alias")
        user_email = request.form.get("user_email")
        password = request.form.get("password")
        role = request.form.get("role")  # Debe ser uno de: 'profesor', 'alumno', 'admin', 'director'

        # Validación de entradas
        if not user_name or not user_lastname or not user_alias or not user_email or not password or not role:
            return "All fields are required", 400
        
        # Validar el rol ingresado
        if role not in ['profesor', 'alumno', 'admin', 'director']:
            return "Role not allowed", 400

        # Encriptar la contraseña
        hashed_password = generate_password_hash(password)

        try:
            # Conexión a la base de datos MariaDB
            db = mysql.connector.connect(
                host="localhost",
                user="flask_user",  
                password="1234",  
                database="classpanner",
                port=3306
            )
            cursor = db.cursor()
            query = """
            INSERT INTO users (user_name, user_lastname, user_password, user_email, user_type, user_alias) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_name, user_lastname, hashed_password, user_email, role, user_alias))
            db.commit()
            cursor.close()
            db.close()
            return "User registered successfully", 201
        except mysql.connector.IntegrityError as excp:
            # Manejo de error si el alias o el correo ya existen
            print(f"Error de integridad: {excp}")
            return "User alias or email already exists", 409
        except mysql.connector.Error as excp:
            print(f"Error registrando usuario: {excp}")
            return "Error registering user", 500

if __name__ == '__main__':
    app.run(debug=True)
