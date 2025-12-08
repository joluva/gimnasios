# Solo para importar en otros módulos
from .auth import CURRENT_EMPRESA_ID, CURRENT_USER

def require_empresa():
    """Usar como decorador o llamada directa"""
    if CURRENT_EMPRESA_ID is None and (not CURRENT_USER or CURRENT_USER['rol'] != 'SuperAdmin'):
        raise PermissionError("No hay empresa seleccionada")