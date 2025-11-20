import customtkinter as ctk
from tkinter import messagebox
import math


class AumentarProductosWindow(ctk.CTkToplevel):
    """Ventana para aumentar precios de productos de forma masiva."""
    
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        
        self.title("Aumentar Productos")
        self.geometry("1000x700")
        self.minsize(900, 600)
        self.resizable(True, True)
        
        # Centrar ventana
        self.transient(parent)
        self.grab_set()
        
        # Variables
        self.productos_cargados = []
        self.productos_widgets = []
        self.producto_seleccionado_idx = None
        self._calculo_timer = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Header con título
        header = ctk.CTkFrame(self, fg_color="#FF9800", height=60)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        titulo = ctk.CTkLabel(
            header,
            text="⬆️ Aumentar Precios de Productos",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        titulo.pack(pady=15)
        
        # Frame de filtros
        filtros_frame = ctk.CTkFrame(self, fg_color="transparent")
        filtros_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        # Búsqueda por nombre
        ctk.CTkLabel(
            filtros_frame,
            text="Buscar productos por nombre:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.entry_buscar = ctk.CTkEntry(
            filtros_frame,
            placeholder_text="Ej: Sieger",
            width=250,
            font=ctk.CTkFont(size=13)
        )
        self.entry_buscar.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=5)
        
        self.btn_buscar = ctk.CTkButton(
            filtros_frame,
            text="🔍 Buscar",
            width=100,
            fg_color="#4CAF50",
            hover_color="#43A047"
        )
        self.btn_buscar.grid(row=0, column=2, padx=5, pady=5)
        
        self.btn_cargar_todos = ctk.CTkButton(
            filtros_frame,
            text="📋 Cargar Todos",
            width=120,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        self.btn_cargar_todos.grid(row=0, column=3, padx=5, pady=5)
        
        # Frame de porcentaje de aumento
        porcentaje_frame = ctk.CTkFrame(self, fg_color="transparent")
        porcentaje_frame.pack(fill="x", padx=20, pady=(5, 10))
        
        ctk.CTkLabel(
            porcentaje_frame,
            text="Porcentaje de aumento:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.entry_porcentaje = ctk.CTkEntry(
            porcentaje_frame,
            placeholder_text="Ej: 8.5",
            width=120,
            font=ctk.CTkFont(size=13)
        )
        self.entry_porcentaje.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=5)
        
        # Bind para calcular automáticamente
        self.entry_porcentaje.bind("<KeyRelease>", self._on_porcentaje_change)
        
        ctk.CTkLabel(
            porcentaje_frame,
            text="%",
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=2, sticky="w", pady=5)
        
        self.btn_aplicar = ctk.CTkButton(
            porcentaje_frame,
            text="✓ Aplicar Aumento",
            width=150,
            fg_color="#FF5722",
            hover_color="#E64A19",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_aplicar.grid(row=0, column=3, padx=20, pady=5)
        
        # Separador
        separator = ctk.CTkFrame(self, height=2, fg_color="#cccccc")
        separator.pack(fill="x", padx=20, pady=10)
        
        # Frame para info y botón eliminar
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(0, 5))
        
        # Label informativo
        info_label = ctk.CTkLabel(
            info_frame,
            text="Productos cargados: 0",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_label.pack(side="left")
        self.info_label = info_label
        
        # Botón eliminar producto
        self.btn_eliminar = ctk.CTkButton(
            info_frame,
            text="🗑️ Eliminar Seleccionado",
            width=160,
            fg_color="#f44336",
            hover_color="#d32f2f",
            font=ctk.CTkFont(size=12)
        )
        self.btn_eliminar.pack(side="right")
        
        # Frame con scroll para la lista de productos
        productos_container = ctk.CTkFrame(self)
        productos_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Canvas y scrollbar
        canvas = ctk.CTkCanvas(productos_container, bg="#2b2b2b", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(productos_container, command=canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(canvas, fg_color="transparent")
        
        # Configure grid to expand
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.scrollable_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas = canvas
        # Ajustar tamaño del frame al canvas
        def resize_scrollable_frame(event):
            canvas.itemconfig(self.scrollable_window, width=event.width, height=event.height)
            canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.bind("<Configure>", resize_scrollable_frame)
        
        # Header de la lista (grid)
        self._create_list_header()
        
        # Frame de botones inferiores
        botones_frame = ctk.CTkFrame(self, fg_color="transparent")
        botones_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        btn_cerrar = ctk.CTkButton(
            botones_frame,
            text="Cerrar",
            width=100,
            fg_color="#9e9e9e",
            hover_color="#7e7e7e",
            command=self.destroy
        )
        btn_cerrar.pack(side="right")
    
    def _create_list_header(self):
        """Crea el encabezado de la lista con grid."""
        header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#424242", corner_radius=5)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 2))
        header_frame.grid_columnconfigure(0, minsize=80)  # ID
        header_frame.grid_columnconfigure(1, weight=1)  # Nombre (expandible)
        header_frame.grid_columnconfigure(2, minsize=150)  # Precio Actual
        header_frame.grid_columnconfigure(3, minsize=150)  # Precio Nuevo
        
        headers = ["ID", "Nombre", "Precio Actual", "Precio Nuevo"]
        for i, header_text in enumerate(headers):
            lbl = ctk.CTkLabel(
                header_frame,
                text=header_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            )
            lbl.grid(row=0, column=i, padx=10, pady=8, sticky="w")
    
    def cargar_productos(self, productos):
        """Carga productos en la lista visual con grid."""
        # Limpiar productos anteriores
        for widget in self.productos_widgets:
            widget.destroy()
        self.productos_widgets.clear()
        
        self.productos_cargados = productos
        self.info_label.configure(text=f"Productos cargados: {len(productos)}")
        
        # Crear fila para cada producto
        for idx, producto in enumerate(productos, start=1):
            fila_frame = ctk.CTkFrame(
                self.scrollable_frame,
                fg_color="#3a3a3a",
                corner_radius=3
            )
            fila_frame.grid(row=idx, column=0, sticky="ew", padx=5, pady=1)
            fila_frame.grid_columnconfigure(0, minsize=80)
            fila_frame.grid_columnconfigure(1, weight=1)
            fila_frame.grid_columnconfigure(2, minsize=150)
            fila_frame.grid_columnconfigure(3, minsize=150)
            
            # Bind click para seleccionar
            fila_idx = idx - 1
            fila_frame.bind("<Button-1>", lambda e, i=fila_idx: self._seleccionar_producto(i))
            
            # ID
            lbl_id = ctk.CTkLabel(
                fila_frame,
                text=str(producto.get('id', '')),
                font=ctk.CTkFont(size=11),
                text_color="#ffffff"
            )
            lbl_id.grid(row=0, column=0, padx=10, pady=8, sticky="w")
            lbl_id.bind("<Button-1>", lambda e, i=fila_idx: self._seleccionar_producto(i))
            
            # Nombre
            lbl_nombre = ctk.CTkLabel(
                fila_frame,
                text=producto.get('nombre', ''),
                font=ctk.CTkFont(size=11),
                text_color="#ffffff",
                anchor="w"
            )
            lbl_nombre.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
            lbl_nombre.bind("<Button-1>", lambda e, i=fila_idx: self._seleccionar_producto(i))
            
            # Precio Actual
            precio_actual = float(producto.get('precio_venta', 0))
            lbl_precio_actual = ctk.CTkLabel(
                fila_frame,
                text=f"${precio_actual:,.2f}",
                font=ctk.CTkFont(size=11),
                text_color="#66BB6A"
            )
            lbl_precio_actual.grid(row=0, column=2, padx=10, pady=8, sticky="w")
            lbl_precio_actual.bind("<Button-1>", lambda e, i=fila_idx: self._seleccionar_producto(i))
            
            # Precio Nuevo (placeholder)
            lbl_precio_nuevo = ctk.CTkLabel(
                fila_frame,
                text="--",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#FFA726"
            )
            lbl_precio_nuevo.grid(row=0, column=3, padx=10, pady=8, sticky="w")
            lbl_precio_nuevo.bind("<Button-1>", lambda e, i=fila_idx: self._seleccionar_producto(i))
            
            # Guardar referencias
            self.productos_widgets.append(fila_frame)
            producto['_fila_frame'] = fila_frame
            producto['_label_nuevo'] = lbl_precio_nuevo
    
    def calcular_precios_nuevos(self, porcentaje):
        """Calcula y muestra los nuevos precios con redondeo inteligente."""
        try:
            porcentaje_float = float(porcentaje)
        except ValueError:
            messagebox.showerror("Error", "Ingrese un porcentaje válido")
            return
        
        for producto in self.productos_cargados:
            precio_actual = float(producto.get('precio_venta', 0))
            precio_aumentado = precio_actual * (1 + porcentaje_float / 100)
            
            # Redondeo inteligente
            precio_final = self._redondear_inteligente(precio_aumentado)
            
            producto['precio_nuevo'] = precio_final
            
            # Actualizar label
            if '_label_nuevo' in producto:
                producto['_label_nuevo'].configure(text=f"${precio_final:,.2f}")
    
    def _redondear_inteligente(self, precio):
        """Redondea el precio de forma inteligente.
        
        Ejemplo: 55985 -> 56000
        """
        if precio < 100:
            # Precios bajos: redondear a 5
            return math.ceil(precio / 5) * 5
        elif precio < 1000:
            # Precios medios: redondear a 10
            return math.ceil(precio / 10) * 10
        elif precio < 10000:
            # Precios altos: redondear a 100
            return math.ceil(precio / 100) * 100
        else:
            # Precios muy altos: redondear a 1000
            return math.ceil(precio / 1000) * 1000
    
    def obtener_productos_actualizados(self):
        """Retorna la lista de productos con precios actualizados."""
        return [
            {
                'id': p.get('id'),
                'precio_venta': p.get('precio_nuevo', p.get('precio_venta'))
            }
            for p in self.productos_cargados
            if 'precio_nuevo' in p
        ]
    
    def _seleccionar_producto(self, idx):
        """Selecciona un producto de la lista."""
        # Deseleccionar anterior
        if self.producto_seleccionado_idx is not None:
            if self.producto_seleccionado_idx < len(self.productos_cargados):
                producto_anterior = self.productos_cargados[self.producto_seleccionado_idx]
                if '_fila_frame' in producto_anterior:
                    producto_anterior['_fila_frame'].configure(fg_color="#3a3a3a")
        
        # Seleccionar nuevo
        self.producto_seleccionado_idx = idx
        producto = self.productos_cargados[idx]
        if '_fila_frame' in producto:
            producto['_fila_frame'].configure(fg_color="#1976D2")
    
    def eliminar_producto_seleccionado(self):
        """Elimina el producto seleccionado de la lista."""
        if self.producto_seleccionado_idx is None:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
        
        if self.producto_seleccionado_idx >= len(self.productos_cargados):
            return
        
        # Eliminar producto
        producto = self.productos_cargados[self.producto_seleccionado_idx]
        self.productos_cargados.pop(self.producto_seleccionado_idx)
        
        # Actualizar vista
        self.producto_seleccionado_idx = None
        self.cargar_productos(self.productos_cargados)
    
    def _on_porcentaje_change(self, event):
        """Maneja el evento de cambio en el entry de porcentaje."""
        # Cancelar timer anterior si existe
        if self._calculo_timer is not None:
            self.after_cancel(self._calculo_timer)
        
        # Programar cálculo después de 200ms
        self._calculo_timer = self.after(200, self._calcular_automatico)
    
    def _calcular_automatico(self):
        """Calcula automáticamente los precios nuevos."""
        porcentaje = self.entry_porcentaje.get().strip()
        
        # Si está vacío o no hay productos, no hacer nada
        if not porcentaje or not self.productos_cargados:
            return
        
        # Intentar calcular
        try:
            porcentaje_float = float(porcentaje)
            if porcentaje_float <= 0:
                return
            self.calcular_precios_nuevos(porcentaje)
        except ValueError:
            # Si no es un número válido, no hacer nada
            pass
