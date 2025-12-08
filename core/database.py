# core/database.py  ← VERSIÓN DEFINITIVA QUE FUNCIONA SIEMPRE
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "gimnasio.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Se llama UNA sola vez al iniciar la app. Crea todo si no existe."""
    if DB_PATH.exists():
        print("Base de datos ya existe → listo")
        return

    print("Creando base de datos desde cero...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ======================= TODAS LAS TABLAS =======================
    cur.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE Empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            nombre_fantasia TEXT,
            email TEXT,
            moneda TEXT DEFAULT 'USD'
        );

        CREATE TABLE Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('SuperAdmin','Admin','Recepcionista','Entrenador')),
            activo INTEGER DEFAULT 1,
            UNIQUE(empresa_id, username),
            FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE
        );

        CREATE TABLE TiposMembresias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            duracion_dias INTEGER NOT NULL,
            precio REAL NOT NULL,
            FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE
        );

        CREATE TABLE Miembros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            email TEXT NOT NULL,
            telefono TEXT,
            fecha_nacimiento DATE,
            genero TEXT,
            foto_path TEXT,
            tipo_membresia_id INTEGER,
            fecha_inicio DATE NOT NULL,
            fecha_fin DATE,
            estado TEXT DEFAULT 'Activo',
            codigo_qr TEXT,
            FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE,
            FOREIGN KEY (tipo_membresia_id) REFERENCES TiposMembresias(id)
        );

        CREATE TABLE Asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            miembro_id INTEGER NOT NULL,
            fecha_entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
            fecha_salida DATETIME,
            FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE,
            FOREIGN KEY (miembro_id) REFERENCES Miembros(id)
        );

        CREATE TABLE Pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            miembro_id INTEGER NOT NULL,
            monto REAL NOT NULL,
            fecha_pago DATE NOT NULL,
            metodo_pago TEXT,
            FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE
        );
    """)

    # ======================= DATOS INICIALES =======================
    print("Insertando datos de prueba...")

    cur.execute("INSERT INTO Empresas (nombre, nombre_fantasia, email) VALUES ('Demo Gym', 'PowerFit Center', 'demo@gimnasio.com')")
    empresa_id = cur.lastrowid

    cur.execute("INSERT INTO TiposMembresias (empresa_id, nombre, duracion_dias, precio) VALUES (?, 'Mensual Básico', 30, 50.00)", (empresa_id,))
    cur.execute("INSERT INTO TiposMembresias (empresa_id, nombre, duracion_dias, precio) VALUES (?, 'Anual Premium', 365, 500.00)", (empresa_id,))

    # SuperAdmin
    cur.execute("INSERT INTO Usuarios (username, password_hash, rol) VALUES ('admin', 'admin123_hash_fake', 'SuperAdmin')")
    # Admin del gimnasio demo
    cur.execute("INSERT INTO Usuarios (empresa_id, username, password_hash, rol) VALUES (?, 'demo', 'demo123_hash_fake', 'Admin')", (empresa_id,))

    # Miembro de ejemplo
    cur.execute("""INSERT INTO Miembros 
        (empresa_id, nombre, apellido, email, telefono, fecha_inicio, fecha_fin, estado)
        VALUES (?, 'María', 'Gómez', 'maria@demo.com', '123456789', '2025-01-01', '2025-01-31', 'Activo')""", (empresa_id,))

    conn.commit()
    conn.close()
    print("Base de datos creada con éxito + datos de prueba listos")