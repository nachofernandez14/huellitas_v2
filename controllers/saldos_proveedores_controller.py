from models.saldos_proveedores_model import SaldosProveedoresModel
from views.saldos_proveedores_view import SaldosProveedoresView
from tkinter import simpledialog, messagebox
import customtkinter as ctk


class SaldosProveedoresController:
    """Controlador para la gestión de saldos de proveedores."""
    
    def __init__(self, master, proveedor_data, app_controller=None):
        self.master = master
        self.app_controller = app_controller
        self.proveedor_data = proveedor_data
        
        # Crear modelo y vista
        self.model = SaldosProveedoresModel()
        self.view = SaldosProveedoresView(master, controller=self)
        
        # Configurar comandos
        self._setup_button_commands()
        
        # Cargar datos iniciales
        self.view.set_proveedor(proveedor_data)
        self._cargar_movimientos()
    
    def _setup_button_commands(self):
        """Configura los comandos de los botones."""
        self.view.btn_agregar_pago.configure(command=self.on_agregar_pago)
        self.view.btn_crear_pedido.configure(command=self.on_crear_pedido)
        self.view.btn_exportar_pdf.configure(command=self.on_exportar_pdf)
    
    def _cargar_movimientos(self):
        """Carga los movimientos del proveedor actual."""
        if not self.proveedor_data:
            return
        
        movimientos = self.model.get_movimientos_proveedor(self.proveedor_data['id'])
        self.view.cargar_movimientos(movimientos)
        self.view.actualizar_saldo()
    
    def get_saldo_proveedor(self, proveedor_id):
        """Obtiene el saldo del proveedor."""
        return self.model.get_saldo_proveedor(proveedor_id)
    
    def on_agregar_pago(self):
        """Abre diálogo para agregar un pago."""
        if not self.proveedor_data:
            messagebox.showwarning("Advertencia", "No hay proveedor seleccionado")
            return
        
        # Pedir monto
        monto = simpledialog.askfloat(
            "Agregar Pago",
            f"Ingrese el monto del pago para {self.proveedor_data['nombre']}:",
            minvalue=0.01
        )
        
        if monto is None:
            return
        
        # Pedir descripción (opcional)
        descripcion = simpledialog.askstring(
            "Descripción",
            "Ingrese una descripción (opcional):"
        ) or ""
        
        try:
            self.model.agregar_pago(self.proveedor_data['id'], monto, descripcion)
            messagebox.showinfo("Éxito", f"Pago de ${monto:,.2f} registrado correctamente")
            self._cargar_movimientos()
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar pago: {e}")
    
    def on_crear_pedido(self):
        """Abre ventana para crear un pedido con boleta."""
        if not self.proveedor_data:
            messagebox.showwarning("Advertencia", "No hay proveedor seleccionado")
            return
        
        # Abrir ventana de creación de boleta
        from views.crear_boleta_view import CrearBoletaWindow
        ventana = CrearBoletaWindow(self.view, controller=self, proveedor=self.proveedor_data)
        ventana.wait_window()
        
        # Recargar movimientos
        self._cargar_movimientos()
    
    def crear_pedido_con_items(self, items, descripcion="", fecha=None):
        """Crea un pedido con los items de la boleta."""
        try:
            boleta_id = self.model.crear_pedido_con_boleta(
                self.proveedor_data['id'],
                items,
                descripcion,
                fecha
            )
            return boleta_id
        except Exception as e:
            raise
    
    def on_exportar_pdf(self):
        """Exporta la última boleta a PDF."""
        if not self.proveedor_data:
            messagebox.showwarning("Advertencia", "No hay proveedor seleccionado")
            return
        
        # Obtener última boleta del proveedor
        movimientos = self.model.get_movimientos_proveedor(self.proveedor_data['id'])
        pedidos = [m for m in movimientos if m['tipo'] == 'pedido']
        
        if not pedidos:
            messagebox.showwarning("Advertencia", "No hay boletas para exportar")
            return
        
        # Obtener el último pedido
        ultimo_pedido = pedidos[0]
        
        # Aquí iría la lógica para encontrar la boleta asociada y exportar a PDF
        # Por ahora, mostrar mensaje
        messagebox.showinfo("Exportar PDF", "Funcionalidad de exportación a PDF en desarrollo")
