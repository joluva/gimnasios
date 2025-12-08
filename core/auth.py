import bcrypt
from .database import get_connection

# Variable global que siempre tendrá la empresa activa durante la sesión
CURRENT_EMPRESA_ID = None
CURRENT_USER = {}

def set_current_empresa(empresa_id):
    global CURRENT_EMPRESA_ID
    CURRENT_EMPRESA_ID = empresa_id

def login(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, password_hash, rol, empresa_id, nombre_completo 
        FROM Usuarios WHERE username = ? AND activo = 1
    """, (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        global CURRENT_USER
        CURRENT_USER = dict(user)
        set_current_empresa(user['empresa_id'])  # puede ser None si es SuperAdmin
        return True
    return False

# Función auxiliar para todas las consultas
def get_empresa_filter():
    """Devuelve la cláusula WHERE para filtrar por empresa"""
    if CURRENT_USER and CURRENT_USER['rol'] == 'SuperAdmin':
        return ""  # SuperAdmin ve todo
    elif CURRENT_EMPRESA_ID:
        return f"WHERE empresa_id = {CURRENT_EMPRESA_ID}"
    else:
        return "WHERE 1=0"  # seguridad: nunca debe pasar