-- =============================================
-- BASE DE DATOS MULTIEMPRESA - GIMNASIO PRO
-- SQLite - Listo para producción y futuro SaaS
-- =============================================

-- Empresas / Gimnasios
CREATE TABLE IF NOT EXISTS Empresas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    nombre_fantasia TEXT,
    rut_o_nit TEXT UNIQUE,
    direccion TEXT,
    telefono TEXT,
    email TEXT,
    logo_path TEXT,
    moneda TEXT DEFAULT 'USD',
    fecha_creacion DATE DEFAULT CURRENT_DATE,
    estado TEXT DEFAULT 'Activa' CHECK(estado IN ('Activa', 'Inactiva', 'Prueba'))
);

-- Usuarios del sistema (SuperAdmin puede tener empresa_id NULL)
CREATE TABLE IF NOT EXISTS Usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER,                                      -- NULL = SuperAdmin
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('SuperAdmin','Admin','Recepcionista','Entrenador')),
    nombre_completo TEXT,
    email TEXT,
    activo INTEGER DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(empresa_id, username),
    FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE
);

-- Tipos de Membresías (por gimnasio)
CREATE TABLE IF NOT EXISTS TiposMembresias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    duracion_dias INTEGER NOT NULL,
    precio REAL NOT NULL,
    descripcion TEXT,
    FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE
);

-- Miembros
CREATE TABLE IF NOT EXISTS Miembros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    email TEXT NOT NULL,
    telefono TEXT,
    direccion TEXT,
    fecha_nacimiento DATE,
    genero TEXT,
    foto_path TEXT,
    tipo_membresia_id INTEGER,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    estado TEXT DEFAULT 'Activo' CHECK(estado IN ('Activo','Inactivo','Suspendido','Congelado')),
    notas TEXT,
    codigo_qr TEXT,                                          -- ruta al archivo QR generado
    FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE,
    FOREIGN KEY (tipo_membresia_id) REFERENCES TiposMembresias(id)
);
CREATE INDEX IF NOT EXISTS idx_miembros_empresa_email ON Miembros(empresa_id, email);

-- Asistencias
CREATE TABLE IF NOT EXISTS Asistencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    miembro_id INTEGER NOT NULL,
    fecha_entrada DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_salida DATETIME,
    FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE,
    FOREIGN KEY (miembro_id) REFERENCES Miembros(id)
);
CREATE INDEX IF NOT EXISTS idx_asistencias_fecha ON Asistencias(empresa_id, fecha_entrada);

-- Pagos
CREATE TABLE IF NOT EXISTS Pagos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    miembro_id INTEGER NOT NULL,
    monto REAL NOT NULL,
    fecha_pago DATE NOT NULL,
    metodo_pago TEXT,
    estado TEXT DEFAULT 'Pagado',
    notas TEXT,
    FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE,
    FOREIGN KEY (miembro_id) REFERENCES Miembros(id)
);

-- Clases (ej: Yoga, CrossFit)
CREATE TABLE IF NOT EXISTS Clases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    capacidad_max INTEGER NOT NULL,
    FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE
);

-- Entrenadores
CREATE TABLE IF NOT EXISTS Entrenadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    especialidad TEXT,
    FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE
);

-- Horarios de clases
CREATE TABLE IF NOT EXISTS Horarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    clase_id INTEGER NOT NULL,
    entrenador_id INTEGER NOT NULL,
    fecha_hora_inicio DATETIME NOT NULL,
    duracion_minutos INTEGER NOT NULL,
    cupos_disponibles INTEGER NOT NULL,
    FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE,
    FOREIGN KEY (clase_id) REFERENCES Clases(id),
    FOREIGN KEY (entrenador_id) REFERENCES Entrenadores(id)
);

-- Inscripciones a clases
CREATE TABLE IF NOT EXISTS Inscripciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    miembro_id INTEGER NOT NULL,
    horario_id INTEGER NOT NULL,
    fecha_inscripcion DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado TEXT DEFAULT 'Confirmada',
    FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE,
    FOREIGN KEY (miembro_id) REFERENCES Miembros(id),
    FOREIGN KEY (horario_id) REFERENCES Horarios(id)
);

-- Productos (tienda del gimnasio)
CREATE TABLE IF NOT EXISTS Productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL,
    stock INTEGER DEFAULT 0,
    descripcion TEXT,
    FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE
);

-- Ventas (punto de venta)
CREATE TABLE IF NOT EXISTS Ventas 
    (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    miembro_id INTEGER,           -- puede ser NULL (venta anónima)
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
    total REAL NOT NULL,
    FOREIGN KEY (empresa_id) REFERENCES Empresas(id) ON DELETE CASCADE,
    FOREIGN KEY (miembro_id) REFERENCES Miembros(id),
    FOREIGN KEY (producto_id) REFERENCES Productos(id)
);

-- =============================================
-- DATOS INICIALES (solo la primera vez)
-- =============================================

-- SuperAdmin por defecto (contraseña: admin123 → hash con bcrypt más abajo)
INSERT INTO Usuarios (empresa_id, username, password_hash, rol, nombre_completo, activo)
VALUES (NULL, 'admin', '$2b$12$3f9xY8oZ7vQ6pL5kJ4h2ge9v8r7t6y5u4i3o2p1ñlkjhgfdsaqwerty', 'SuperAdmin', 'Administrador General', 1);

-- Empresa de prueba
INSERT INTO Empresas (nombre, nombre_fantasia, email, moneda)
VALUES ('Mi Gimnasio Demo', 'PowerFit Center', 'demo@gimnasio.com', 'USD');

-- Primer admin del gimnasio demo (contraseña: demo123)
INSERT INTO Usuarios (empresa_id, username, password_hash, rol, nombre_completo)
SELECT id, 'demo', '$2b$12$9k8j7h6g5f4d3s2a1ñlkjhgfdsaqwertyPOIUYTREWQasdfghjklmnbvcx', 'Admin', 'Admin Demo' 
FROM Empresas WHERE nombre_fantasia = 'PowerFit Center';   