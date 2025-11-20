import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime


class VentasView(ctk.CTkFrame):
    """Vista de ventas con diseño moderno y atractivo."""
    
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Header principal con degradado simulado
        header = ctk.CTkFrame(self, fg_color="#1976D2", height=80, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        titulo = ctk.CTkLabel(
            header,
            text="💰 Punto de Venta",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        )
        titulo.pack(side="left", padx=30, pady=20)
        
        fecha_hora = ctk.CTkLabel(
            header,
            text=datetime.now().strftime("%d/%m/%Y - %H:%M"),
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        fecha_hora.pack(side="right", padx=30, pady=20)
        
        # Container principal
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Dividir en dos columnas
        main_container.grid_columnconfigure(0, weight=2)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # === COLUMNA IZQUIERDA: Productos y búsqueda ===
        left_panel = ctk.CTkFrame(main_container, corner_radius=10)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Búsqueda de productos
        search_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            search_frame,
            text="Buscar Producto:",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 8))
        
        search_input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_input_frame.pack(fill="x")
        
        self.entry_buscar_producto = ctk.CTkEntry(
            search_input_frame,
            placeholder_text="Código de barras, nombre o ID...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.entry_buscar_producto.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_buscar_producto = ctk.CTkButton(
            search_input_frame,
            text="🔍",
            width=50,
            height=40,
            font=ctk.CTkFont(size=18),
            fg_color="#4CAF50",
            hover_color="#43A047"
        )
        self.btn_buscar_producto.pack(side="left")
        
        # Separador
        ctk.CTkFrame(left_panel, height=2, fg_color="#e0e0e0").pack(fill="x", padx=15, pady=10)
        
        # Productos rápidos (grid de botones)
        productos_rapidos_label = ctk.CTkLabel(
            left_panel,
            text="⚡ Acceso Rápido:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        productos_rapidos_label.pack(anchor="w", padx=15, pady=(10, 8))
        
        productos_grid = ctk.CTkFrame(left_panel, fg_color="transparent")
        productos_grid.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Grid de productos destacados (ejemplo)
        colores = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F"]
        productos_ejemplo = [
            "Producto 1", "Producto 2", "Producto 3",
            "Producto 4", "Producto 5", "Producto 6"
        ]
        
        for i, (producto, color) in enumerate(zip(productos_ejemplo, colores)):
            fila = i // 3
            col = i % 3
            
            btn = ctk.CTkButton(
                productos_grid,
                text=producto,
                height=80,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=color,
                hover_color=self._darken_color(color),
                corner_radius=8
            )
            btn.grid(row=fila, column=col, padx=5, pady=5, sticky="nsew")
            productos_grid.grid_columnconfigure(col, weight=1)
        
        # === COLUMNA DERECHA: Carrito y total ===
        right_panel = ctk.CTkFrame(main_container, corner_radius=10, fg_color="#f5f5f5")
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        # Header del carrito
        carrito_header = ctk.CTkFrame(right_panel, fg_color="#FF6B6B", corner_radius=10)
        carrito_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            carrito_header,
            text="🛒 Carrito de Compra",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(pady=12)
        
        # Lista de items en el carrito
        carrito_scroll_frame = ctk.CTkScrollableFrame(
            right_panel,
            fg_color="white",
            corner_radius=8
        )
        carrito_scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.carrito_frame = carrito_scroll_frame
        
        # Mensaje vacío inicial
        self.carrito_vacio_label = ctk.CTkLabel(
            carrito_scroll_frame,
            text="El carrito está vacío\n\n🛍️",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.carrito_vacio_label.pack(expand=True, pady=40)
        
        # Total y botones de acción
        total_frame = ctk.CTkFrame(right_panel, fg_color="#f5f5f5")
        total_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Subtotal
        subtotal_row = ctk.CTkFrame(total_frame, fg_color="transparent")
        subtotal_row.pack(fill="x", pady=2)
        ctk.CTkLabel(
            subtotal_row,
            text="Subtotal:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left")
        self.label_subtotal = ctk.CTkLabel(
            subtotal_row,
            text="$0.00",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label_subtotal.pack(side="right")
        
        # Total
        ctk.CTkFrame(total_frame, height=2, fg_color="#e0e0e0").pack(fill="x", pady=5)
        total_row = ctk.CTkFrame(total_frame, fg_color="transparent")
        total_row.pack(fill="x", pady=2)
        ctk.CTkLabel(
            total_row,
            text="TOTAL:",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        self.label_total = ctk.CTkLabel(
            total_row,
            text="$0.00",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FF6B6B"
        )
        self.label_total.pack(side="right")
        
        # Botones de acción
        botones_frame = ctk.CTkFrame(right_panel, fg_color="#f5f5f5")
        botones_frame.pack(fill="x", padx=10, pady=(10, 10))
        
        self.btn_limpiar = ctk.CTkButton(
            botones_frame,
            text="🗑️ Limpiar",
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color="#9e9e9e",
            hover_color="#7e7e7e"
        )
        self.btn_limpiar.pack(fill="x", pady=(0, 8))
        
        self.btn_finalizar = ctk.CTkButton(
            botones_frame,
            text="✓ Finalizar Venta",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#43A047"
        )
        self.btn_finalizar.pack(fill="x")
    
    def _darken_color(self, hex_color):
        """Oscurece un color hex para hover."""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def agregar_item_carrito(self, producto, cantidad=1):
        """Agrega un item al carrito visualmente."""
        # Ocultar mensaje de carrito vacío
        if self.carrito_vacio_label.winfo_exists():
            self.carrito_vacio_label.pack_forget()
        
        # Crear frame para el item
        item_frame = ctk.CTkFrame(self.carrito_frame, fg_color="#f9f9f9", corner_radius=5)
        item_frame.pack(fill="x", padx=5, pady=3)
        
        # Nombre y precio
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(
            info_frame,
            text=producto.get('nombre', 'Producto'),
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        precio_cant_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        precio_cant_frame.pack(fill="x", pady=(3, 0))
        
        ctk.CTkLabel(
            precio_cant_frame,
            text=f"${producto.get('precio_venta', 0):.2f} x {cantidad}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(side="left")
        
        ctk.CTkLabel(
            precio_cant_frame,
            text=f"${producto.get('precio_venta', 0) * cantidad:.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4CAF50"
        ).pack(side="right")
    
    def actualizar_total(self, subtotal, total):
        """Actualiza los labels de subtotal y total."""
        self.label_subtotal.configure(text=f"${subtotal:.2f}")
        self.label_total.configure(text=f"${total:.2f}")
    
    def limpiar_carrito(self):
        """Limpia todos los items del carrito."""
        for widget in self.carrito_frame.winfo_children():
            widget.destroy()
        
        # Mostrar mensaje de carrito vacío
        self.carrito_vacio_label = ctk.CTkLabel(
            self.carrito_frame,
            text="El carrito está vacío\n\n🛍️",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.carrito_vacio_label.pack(expand=True, pady=40)
        
        self.actualizar_total(0, 0)
