from models.db import Database
import sqlite3

class UsuarioModel:
    def __init__(self, username='admin', password='admin123'):
        self.username = username
        self.password = password
        self.db = Database()

    def crear_tabla(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS "usuarios" (
            "id"	INTEGER,
            "usuario"	TEXT NOT NULL,
            "contraseña"	TEXT NOT NULL,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """)

    def crear_usuario(self, username, password):
        """Crea un nuevo usuario en la tabla `usuarios`.

        Retorna True si el usuario se creó correctamente, False si el usuario
        ya existe o si los datos de entrada son inválidos.
        """
        # Validaciones simples
        if not username or not password:
            return False

        # Comprobar si el usuario ya existe
        query_check = "SELECT id FROM usuarios WHERE usuario = ?"
        cursor = self.db.execute(query_check, (username,))
        if cursor.fetchone() is not None:
            return False

        # Insertar nuevo usuario
        query_insert = "INSERT INTO usuarios (usuario, contraseña) VALUES (?, ?)"
        self.db.execute(query_insert, (username, password))
        # La clase Database hace commit para INSERT
        return True

    def verificar_credenciales(self, username, password):
        """Verifica si existe un usuario con las credenciales proporcionadas.

        Devuelve True si existe una fila que coincida, False en caso contrario.
        """
        query = "SELECT id FROM usuarios WHERE usuario = ? AND contraseña = ?"
        cursor = self.db.execute(query, (username, password))
        row = cursor.fetchone()
        return row is not None