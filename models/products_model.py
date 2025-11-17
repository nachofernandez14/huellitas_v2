from models.db import Database


class ProductsModel:
    def __init__(self):
        self.db_path = 'database/negocio.db'  # Guardar la ruta en lugar de la instancia
        self._create_table_if_needed()

    def _get_db_connection(self):
        """Crea una nueva conexión a la base de datos thread-safe."""
        return Database(self.db_path)

    def _create_table_if_needed(self):
        """Crea la tabla si no existe."""
        try:
            db = self._get_db_connection()
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS articulos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    id_categoria INTEGER,
                    subcategoria TEXT,
                    id_proveedor INTEGER,
                    precio_costo REAL NOT NULL,
                    precio_venta REAL NOT NULL,
                    cantidad INTEGER NOT NULL,
                    estado TEXT NOT NULL DEFAULT 'activo',
                    codigo_barras TEXT,
                    FOREIGN KEY(id_categoria) REFERENCES categorias(id),
                    FOREIGN KEY(id_proveedor) REFERENCES proveedores(id)
                )
                """
            )
            # crear índice en nombre para búsquedas case-insensitive más rápidas
            try:
                db.execute("CREATE INDEX IF NOT EXISTS idx_articulos_nombre ON articulos (nombre COLLATE NOCASE)")
            except Exception:
                pass
            db.close()
        except Exception as e:
            print(f"Error al crear tabla: {e}")

    def search_products(self, query: str = None, limit: int = 50, offset: int = 0):
        """Busca productos en la BD aplicando LIMIT/OFFSET. Devuelve (rows_list, total_count).

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
            count_sql = f"SELECT COUNT(*) FROM articulos{where}"
            cur = db.execute(count_sql, tuple(params) if params else ())
            total = cur.fetchone()[0] if cur else 0

            sql = (
                "SELECT id, nombre, id_categoria, subcategoria, id_proveedor, precio_costo, precio_venta, cantidad, estado, codigo_barras "
                f"FROM articulos{where} LIMIT ? OFFSET ?"
            )
            params_page = list(params) if params else []
            params_page.extend([limit, offset])
            cur2 = db.execute(sql, tuple(params_page))
            rows = cur2.fetchall() if cur2 else []

            result = []
            for r in rows:
                result.append({
                    "id": r[0],
                    "nombre": r[1],
                    "id_categoria": r[2],
                    "subcategoria": r[3],
                    "id_proveedor": r[4],
                    "precio_costo": r[5],
                    "precio_venta": r[6],
                    "cantidad": r[7],
                    "estado": r[8],
                    "codigo_barras": r[9],
                })

            db.close()
            return result, total
        except Exception as e:
            print(f"Error en search_products: {e}")
            # en caso de error, devolver lista vacía
            return [], 0

    def get_all(self, use_db: bool = True):
        """Devuelve la lista de productos.

        Si use_db es True intentará leer desde la base de datos.
        Por defecto usa la base de datos.
        """
        try:
            db = self._get_db_connection()
            cursor = db.execute(
                "SELECT id, nombre, id_categoria, subcategoria, id_proveedor, precio_costo, precio_venta, cantidad, estado, codigo_barras FROM articulos"
            )
            rows = cursor.fetchall()
            result = []
            for r in rows:
                result.append({
                    "id": r[0],
                    "nombre": r[1],
                    "id_categoria": r[2],
                    "subcategoria": r[3],
                    "id_proveedor": r[4],
                    "precio_costo": r[5],
                    "precio_venta": r[6],
                    "cantidad": r[7],
                    "estado": r[8],
                    "codigo_barras": r[9],
                })
            db.close()
            return result
        except Exception as e:
            print(f"Error en get_all: {e}")
            return []

    def get_by_id(self, product_id):
        try:
            db = self._get_db_connection()
            cursor = db.execute(
                "SELECT id, nombre, id_categoria, subcategoria, id_proveedor, precio_costo, precio_venta, cantidad, estado, codigo_barras FROM articulos WHERE id = ?",
                (product_id,)
            )
            r = cursor.fetchone()
            db.close()
            if not r:
                return None
            return {
                "id": r[0],
                "nombre": r[1],
                "id_categoria": r[2],
                "subcategoria": r[3],
                "id_proveedor": r[4],
                "precio_costo": r[5],
                "precio_venta": r[6],
                "cantidad": r[7],
                "estado": r[8],
                "codigo_barras": r[9],
            }
        except Exception as e:
            print(f"Error en get_by_id: {e}")
            return None

    def create_product(self, data: dict):
        """Inserta un nuevo producto en la base de datos. Devuelve el id insertado o None."""
        try:
            db = self._get_db_connection()
            cursor = db.execute(
                "INSERT INTO articulos (nombre, id_categoria, subcategoria, id_proveedor, precio_costo, precio_venta, cantidad, estado, codigo_barras) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    data.get("nombre"),
                    data.get("id_categoria"),
                    data.get("subcategoria"),
                    data.get("id_proveedor"),
                    data.get("precio_costo", 0.0),
                    data.get("precio_venta", 0.0),
                    data.get("cantidad", 0),
                    data.get("estado", "activo"),
                    data.get("codigo_barras"),
                ),
            )
            product_id = cursor.lastrowid
            db.close()
            return product_id
        except Exception as e:
            print(f"Error en create_product: {e}")
            return None

    def update_product(self, product_id, data: dict):
        """Actualiza un producto. Devuelve True si se actualizó al menos una fila."""
        try:
            db = self._get_db_connection()
            # construir SET dinámico
            fields = []
            values = []
            for key in ("nombre", "id_categoria", "subcategoria", "id_proveedor", "precio_costo", "precio_venta", "cantidad", "estado", "codigo_barras"):
                if key in data:
                    fields.append(f"{key} = ?")
                    values.append(data[key])

            if not fields:
                db.close()
                return False

            values.append(product_id)
            sql = f"UPDATE articulos SET {', '.join(fields)} WHERE id = ?"
            cursor = db.execute(sql, tuple(values))
            result = cursor.rowcount > 0
            db.close()
            return result
        except Exception as e:
            print(f"Error en update_product: {e}")
            return False

    def delete_product(self, product_id):
        """Borra un producto por id. Devuelve True si se borró una fila."""
        try:
            db = self._get_db_connection()
            cursor = db.execute("DELETE FROM articulos WHERE id = ?", (product_id,))
            result = cursor.rowcount > 0
            db.close()
            return result
        except Exception as e:
            print(f"Error en delete_product: {e}")
            return False

    def add_product(self, data: dict):
        """Alias para create_product para compatibilidad con el controller."""
        return self.create_product(data)


