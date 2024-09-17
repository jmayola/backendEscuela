from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8DsasDajwuh12z\n\xec]/'

# Configura CORS para permitir solicitudes desde el frontend
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Función de autenticación
def auth(user_alias, passwd):
    """Define si un usuario puede iniciar sesión o no"""
    try:
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

        if result and check_password_hash(result['user_password'], passwd):
            return result['user_type']
        else:
            return None
    except mysql.connector.Error as excp:
        print(f"Error de conexión a la base de datos: {excp}")
        return None

@app.route("/login", methods=["POST"])
def login():
    user_alias = request.form.get("user_alias")
    password = request.form.get("password")

    if not user_alias or not password:
        return {"error": "User alias and password are required"}, 400

    role = auth(user_alias, password)
    if role:
        session["user_alias"] = user_alias
        session["role"] = role
        return {"message": "Login successful", "role": role}, 200
    else:
        return {"error": "Unauthorized"}, 401

@app.route("/register", methods=["POST"])
def register():
    user_name = request.form.get("user_name")
    user_lastname = request.form.get("user_lastname")
    user_alias = request.form.get("user_alias")
    user_email = request.form.get("user_email")
    password = request.form.get("password")
    role = request.form.get("role")

    if not user_name or not user_lastname or not user_alias or not user_email or not password or not role:
        return {"error": "All fields are required"}, 400

    if role not in ['profesor', 'alumno', 'admin', 'director']:
        return {"error": "Role not allowed"}, 400

    hashed_password = generate_password_hash(password)

    try:
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

def generate_random_token():
    """Genera un token aleatorio para la contraseña"""
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

if __name__ == '__main__':
    app.run(debug=True)
