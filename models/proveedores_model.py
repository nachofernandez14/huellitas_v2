from models.db import Database


class ProveedoresModel:
    def __init__(self):
        self.db_path = 'database/negocio.db'  # Guardar la ruta en lugar de la instancia
        self._create_table_if_needed()

    def _get_db_connection(self):
        """Crea una nueva conexión a la base de datos thread-safe."""
        return Database(self.db_path)

    def _create_table_if_needed(self):
        """Crea la tabla de proveedores si no existe."""
        try:
            db = self._get_db_connection()
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS proveedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    contacto TEXT,
                    telefono TEXT,
                    email TEXT,
                    direccion TEXT,
                    ciudad TEXT,
                    estado TEXT NOT NULL DEFAULT 'activo',
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            # crear índice en nombre para búsquedas case-insensitive más rápidas
            try:
                db.execute("CREATE INDEX IF NOT EXISTS idx_proveedores_nombre ON proveedores (nombre COLLATE NOCASE)")
            except Exception:
                pass
            db.close()
        except Exception as e:
            print(f"Error al crear tabla proveedores: {e}")

    def search_proveedores(self, query: str = None, limit: int = 50, offset: int = 0):
        """Busca proveedores en la BD aplicando LIMIT/OFFSET. Devuelve (rows_list, total_count).

        Si query es None o vacía, devuelve todos (paginados).
        """
        try:
            db = self._get_db_connection()
            params = []
            where = ""
            if query:
                where = " WHERE nombre LIKE ? COLLATE NOCASE"
                params.append(f"%{query}%")

            # total count
            count_sql = f"SELECT COUNT(*) FROM proveedores{where}"
            cur = db.execute(count_sql, tuple(params) if params else ())
            total = cur.fetchone()[0] if cur else 0

            sql = (
                "SELECT id, nombre, telefono, saldo "
                f"FROM proveedores{where} LIMIT ? OFFSET ?"
            )
            params.extend([limit, offset])
            cur = db.execute(sql, tuple(params))
            rows = cur.fetchall() or []

            # convertir a dict (incluyendo id para operaciones internas)
            columnas = ["id", "nombre", "telefono", "saldo"]
            result = []
            for row in rows:
                d = dict(zip(columnas, row))
                result.append(d)

            db.close()
            return result, total

        except Exception as e:
            print(f"Error al buscar proveedores: {e}")
            return [], 0

    def get_all(self, use_db: bool = True):
        """Obtiene todos los proveedores de la base de datos."""
        if not use_db:
            return []
        try:
            db = self._get_db_connection()
            cur = db.execute("SELECT id, nombre, telefono, saldo FROM proveedores")
            rows = cur.fetchall() or []
            
            # convertir a dict
            columnas = ["id", "nombre", "telefono", "saldo"]
            result = []
            for row in rows:
                d = dict(zip(columnas, row))
                result.append(d)
            
            db.close()
            return result
        except Exception as e:
            print(f"Error al obtener proveedores: {e}")
            return []

    def get_by_id(self, proveedor_id):
        """Obtiene un proveedor por su ID."""
        try:
            db = self._get_db_connection()
            cur = db.execute("SELECT id, nombre, telefono, saldo FROM proveedores WHERE id = ?", (proveedor_id,))
            row = cur.fetchone()
            db.close()
            
            if row:
                columnas = ["id", "nombre", "telefono", "saldo"]
                return dict(zip(columnas, row))
            return None
        except Exception as e:
            print(f"Error al obtener proveedor por ID: {e}")
            return None

    def create_proveedor(self, data: dict):
        """Inserta un nuevo proveedor en la base de datos. Devuelve el id insertado o None."""
        try:
            db = self._get_db_connection()
            
            # Validación básica
            if not data.get("nombre", "").strip():
                print("Error: El nombre del proveedor es requerido")
                return None
            
            sql = """
                INSERT INTO proveedores (nombre, telefono, saldo, estado)
                VALUES (?, ?, ?, 'activo')
            """
            params = (
                data.get("nombre", "").strip(),
                data.get("telefono", "").strip(),
                float(data.get("saldo", 0)) if data.get("saldo", "").strip() else 0.0
            )
            
            cur = db.execute(sql, params)
            proveedor_id = cur.lastrowid
            db.close()
            return proveedor_id
            
        except Exception as e:
            print(f"Error al crear proveedor: {e}")
            return None

    def update_proveedor(self, proveedor_id, data: dict):
        """Actualiza un proveedor. Devuelve True si se actualizó al menos una fila."""
        try:
            db = self._get_db_connection()
            
            # Validación básica
            if not data.get("nombre", "").strip():
                print("Error: El nombre del proveedor es requerido")
                return False
            
            sql = """
                UPDATE proveedores 
                SET nombre = ?, telefono = ?, saldo = ?
                WHERE id = ?
            """
            params = (
                data.get("nombre", "").strip(),
                data.get("telefono", "").strip(),
                float(data.get("saldo", 0)) if data.get("saldo", "").strip() else 0.0,
                proveedor_id
            )
            
            cur = db.execute(sql, params)
            affected = cur.rowcount
            db.close()
            return affected > 0
            
        except Exception as e:
            print(f"Error al actualizar proveedor: {e}")
            return False

    def delete_proveedor(self, proveedor_id):
        """Borra un proveedor por id. Devuelve True si se borró una fila."""
        try:
            db = self._get_db_connection()
            cur = db.execute("DELETE FROM proveedores WHERE id = ?", (proveedor_id,))
            affected = cur.rowcount
            db.close()
            return affected > 0
        except Exception as e:
            print(f"Error al borrar proveedor: {e}")
            return False