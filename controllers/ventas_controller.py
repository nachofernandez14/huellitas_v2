from tkinter import messagebox
from views.ventas_view import VentasView


class VentasController:
    """Controlador para la vista de ventas."""
    
    def __init__(self, master, app_controller=None):
        self.master = master
        self.app_controller = app_controller
        self.view = VentasView(master, controller=self)
        
        # Carrito actual
        self.carrito = []
        
        self._setup_button_commands()
    
    def _setup_button_commands(self):
        """Configura los comandos de los botones."""
        try:
            self.view.btn_buscar_producto.configure(command=self.on_buscar_producto)
            self.view.btn_limpiar.configure(command=self.on_limpiar_carrito)
            self.view.btn_finalizar.configure(command=self.on_finalizar_venta)
            
            # Enter en búsqueda
            self.view.entry_buscar_producto.bind("<Return>", lambda e: self.on_buscar_producto())
        except Exception as e:
            print(f"Error configurando botones: {e}")
    
    def on_buscar_producto(self):
        """Busca un producto y lo agrega al carrito."""
        query = self.view.entry_buscar_producto.get().strip()
        if not query:
            return
        
        # Aquí iría la lógica para buscar en la BD
        # Por ahora, simulamos un producto
        producto_ejemplo = {
            'id': 1,
            'nombre': f'Producto: {query}',
            'precio_venta': 1500.00,
            'cantidad': 10
        }
        
        self.agregar_al_carrito(producto_ejemplo, cantidad=1)
        self.view.entry_buscar_producto.delete(0, 'end')
    
    def agregar_al_carrito(self, producto, cantidad=1):
        """Agrega un producto al carrito."""
        # Verificar si ya existe en el carrito
        for item in self.carrito:
            if item['producto']['id'] == producto['id']:
                item['cantidad'] += cantidad
                self._actualizar_vista_carrito()
                return
        
        # Agregar nuevo item
        self.carrito.append({
            'producto': producto,
            'cantidad': cantidad
        })
        
        self._actualizar_vista_carrito()
    
    def _actualizar_vista_carrito(self):
        """Actualiza la vista del carrito."""
        # Limpiar carrito visual
        self.view.limpiar_carrito()
        
        # Agregar items
        subtotal = 0
        for item in self.carrito:
            producto = item['producto']
            cantidad = item['cantidad']
            self.view.agregar_item_carrito(producto, cantidad)
            subtotal += producto['precio_venta'] * cantidad
        
        # Actualizar total
        total = subtotal  # Aquí podrían aplicarse descuentos, impuestos, etc.
        self.view.actualizar_total(subtotal, total)
    
    def on_limpiar_carrito(self):
        """Limpia el carrito."""
        if not self.carrito:
            return
        
        confirmar = messagebox.askyesno(
            "Limpiar carrito",
            "¿Desea limpiar el carrito?"
        )
        
        if confirmar:
            self.carrito.clear()
            self.view.limpiar_carrito()
    
    def on_finalizar_venta(self):
        """Finaliza la venta actual."""
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "Agregue productos al carrito antes de finalizar la venta")
            return
        
        # Calcular total
        total = sum(item['producto']['precio_venta'] * item['cantidad'] for item in self.carrito)
        
        # Confirmar venta
        confirmar = messagebox.askyesno(
            "Finalizar venta",
            f"Total de la venta: ${total:.2f}\n\n¿Confirma la venta?"
        )
        
        if confirmar:
            # Aquí iría la lógica para guardar la venta en BD
            # y actualizar el stock de productos
            
            messagebox.showinfo("Venta completada", f"Venta registrada correctamente\n\nTotal: ${total:.2f}")
            
            # Limpiar carrito
            self.carrito.clear()
            self.view.limpiar_carrito()
