from flask import Flask, request, jsonify, make_response, sessions, session
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
app = Flask(__name__)
CORS(app,supports_credentials=True)
load_dotenv()
app.secret_key = b'_5#y2L"F4Q8DsasDajwuh12z\n\xec]/'

# Conexión a la base de datos
def db_connection():
    try:
        db = mysql.connector.connect(
            host=os.getenv("host"),
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database"),
            port=os.getenv("port")
        )
        return db
    except mysql.connector.Error as excp:
        print(f"Error de conexión a la base de datos: {excp}")
        return None

# Ejecutar consultas en la base de datos
def execute_query(query, params=None, fetch_one=False, fetch_all=False):

    db = db_connection()

    if db is None:

        print("No se pudo establecer conexión con la base de datos.")

        return None


    try:

        cursor = db.cursor(dictionary=True)

        cursor.execute(query, params)

        

        if fetch_one:

            result = cursor.fetchone()

        elif fetch_all:

            result = cursor.fetchall()

            # print("Resultados obtenidos de la base de datos:", result)  # Verifica lo que se obtiene

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

# Obtencion de datos personales
def getUserData(username):
    query = "SELECT id_user,nacimiento FROM usuarios WHERE username = %s"
    result = execute_query(query, (username,), fetch_one=True)
    if result is not None:
        return {"id_user":result["id_user"],"nacimiento":result["nacimiento"],"username":session["username"],"user_type":session["user_type"]}
    else:
        return {"message":"La sesión no existe"}, 401
# Cambiar tipo de usuario
@app.route("/user", methods=["GET","PUT","DELETE"])
def userData():
    if request.method == "DELETE":
        return deleteSession()
    elif request.method == "PUT":
        return changeUser()
    elif request.method == "GET":
        if session:
            return getUserData(session["username"]), 202
            #return {"message":"La sesión no existe"}, 401
        else:
            return {"message":"La sesión no existe"}, 401

def changeUser():
    try:
        for user in request.json:
            username = user.get("id_user")
            user_type = user.get("user_type")
            query = "UPDATE `usuarios` SET `user_type` = %s WHERE `id_user` = %s;"
            result = execute_query(query,(user_type,username))
            print(result)

        return {"message": f"Changed user type"}, 201
    except Exception as e:
        return e,500

@app.route("/users", methods=["GET","DELETE"])
def userMethods():
    if request.method == "DELETE":
        return deleteSession()
    elif request.method == "GET":
        return getUsers()
def deleteSession():
    session.clear()
    return {"message":"Session cerrada"},202
def getUsers():
    user_type = session["user_type"]
    user_types_map = {
        "docente": "('visitor', 'alumno')",
        "director": "('visitor', 'alumno', 'docente')",
        "admin": "('visitor', 'alumno', 'docente', 'director')"
    }
    if not user_type:
        return {"message": "Debes de registrarte"}, 403
    if user_type not in user_types_map:
        return {"message": "Error en el servidor."}, 500
    allowed_user_types = user_types_map[user_type]
    query="SELECT u.id_user,u.username,u.dni,u.nacimiento,u.user_type FROM usuarios u WHERE u.user_type IN" + allowed_user_types
    print(query)
    if user_type == "visitor" or user_type == "alumno":
        return {"message": f"No puedes realizar cambios."}, 403
    if user_type == "docente":
        return execute_query(query,fetch_all=True), 200
    if user_type == "director":
        return execute_query(query,fetch_all=True), 200
    if user_type == "admin":
        return execute_query(query,fetch_all=True), 200
    else:
        return {"message": f"Error en el servidor."}, 500
def getUsersWithSchool():
    user_type = session["user_type"]
    user_types_map = {
        "docente": "('visitor', 'alumno')",
        "director": "('visitor', 'alumno', 'docente')",
        "admin": "('visitor', 'alumno', 'docente', 'director')"
    }
    if not user_type:
        return {"message": "Debes de registrarte"}, 403
    if user_type not in user_types_map:
        return {"message": "Error en el servidor."}, 500
    allowed_user_types = user_types_map[user_type]
    query="SELECT u.id_user,u.username,u.dni,u.nacimiento,u.user_type,e.nombre,e.localidad FROM usuarios u INNER JOIN escuela_det ed ON ed.id_user = u.id_user INNER JOIN escuelas e ON e.id_escuela = ed.id_escuela WHERE u.user_type IN" + allowed_user_types
    print(query)
    if user_type == "visitor" or user_type == "alumno":
        return {"message": f"No puedes realizar cambios."}, 403
    if user_type == "docente":
        return execute_query(query,fetch_all=True), 200
    if user_type == "director":
        return execute_query(query,fetch_all=True), 200
    if user_type == "admin":
        return execute_query(query,fetch_all=True), 200
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
    session["dni"] = dni
    if result is None:
        # return {"error": "Error registrando el usuario"}, 500
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
        return getreportesaceptar()
    return {"error": "Ha ocurrido un error"}, 500

def registerRep():
    # Extraer datos del reporte
    data = request.json
    fields = ["lat", "lng", "calle", "altura", "localidad", "escuela", "descripcion", "categoria", "reporte_del_problema","id_user"]
    # fields = ["lat", "lng", "calle", "altura", "localidad", "descripcion", "categoria", "escuela"]
    # Validar que todos los campos estén presentes
    if not all(data.get(field) for field in fields):
        return {"error": "Todos los campos son obligatorios"}, 403

    query = """
        INSERT INTO reports (calle, altura, localidad, lat, lng, descripcion, categoria, escuela, reporte_del_problema,user_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
    """
    params = (
        data["calle"],
        data["altura"],
        data["localidad"],
        data["lat"],
        data["lng"],
        data["descripcion"],
        data["categoria"],
        data["escuela"],
        data["reporte_del_problema"],
        data["id_user"]
    )
    result = execute_query(query, params)
    if result is None:
        # return {"error": "Error registrando el reporte"}, 500
        return {"message": "Reporte ingresado exitosamente"}, 201
def verRep():
    query = """
    SELECT lat, lng, descripcion, escuela, fecha_reporte, categoria, user_id,reporte_del_problema FROM reports
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

@app.route("/escuelas", methods=["GET","POST"])
def SchoolMethods():
    if request.method == "GET":
        return get_schools()
    elif request.method == "POST":
        return add_school()
def get_schools():
    try:
        query = "SELECT id_escuela, nombre, director, calle, altura, cue, localidad, lat, lng FROM escuelas"
        result = execute_query(query=query, fetch_all=True)

        if result is None:
            return {"error": "No se encontraron escuelas"}, 404

        escuelas = []
        for row in result:
            escuelas.append({
                "id_escuela": row['id_escuela'],
                "nombre": row['nombre'],
                "director": row['director'],
                "calle": row['calle'],
                "altura": row['altura'],
                "cue": row['cue'],
                "localidad": row['localidad'],
                "lat": row['lat'],
                "lng": row['lng']
            })

        return {"data": escuelas}, 200

    except Exception as e:
        print(f"Error al obtener las escuelas: {e}")
        return {"error": "Error interno del servidor"}, 500
    
def add_school():
    try:
        data = request.get_json()

        required_fields = ['nombre', 'director', 'calle', 'altura', 'cue', 'localidad', 'latitud', 'longitud']
        for field in required_fields:
            if field not in data:
                return {"error": f"Falta el campo: {field}"}, 400

        nombre = data['nombre']
        director = data['director']
        calle = data['calle']
        altura = data['altura']
        cue = data['cue']
        localidad = data['localidad']
        lat = data['latitud']
        lng = data['longitud']

        query = """
        INSERT INTO escuelas (nombre, director, calle, altura, cue, localidad, lat, lng)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        execute_query(query, (nombre, director, calle, altura, cue, localidad, lat, lng))
        query_id_escuela = "SELECT MAX(id_escuela) from escuelas"
        id_escuela = execute_query(query_id_escuela, fetch_one=True)
        # Paso 3: Insertar la relación en la tabla escuela_det
        query_escuela_det = """
        INSERT INTO escuela_det (id_escuela, user_id)
        VALUES (%s, %s)
        """
        execute_query(query_escuela_det, (id_escuela, director))
        return {"message": "Escuela agregada correctamente"}, 201

    except Exception as e:
        print(f"Error al agregar la escuela: {e}")
        return {"error": "Error interno del servidor"}, 500
    
@app.route("/reportes/pendientes", methods=["GET"])
def reportes_pendientes():
    query = """
    SELECT id_reports,lat, lng, descripcion, escuela, fecha_reporte, categoria, usuarios.username, usuarios.dni, reporte_del_problema 
    FROM reports 
    INNER JOIN usuarios ON usuarios.id_user=reports.user_id
    WHERE estado = 'pendiente'
    """
    result = execute_query(query, fetch_all=True)
    if result is None:
        return {"error": "Error obteniendo los reportes pendientes"}, 500
    return jsonify(result), 200

@app.route("/reporte/aceptar/<int:reporte_id>", methods=["GET","POST"])
def reporteaceptar(reporte_id):
    if request.method == "GET":
        return getreportesaceptar(reporte_id)
    elif request.method == "POST":
        return aceptar_reporte(reporte_id)

def getreportesaceptar(reporte_id):
    query = """
    SELECT r.id_reports, r.lat, r.lng, r.descripcion, r.escuela, r.fecha_reporte, r.categoria, usuarios.username, usuarios.dni, r.reporte_del_problema, es.nombre,es.cue,es.localidad
    FROM reports r
    INNER JOIN usuarios ON usuarios.id_user=r.user_id
    INNER JOIN escuela_det ed ON ed.id_user=r.user_id
    INNER JOIN escuelas es ON es.id_escuela=ed.id_escuela
    WHERE estado = 'aceptado'
    """
    result = execute_query(query,fetch_all=True)
    if result is None:
        return {"error": "Error al aprobar el reporte"}, 500
    return jsonify(result), 200
def aceptar_reporte(reporte_id):
    query = "UPDATE reports SET estado = 'aceptado' WHERE id_reports = %s"
    result = execute_query(query, (reporte_id,))
    if result is not None:
        return {"error": "Error al aprobar el reporte"}, 500
    return {"message": "Reporte aprobado"}, 200

@app.route("/reporte/rechazar/<int:reporte_id>", methods=["GET","POST"])
def reporterechazado(reporte_id):
    if request.method == "GET":
        return getreportesrechazados(reporte_id)
    elif request.method == "POST":
        return rechazar_reporte(reporte_id)
        
def getreportesrechazados(reporte_id):
    query = """
    SELECT id_reports,lat, lng, descripcion, escuela, fecha_reporte, categoria, usuarios.username, usuarios.dni, reporte_del_problema 
    FROM reports 
    INNER JOIN usuarios ON usuarios.id_user=reports.user_id
    WHERE estado = 'rechazado'
    """
    result = execute_query(query,fetch_all=True)
    if result is None:
        return {"error": "Error al aprobar el reporte"}, 500
    return jsonify(result), 200
def rechazar_reporte(reporte_id):
    query = "UPDATE reports SET estado = 'rechazado' WHERE id_reports = %s"
    result = execute_query(query, (reporte_id,))
    if result is not None:
        return {"error": "Error al rechazar el reporte"}, 500
    return {"message": "Reporte rechazado"}, 200

@app.route("/asignarescuela", methods=["POST"])
def asignarescuela():
    data = request.get_json()
    usuario = data.get('usuario')
    escuela = data.get('escuela')

    if not usuario or not escuela:
        return {"error": "Faltan datos"}, 400

    try:
        # Primero verificamos si el usuario ya está asignado a una escuela
        check_query = """
        SELECT * FROM escuela_det WHERE id_user = %s
        """
        result = execute_query(check_query, (usuario,), fetch_one=True)

        if result:
            # Si el usuario ya está asignado a una escuela, actualizamos la asignación
            update_query = """
            UPDATE escuela_det
            SET id_escuela = %s
            WHERE id_user = %s
            """
            execute_query(update_query, (escuela, usuario))
            return {"message": "Usuario actualizado correctamente a la nueva escuela"}, 200
        else:
            # Si el usuario no está asignado a ninguna escuela, insertamos una nueva asignación
            insert_query = """
            INSERT INTO escuela_det (id_escuela, id_user)
            VALUES (%s, %s)
            """
            execute_query(insert_query, (escuela, usuario))
            return {"message": "Usuario asignado correctamente a la escuela"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/estadisticas', methods=['GET'])
def estadisticas():
    try:
        query = """
            SELECT categoria, COUNT(*) AS total
            FROM reports
            WHERE estado = "aceptado"
            GROUP BY categoria;
        """
        resultados = execute_query(query, fetch_all=True)

        if resultados is None:
            return jsonify({"error": "No se pudieron obtener las estadísticas."}), 500

        print("Resultados que se van a enviar:", resultados)
        return jsonify(resultados)

    except Exception as e:
        print(f"Error en la consulta: {e}")
        return jsonify({"error": "Ocurrió un error en el servidor."}), 500
    
@app.route('/director', methods=['GET'])
def director():
    query = """SELECT 
                    u.id_user,
                    u.username,
                    u.dni,
                    u.nacimiento,
                    u.user_type
                FROM 
                    usuarios u
                LEFT JOIN 
                    escuela_det ed ON ed.id_user = u.id_user
                WHERE 
                    u.user_type = 'director' AND ed.id_escuela IS NULL;
            """
    resultados = execute_query(query, fetch_all=True)
    try:
        if resultados is None:
            return jsonify({"error": "No se pudieron obtener los directores."}), 500
        return jsonify(resultados)

    except Exception as e:
        print(f"Error en la consulta: {e}")
        return jsonify({"error": "Ocurrió un error en el servidor."}), 500

