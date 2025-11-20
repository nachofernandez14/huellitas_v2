from models.db import Database


class CategoriasModel:
    def __init__(self):
        self.db_path = 'database/negocio.db'
        self._create_tables_if_needed()

    def _get_db_connection(self):
        return Database(self.db_path)

    def _create_tables_if_needed(self):
        try:
            db = self._get_db_connection()
            # Tabla de subcategorias
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS subcategorias (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT
                )
                """
            )

            # Tabla de categorias con ID autoincremental
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    categoria TEXT,
                    subcategoria TEXT,
                    descripcion TEXT,
                    estado TEXT NOT NULL DEFAULT 'activo',
                    FOREIGN KEY(subcategoria) REFERENCES subcategorias(id)
                )
                """
            )

            # Si la tabla existía antes sin `descripcion`, agregar la columna
            try:
                # comprobar si la columna descripcion existe
                info_cur = db.execute("PRAGMA table_info('categorias')")
                cols = [r[1] for r in info_cur.fetchall() or []]
                if 'descripcion' not in cols:
                    try:
                        db.execute("ALTER TABLE categorias ADD COLUMN descripcion TEXT")
                    except Exception:
                        pass
            except Exception:
                pass

            # índice para búsquedas por nombre de categoría
            try:
                db.execute("CREATE INDEX IF NOT EXISTS idx_categorias_nombre ON categorias (categoria COLLATE NOCASE)")
            except Exception:
                pass

            db.close()
        except Exception as e:
            print(f"Error al crear tablas de categorías: {e}")

    # --- Operaciones sobre categorías ---
    def list_categories(self):
        """Devuelve todas las categorías como lista de dicts con keys compatibles con la vista.

        Formato devuelto: {id, nombre, parent_id, descripcion, estado}
        """
        try:
            db = self._get_db_connection()
            cur = db.execute("SELECT id, categoria, subcategoria, IFNULL(descripcion, ''), estado FROM categorias ORDER BY categoria COLLATE NOCASE")
            rows = cur.fetchall() or []
            result = []
            for r in rows:
                result.append({
                    "id": r[0],
                    "nombre": r[1],
                    "parent_id": r[2],
                    "descripcion": r[3],
                    "estado": r[4],
                })
            db.close()
            return result
        except Exception as e:
            print(f"Error en list_categories: {e}")
            return []

    def search_categories(self, query: str = None, limit: int = 50, offset: int = 0):
        """Busca categorías por nombre (LIKE). Devuelve (rows_list, total_count)."""
        try:
            db = self._get_db_connection()
            params = []
            where = ""
            if query:
                where = " WHERE categoria LIKE ? COLLATE NOCASE"
                params.append(f"%{query}%")

            count_sql = f"SELECT COUNT(*) FROM categorias{where}"
            cur = db.execute(count_sql, tuple(params) if params else ())
            total = cur.fetchone()[0] if cur else 0

            sql = f"SELECT id, categoria, subcategoria, IFNULL(descripcion, ''), estado FROM categorias{where} ORDER BY categoria COLLATE NOCASE LIMIT ? OFFSET ?"
            params_page = list(params) if params else []
            params_page.extend([limit, offset])
            cur2 = db.execute(sql, tuple(params_page))
            rows = cur2.fetchall() if cur2 else []

            result = []
            for r in rows:
                result.append({
                    "id": r[0],
                    "nombre": r[1],
                    "parent_id": r[2],
                    "descripcion": r[3],
                    "estado": r[4],
                })

            db.close()
            return result, total
        except Exception as e:
            print(f"Error en search_categories: {e}")
            return [], 0

    def get_by_id(self, category_id):
        try:
            db = self._get_db_connection()
            cur = db.execute("SELECT id, categoria, subcategoria, IFNULL(descripcion, ''), estado FROM categorias WHERE id = ?", (category_id,))
            r = cur.fetchone()
            db.close()
            if not r:
                return None
            return {
                "id": r[0],
                "nombre": r[1],
                "parent_id": r[2],
                "descripcion": r[3],
                "estado": r[4],
            }
        except Exception as e:
            print(f"Error en get_by_id: {e}")
            return None

    def create_category(self, data: dict):
        """Crea una categoría. El campo 'id' debe ser provisto por el usuario (no autoincremental).

        Espera keys: id (texto), nombre (categoria), parent_id (opcional), estado (opcional).
        Devuelve el id insertado (o el mismo id) o None en caso de error.
        """
        try:
            cat_id = data.get("id")
            nombre = data.get("nombre")
            parent = data.get("parent_id")
            estado = data.get("estado", "activo")

            if not cat_id or not str(cat_id).strip():
                print("Error: El id de la categoría es requerido y lo provee el usuario.")
                return None
            if not nombre or not str(nombre).strip():
                print("Error: El nombre de la categoría es requerido.")
                return None

            db = self._get_db_connection()
            db.execute(
                "INSERT INTO categorias (id, categoria, subcategoria, descripcion, estado) VALUES (?, ?, ?, ?, ?)",
                (
                    str(cat_id),
                    nombre.strip(),
                    parent if parent not in (None, "") else None,
                    data.get("descripcion", ""),
                    estado,
                ),
            )
            db.close()
            return str(cat_id)
        except Exception as e:
            print(f"Error en create_category: {e}")
            return None

    def update_category(self, category_id, data: dict):
        """Actualiza una categoría. Devuelve True si se actualizó alguna fila."""
        try:
            db = self._get_db_connection()
            fields = []
            values = []
            if "nombre" in data:
                fields.append("categoria = ?")
                values.append(data.get("nombre"))
            if "descripcion" in data:
                fields.append("descripcion = ?")
                values.append(data.get("descripcion"))
            if "parent_id" in data:
                fields.append("subcategoria = ?")
                values.append(data.get("parent_id") if data.get("parent_id") not in (None, "") else None)
            if "estado" in data:
                fields.append("estado = ?")
                values.append(data.get("estado"))

            if not fields:
                db.close()
                return False

            values.append(category_id)
            sql = f"UPDATE categorias SET {', '.join(fields)} WHERE id = ?"
            cur = db.execute(sql, tuple(values))
            affected = cur.rowcount
            db.close()
            return affected > 0
        except Exception as e:
            print(f"Error en update_category: {e}")
            return False

    def delete_category(self, category_id):
        try:
            db = self._get_db_connection()
            cur = db.execute("DELETE FROM categorias WHERE id = ?", (category_id,))
            affected = cur.rowcount
            db.close()
            return affected > 0
        except Exception as e:
            print(f"Error en delete_category: {e}")
            return False

    # --- Operaciones sobre subcategorías ---
    def list_subcategories(self):
        try:
            db = self._get_db_connection()
            cur = db.execute("SELECT id, nombre FROM subcategorias ORDER BY nombre COLLATE NOCASE")
            rows = cur.fetchall() or []
            result = []
            for r in rows:
                result.append({"id": r[0], "nombre": r[1]})
            db.close()
            return result
        except Exception as e:
            print(f"Error en list_subcategories: {e}")
            return []

    def get_subcategory_by_id(self, sub_id):
        try:
            db = self._get_db_connection()
            cur = db.execute("SELECT id, nombre FROM subcategorias WHERE id = ?", (sub_id,))
            r = cur.fetchone()
            db.close()
            if not r:
                return None
            return {"id": r[0], "nombre": r[1]}
        except Exception as e:
            print(f"Error en get_subcategory_by_id: {e}")
            return None

    def create_subcategory(self, data: dict):
        """Crea una subcategoría. Se espera que el usuario provea el id (entero) y nombre."""
        try:
            sub_id = data.get("id")
            nombre = data.get("nombre")
            if sub_id is None:
                print("Error: id de subcategoría requerido (no autoincremental).")
                return None
            if not nombre or not str(nombre).strip():
                print("Error: nombre de subcategoría requerido.")
                return None
            db = self._get_db_connection()
            db.execute("INSERT INTO subcategorias (id, nombre) VALUES (?, ?)", (int(sub_id), nombre.strip()))
            db.close()
            return int(sub_id)
        except Exception as e:
            print(f"Error en create_subcategory: {e}")
            return None

    def update_subcategory(self, sub_id, data: dict):
        try:
            db = self._get_db_connection()
            fields = []
            values = []
            if "nombre" in data:
                fields.append("nombre = ?")
                values.append(data.get("nombre"))
            if not fields:
                db.close()
                return False
            values.append(sub_id)
            sql = f"UPDATE subcategorias SET {', '.join(fields)} WHERE id = ?"
            cur = db.execute(sql, tuple(values))
            affected = cur.rowcount
            db.close()
            return affected > 0
        except Exception as e:
            print(f"Error en update_subcategory: {e}")
            return False

    def delete_subcategory(self, sub_id):
        try:
            db = self._get_db_connection()
            cur = db.execute("DELETE FROM subcategorias WHERE id = ?", (sub_id,))
            affected = cur.rowcount
            db.close()
            return affected > 0
        except Exception as e:
            print(f"Error en delete_subcategory: {e}")
            return False
