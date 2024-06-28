from flask import Flask, flash, render_template, url_for, send_from_directory, jsonify, request, session, redirect, g
from flask_bcrypt import Bcrypt
from fare_ondemand import calculate_peak_fare
import os
import time
import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave secreta real
bcrypt = Bcrypt(app)

# Configuración de la base de datos
DATABASE = 'users.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def calculate_fare(self):
        now = time.time()
        if self.last_status_change is not None:
            time_elapsed = now - self.last_status_change
            fare = calculate_peak_fare(self.in_movement)
            self.fare_total += round(time_elapsed * fare, 2)
        self.last_status_change = now

fare_movement = 0.05  # tarifa en movimiento en céntimos de euro por segundo
fare_stop = 0.02  # tarifa en reposo en céntimos de euro por segundo

class Taximetro:
    def __init__(self):
        self.start_road = False
        self.last_status_change = None
        self.fare_total = 0
        self.in_movement = False
        self.start_time = None
        self.end_time = None
        self.username = None
    
    def calculate_fare(self):
        now = time.time()
        if self.last_status_change is not None:
            time_elapsed = (now - self.last_status_change) / 60  # Convertir a minutos
            fare = calculate_peak_fare(self.in_movement)
            self.fare_total += round(time_elapsed * fare, 2)
        self.last_status_change = now
    
    def start(self):
        self.start_road = True
        self.last_status_change = time.time()
        self.start_time = datetime.datetime.now()
        self.in_movement = True
    
    def stop(self):
        self.calculate_fare()
        self.in_movement = False
    
    def continue_road(self):
        if self.start_road:
            self.calculate_fare()
            self.in_movement = True
    
    def finish_road(self):
        self.calculate_fare()
        self.start_road = False
        self.end_time = datetime.datetime.now()
        self.save_ride_history()
        return self.fare_total
    
    def save_ride_history(self):
        with open('rides_history.txt', mode='a', encoding='utf-8') as file:
            file.write(f"Usuario: {self.username}\n")
            file.write(f"Fecha de inicio: {self.start_time}\n")
            file.write(f"Fecha de fin: {self.end_time}\n")
            file.write(f"Total a cobrar: €{self.fare_total:.2f}\n")
            file.write("=======================================\n")
    
    def view_history(self, limit=4):
        try:
            with open('rides_history.txt', mode='r', encoding='utf-8') as file:
                lines = file.readlines()
                rides = []
                current_ride = {}
                for line in reversed(lines):
                    if line.startswith("Usuario:"):
                        if current_ride:
                            rides.append(current_ride)
                            if len(rides) >= limit:
                                break
                        current_ride = {"usuario": line.split(":")[1].strip()}
                    elif line.startswith("Fecha de inicio:"):
                        current_ride["inicio"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Fecha de fin:"):
                        current_ride["fin"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Total a cobrar:"):
                        current_ride["total"] = line.split(":")[1].strip()
                if current_ride and len(rides) < limit:
                    rides.append(current_ride)
                return rides
        except FileNotFoundError:
            return []
    
    def clear(self):
        self.start_road = False
        self.last_status_change = None
        self.fare_total = 0
        self.in_movement = False
        self.start_time = None
        self.end_time = None

taximetro = Taximetro()

@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        if user and bcrypt.check_password_hash(user[2], password):
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar si el usuario ya existe
        existing_user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        if existing_user:
            flash('El nombre de usuario ya existe, por favor elige otro', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        db = get_db()
        db.execute('INSERT INTO users (username, password) VALUES (?, ?)', [username, hashed_password])
        db.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'img'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/start', methods=['POST'])
def start():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    user = query_db('SELECT username FROM users WHERE id = ?', [session['user_id']], one=True)
    taximetro.username = user[0]
    taximetro.start()
    return jsonify({"message": "Carrera iniciada", "start_time": taximetro.start_time.isoformat()})

@app.route('/stop', methods=['POST'])
def stop():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    taximetro.stop()
    return jsonify({"message": "Taxi detenido"})

@app.route('/continue', methods=['POST'])
def continue_road():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    taximetro.continue_road()
    return jsonify({"message": "Carrera continuada"})

@app.route('/finish', methods=['POST'])
def finish():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    fare = taximetro.finish_road()
    taximetro.clear()
    return jsonify({"message": "Carrera finalizada", "fare": fare})

@app.route('/history', methods=['GET'])
def view_history():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    history = taximetro.view_history(limit=4)
    return jsonify({"history": history})

@app.route('/fare', methods=['GET'])
def get_fare():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    taximetro.calculate_fare()
    return jsonify({"fare": taximetro.fare_total})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=3000)
