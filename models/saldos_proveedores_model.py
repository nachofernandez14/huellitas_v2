from models.db import Database
from datetime import datetime


class SaldosProveedoresModel:
    def __init__(self):
        self.db_path = 'database/negocio.db'
        self._create_tables_if_needed()

    def _get_db_connection(self):
        """Crea una nueva conexión a la base de datos thread-safe."""
        return Database(self.db_path)

    def _create_tables_if_needed(self):
        """Crea las tablas necesarias para el sistema de saldos."""
        try:
            db = self._get_db_connection()
            
            # Tabla de movimientos (pagos y pedidos)
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS movimientos_proveedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proveedor_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL,  -- 'pago' o 'pedido'
                    monto REAL NOT NULL,
                    descripcion TEXT,
                    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
                )
                """
            )
            
            # Tabla de boletas (asociadas a pedidos)
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS boletas_proveedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    movimiento_id INTEGER NOT NULL,
                    proveedor_id INTEGER NOT NULL,
                    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                    subtotal REAL NOT NULL DEFAULT 0,
                    total REAL NOT NULL DEFAULT 0,
                    estado TEXT DEFAULT 'activa',
                    FOREIGN KEY (movimiento_id) REFERENCES movimientos_proveedores(id),
                    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
                )
                """
            )
            
            # Tabla de items de boleta
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS boletas_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    boleta_id INTEGER NOT NULL,
                    producto_id INTEGER,
                    producto_nombre TEXT NOT NULL,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (boleta_id) REFERENCES boletas_proveedores(id),
                    FOREIGN KEY (producto_id) REFERENCES articulos(id)
                )
                """
            )
            
            db.close()
        except Exception as e:
            print(f"Error al crear tablas de saldos: {e}")

    def get_movimientos_proveedor(self, proveedor_id):
        """Obtiene todos los movimientos de un proveedor."""
        try:
            db = self._get_db_connection()
            cur = db.execute(
                """
                SELECT id, tipo, monto, descripcion, fecha
                FROM movimientos_proveedores
                WHERE proveedor_id = ?
                ORDER BY fecha DESC
                """,
                (proveedor_id,)
            )
            rows = cur.fetchall()
            db.close()
            
            columnas = ["id", "tipo", "monto", "descripcion", "fecha"]
            return [dict(zip(columnas, row)) for row in rows]
        except Exception as e:
            print(f"Error al obtener movimientos: {e}")
            return []

    def agregar_pago(self, proveedor_id, monto, descripcion=""):
        """Agrega un pago (disminuye el saldo)."""
        try:
            db = self._get_db_connection()
            
            # Insertar movimiento
            cur = db.execute(
                """
                INSERT INTO movimientos_proveedores (proveedor_id, tipo, monto, descripcion)
                VALUES (?, 'pago', ?, ?)
                """,
                (proveedor_id, float(monto), descripcion)
            )
            movimiento_id = cur.lastrowid
            
            # Actualizar saldo del proveedor (restar)
            db.execute(
                """
                UPDATE proveedores
                SET saldo = saldo - ?
                WHERE id = ?
                """,
                (float(monto), proveedor_id)
            )
            
            db.commit()
            db.close()
            return movimiento_id
        except Exception as e:
            print(f"Error al agregar pago: {e}")
            raise

    def crear_pedido_con_boleta(self, proveedor_id, items, descripcion="", fecha=None):
        """Crea un pedido con su boleta de productos asociada.
        
        items: lista de dicts con keys: producto_id, producto_nombre, cantidad, precio_unitario
        fecha: fecha de llegada del pedido (formato YYYY-MM-DD)
        """
        try:
            db = self._get_db_connection()
            
            # Calcular totales
            subtotal = sum(item['cantidad'] * item['precio_unitario'] for item in items)
            total = subtotal
            
            # Insertar movimiento de tipo pedido con fecha opcional
            if fecha:
                cur = db.execute(
                    """
                    INSERT INTO movimientos_proveedores (proveedor_id, tipo, monto, descripcion, fecha)
                    VALUES (?, 'pedido', ?, ?, ?)
                    """,
                    (proveedor_id, total, descripcion, fecha)
                )
            else:
                cur = db.execute(
                    """
                    INSERT INTO movimientos_proveedores (proveedor_id, tipo, monto, descripcion)
                    VALUES (?, 'pedido', ?, ?)
                    """,
                    (proveedor_id, total, descripcion)
                )
            movimiento_id = cur.lastrowid
            
            # Crear boleta con fecha opcional
            if fecha:
                cur = db.execute(
                    """
                    INSERT INTO boletas_proveedores (movimiento_id, proveedor_id, subtotal, total, fecha)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (movimiento_id, proveedor_id, subtotal, total, fecha)
                )
            else:
                cur = db.execute(
                    """
                    INSERT INTO boletas_proveedores (movimiento_id, proveedor_id, subtotal, total)
                    VALUES (?, ?, ?, ?)
                    """,
                    (movimiento_id, proveedor_id, subtotal, total)
                )
            boleta_id = cur.lastrowid
            
            # Insertar items de la boleta
            for item in items:
                subtotal_item = item['cantidad'] * item['precio_unitario']
                db.execute(
                    """
                    INSERT INTO boletas_items (boleta_id, producto_id, producto_nombre, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        boleta_id,
                        item.get('producto_id'),
                        item['producto_nombre'],
                        item['cantidad'],
                        item['precio_unitario'],
                        subtotal_item
                    )
                )
            
            # Actualizar saldo del proveedor (sumar)
            db.execute(
                """
                UPDATE proveedores
                SET saldo = saldo + ?
                WHERE id = ?
                """,
                (total, proveedor_id)
            )
            
            db.commit()
            db.close()
            return boleta_id
        except Exception as e:
            print(f"Error al crear pedido con boleta: {e}")
            raise

    def get_boleta_completa(self, boleta_id):
        """Obtiene una boleta completa con sus items."""
        try:
            db = self._get_db_connection()
            
            # Obtener info de boleta
            cur = db.execute(
                """
                SELECT b.id, b.fecha, b.subtotal, b.total, b.estado,
                       p.nombre as proveedor_nombre, p.telefono, p.direccion
                FROM boletas_proveedores b
                JOIN proveedores p ON b.proveedor_id = p.id
                WHERE b.id = ?
                """,
                (boleta_id,)
            )
            row = cur.fetchone()
            if not row:
                db.close()
                return None
            
            boleta = {
                "id": row[0],
                "fecha": row[1],
                "subtotal": row[2],
                "total": row[3],
                "estado": row[4],
                "proveedor_nombre": row[5],
                "proveedor_telefono": row[6],
                "proveedor_direccion": row[7]
            }
            
            # Obtener items
            cur = db.execute(
                """
                SELECT producto_nombre, cantidad, precio_unitario, subtotal
                FROM boletas_items
                WHERE boleta_id = ?
                """,
                (boleta_id,)
            )
            items = cur.fetchall()
            boleta['items'] = [
                {
                    "producto_nombre": item[0],
                    "cantidad": item[1],
                    "precio_unitario": item[2],
                    "subtotal": item[3]
                }
                for item in items
            ]
            
            db.close()
            return boleta
        except Exception as e:
            print(f"Error al obtener boleta: {e}")
            return None

    def get_saldo_proveedor(self, proveedor_id):
        """Obtiene el saldo actual de un proveedor."""
        try:
            db = self._get_db_connection()
            cur = db.execute(
                "SELECT saldo FROM proveedores WHERE id = ?",
                (proveedor_id,)
            )
            row = cur.fetchone()
            db.close()
            return row[0] if row else 0.0
        except Exception as e:
            print(f"Error al obtener saldo: {e}")
            return 0.0
