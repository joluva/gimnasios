import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "gimnasio.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if DB_PATH.exists():
        return  # Ya existe

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Lee y ejecuta el esquema completo
    schema_path = Path(__file__) / "database_schema.sql"
    with open(schema_path, encoding="utf-8") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    print("Base de datos creada con éxito (multiempresa activada)")