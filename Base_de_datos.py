import sqlite3
from datetime import datetime

def inicializar_bd():
    """Inicializa la base de datos creando las tablas necesarias."""
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()

        # Crear la tabla 'usuarios'
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          username TEXT NOT NULL UNIQUE,
                          password TEXT NOT NULL)''')
        cursor.execute('INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)', ('admin', 'adminpass'))
        cursor.execute('INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)', ('123', '123'))

        # Crear la tabla 'proyectos' 
        cursor.execute('''CREATE TABLE IF NOT EXISTS proyectos (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          nombre_proyecto TEXT NOT NULL,
                          ruta_proyecto TEXT NOT NULL)''')

        # Crear la tabla 'registro'
        cursor.execute('''CREATE TABLE IF NOT EXISTS registro (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          timestamp TEXT NOT NULL,
                          username TEXT NOT NULL,
                          accion TEXT NOT NULL)''')

        # Crear la tabla 'imagenes' para almacenar rutas de imágenes
        cursor.execute('''CREATE TABLE IF NOT EXISTS imagenes (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          id_proyecto INTEGER,                          
                          nombre_archivo TEXT NOT NULL,
                          botellas_detectadas INTEGER,
                          botellas_probables INTEGER,
                          recuadro_sin_texto FLOAT NOT NULL DEFAULT 0.4,
                          recuadro_con_texto FLOAT NOT NULL DEFAULT 0.5,
                          FOREIGN KEY (id_proyecto) REFERENCES proyectos(id))''')
    
    conn = sqlite3.connect('base.db')
    conn.close()  # Cerrar la conexión después de crearlas

def verificar_credenciales(usuario, contrasena):
    """Verifica las credenciales del usuario."""
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?', (usuario, contrasena))
        return cursor.fetchone() is not None
    
def obtener_usuarios():
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor() 
        cursor.execute('SELECT username FROM usuarios')
        return cursor.fetchall()
    
def eliminar_usuario(username, password):
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM usuarios WHERE username = ? AND password = ?', (username, password))
        print("Usuario eliminado exitosamente.")

def cambiar_contrasena(username, password):
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE usuarios SET password = ? WHERE username = ?', (password, username))
        print("Contrasena cambiada exitosamente.")
    
def registrar_usuario(username, password):
    """Registra un usuario en la base de datos."""
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO usuarios (username, password) VALUES (?, ?)', (username, password))
        if cursor:
            print("Usuario registrado exitosamente.")

def registrar_accion(usuario, accion):
    """Registra una acción en la base de datos."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO registro (timestamp, username, accion) VALUES (?, ?, ?)', (timestamp, usuario, accion))
        if cursor:
            print("Acción registrada exitosamente.")

def obtener_proyectos():
    with sqlite3.connect('base.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT nombre_proyecto FROM proyectos')
            return cursor.fetchall()

def obtener_ruta_proyecto(proyecto):
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT ruta_proyecto FROM proyectos WHERE nombre_proyecto = ?', (proyecto,))
        return cursor.fetchall()[0]

def obtener_sensibilidad(archivo, proyecto):
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT recuadro_con_texto, recuadro_sin_texto FROM imagenes WHERE id_proyecto = (SELECT id FROM proyectos WHERE nombre_proyecto = ?) AND nombre_archivo = ?', (proyecto, archivo))        
        return cursor.fetchall()[0]
    
def actualizar_sensibilidad(con_texto, sin_texto, archivo, proyecto):
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE imagenes SET recuadro_con_texto = ?, recuadro_sin_texto = ? WHERE nombre_archivo = ? AND id_proyecto = (SELECT id FROM proyectos WHERE nombre_proyecto = ?)', (con_texto, sin_texto, archivo, proyecto))
        print("Sensibilidad actualizada exitosamente.")
        

def agregar_proyecto(nombre_proyecto, ruta_proyecto):
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO proyectos (nombre_proyecto, ruta_proyecto) VALUES (?, ?)', (nombre_proyecto, ruta_proyecto))
        print("Proyecto agregado exitosamente.")
        
def eliminar_proyecto(nombre_proyecto):
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM proyectos WHERE nombre_proyecto = ?', (nombre_proyecto,))
        print("Proyecto eliminado exitosamente.")

def modificar_proyecto(nombre_antes, nombre_nuevo, ruta_proyecto):
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE proyectos SET nombre_proyecto = ?, ruta_proyecto = ? WHERE nombre_proyecto = ?', (nombre_nuevo, ruta_proyecto, nombre_antes))
        print("Proyecto modificado exitosamente.")

def obtener_registros():
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, username, accion FROM registro ORDER BY timestamp DESC")               
        return cursor.fetchall() 

def agregar_imagen(nombre_archivo, nombre_proyecto):
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO imagenes (nombre_archivo, id_proyecto) VALUES (?, (SELECT id FROM proyectos WHERE nombre_proyecto = ?))', (nombre_archivo, nombre_proyecto))
        print("Imagen cargada exitosamente.")

def obtener_imagenes(nombre_proyecto):
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT nombre_archivo FROM imagenes WHERE id_proyecto = (SELECT id FROM proyectos WHERE nombre_proyecto = ?)', (nombre_proyecto,))
        return cursor.fetchall()

def eliminar_imagen(nombre_archivo, nombre_proyecto):
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM imagenes WHERE nombre_archivo = ? AND id_proyecto = (SELECT id FROM proyectos WHERE nombre_proyecto = ?)', (nombre_archivo, nombre_proyecto))
        print(f"Imagen", nombre_archivo, " eliminada exitosamente.")

def actualizar_detectadas_probables(archivo, proyecto, botellas_detectadas, botellas_probables):
    # Actualizar botellas detectadas y botellas probables
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE imagenes SET botellas_detectadas = ?, botellas_probables = ? WHERE nombre_archivo = ? AND id_proyecto = (SELECT id FROM proyectos WHERE nombre_proyecto = ?)', (botellas_detectadas, botellas_probables, archivo, proyecto))
        print("Botellas detectadas y probables actualizadas exitosamente.")
                       
def obtener_datos_procesados(nombre_archivo, nombre_proyecto):
    with sqlite3.connect('base.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT botellas_detectadas, botellas_probables FROM imagenes WHERE nombre_archivo = ? AND id_proyecto = (SELECT id FROM proyectos WHERE nombre_proyecto = ?)', (nombre_archivo, nombre_proyecto))
        return cursor.fetchall()[0]
