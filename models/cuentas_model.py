from models.db import Database


class CuentasModel:
    def __init__(self):
        self.db_path = 'database/negocio.db'

    def _get_db_connection(self):
        """Crea una nueva conexión a la base de datos thread-safe."""
        return Database(self.db_path)

    def get_movimientos_by_proveedor(self, proveedor_id):
        """Obtiene todos los movimientos de cuenta para un proveedor específico."""
        try:
            db = self._get_db_connection()
            cur = db.execute("""
                SELECT id, fecha, movimiento, monto_movimiento, monto_boleta, saldo 
                FROM cuentas 
                WHERE proveedor = ? 
                ORDER BY fecha DESC, id DESC
            """, (proveedor_id,))
            rows = cur.fetchall() or []
            
            # convertir a dict
            columnas = ["id", "fecha", "movimiento", "monto_movimiento", "monto_boleta", "saldo"]
            result = []
            for row in rows:
                d = dict(zip(columnas, row))
                result.append(d)
            
            db.close()
            return result
        except Exception as e:
            print(f"Error al obtener movimientos de cuenta: {e}")
            return []

    def get_saldo_actual_by_proveedor(self, proveedor_id):
        """Obtiene el saldo actual del proveedor basado en el último movimiento."""
        try:
            db = self._get_db_connection()
            cur = db.execute("""
                SELECT saldo 
                FROM cuentas 
                WHERE proveedor = ? 
                ORDER BY fecha DESC, id DESC 
                LIMIT 1
            """, (proveedor_id,))
            row = cur.fetchone()
            db.close()
            
            if row:
                return float(row[0]) if row[0] is not None else 0.0
            return 0.0
        except Exception as e:
            print(f"Error al obtener saldo actual: {e}")
            return 0.0

    def create_movimiento(self, data: dict):
        """Crea un nuevo movimiento de cuenta."""
        try:
            db = self._get_db_connection()
            
            # Validación básica
            if not data.get("proveedor") or not data.get("fecha"):
                print("Error: Proveedor y fecha son requeridos")
                return None
            
            sql = """
                INSERT INTO cuentas (fecha, proveedor, movimiento, monto_movimiento, monto_boleta, saldo)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                data.get("fecha"),
                data.get("proveedor"),
                data.get("movimiento", 0),
                float(data.get("monto_movimiento", 0)) if data.get("monto_movimiento") else 0.0,
                float(data.get("monto_boleta", 0)) if data.get("monto_boleta") else 0.0,
                float(data.get("saldo", 0)) if data.get("saldo") else 0.0
            )
            
            cur = db.execute(sql, params)
            movimiento_id = cur.lastrowid
            db.close()
            return movimiento_id
            
        except Exception as e:
            print(f"Error al crear movimiento: {e}")
            return None