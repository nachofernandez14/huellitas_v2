import customtkinter as ctk
from tkinter import messagebox


class SaldosProveedoresView(ctk.CTkFrame):
    """Vista para gestionar saldos de proveedores con pagos y pedidos."""
    
    def __init__(self, master, controller=None):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        # Variables
        self.proveedor_actual = None
        self.items_pedido = []
        self.movimientos_widgets = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Header
        header = ctk.CTkFrame(self, fg_color="#4CAF50", height=60)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        titulo = ctk.CTkLabel(
            header,
            text="💰 Gestión de Saldos de Proveedores",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        titulo.pack(pady=15)
        
        # Frame principal con dos columnas
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Columna izquierda: Info del proveedor y saldo
        left_column = ctk.CTkFrame(main_frame, fg_color="#2b2b2b", corner_radius=10)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Sección de proveedor
        proveedor_frame = ctk.CTkFrame(left_column, fg_color="#333333", corner_radius=8)
        proveedor_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            proveedor_frame,
            text="Proveedor Actual:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.lbl_proveedor_nombre = ctk.CTkLabel(
            proveedor_frame,
            text="No seleccionado",
            font=ctk.CTkFont(size=16),
            text_color="#00fe67"
        )
        self.lbl_proveedor_nombre.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Saldo actual
        saldo_frame = ctk.CTkFrame(left_column, fg_color="#1976D2", corner_radius=8)
        saldo_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            saldo_frame,
            text="Saldo Actual:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.lbl_saldo = ctk.CTkLabel(
            saldo_frame,
            text="$0.00",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        self.lbl_saldo.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Botones de acción
        botones_frame = ctk.CTkFrame(left_column, fg_color="transparent")
        botones_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.btn_agregar_pago = ctk.CTkButton(
            botones_frame,
            text="💵 Agregar Pago",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#43A047",
            height=40
        )
        self.btn_agregar_pago.pack(fill="x", pady=5)
        
        self.btn_crear_pedido = ctk.CTkButton(
            botones_frame,
            text="📋 Crear Pedido/Boleta",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#FF9800",
            hover_color="#F57C00",
            height=40
        )
        self.btn_crear_pedido.pack(fill="x", pady=5)
        
        self.btn_exportar_pdf = ctk.CTkButton(
            botones_frame,
            text="📄 Exportar Boleta a PDF",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2196F3",
            hover_color="#1976D2",
            height=40
        )
        self.btn_exportar_pdf.pack(fill="x", pady=5)
        
        # Columna derecha: Lista de movimientos con GRID
        right_column = ctk.CTkFrame(main_frame, fg_color="#2b2b2b", corner_radius=10)
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ctk.CTkLabel(
            right_column,
            text="Historial de Movimientos",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Frame con scroll para movimientos
        movimientos_container = ctk.CTkFrame(right_column, fg_color="transparent")
        movimientos_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Canvas y scrollbar
        canvas = ctk.CTkCanvas(movimientos_container, bg="#2b2b2b", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(movimientos_container, command=canvas.yview)
        self.scrollable_movimientos = ctk.CTkFrame(canvas, fg_color="transparent")
        
        self.scrollable_movimientos.grid_columnconfigure(0, weight=1)
        
        self.scrollable_window = canvas.create_window((0, 0), window=self.scrollable_movimientos, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas = canvas
        
        # Ajustar tamaño del frame al canvas
        def resize_scrollable_frame(event):
            canvas.itemconfig(self.scrollable_window, width=event.width)
            canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.bind("<Configure>", resize_scrollable_frame)
        
        # Header de la lista con grid
        self._create_grid_header()
    
    def _create_grid_header(self):
        """Crea el encabezado de la lista con grid."""
        header_frame = ctk.CTkFrame(self.scrollable_movimientos, fg_color="#424242", corner_radius=5)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 2))
        header_frame.grid_columnconfigure(0, minsize=60)  # ID
        header_frame.grid_columnconfigure(1, minsize=80)  # Tipo
        header_frame.grid_columnconfigure(2, minsize=100)  # Monto
        header_frame.grid_columnconfigure(3, weight=1)  # Descripción
        header_frame.grid_columnconfigure(4, minsize=120)  # Fecha
        
        headers = ["ID", "Tipo", "Monto", "Descripción", "Fecha"]
        for i, header_text in enumerate(headers):
            lbl = ctk.CTkLabel(
                header_frame,
                text=header_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white"
            )
            lbl.grid(row=0, column=i, padx=8, pady=8, sticky="w")
    
    def set_proveedor(self, proveedor_data):
        """Establece el proveedor actual."""
        self.proveedor_actual = proveedor_data
        self.lbl_proveedor_nombre.configure(text=proveedor_data.get('nombre', 'Sin nombre'))
        self.actualizar_saldo()
    
    def actualizar_saldo(self):
        """Actualiza el saldo mostrado."""
        if self.controller and self.proveedor_actual:
            saldo = self.controller.get_saldo_proveedor(self.proveedor_actual['id'])
            self.lbl_saldo.configure(text=f"${saldo:,.2f}")
    
    def cargar_movimientos(self, movimientos):
        """Carga los movimientos en el grid."""
        # Limpiar movimientos anteriores
        for widget in self.movimientos_widgets:
            widget.destroy()
        self.movimientos_widgets.clear()
        
        if not movimientos:
            return
        
        # Crear fila para cada movimiento
        for idx, mov in enumerate(movimientos, start=1):
            fila_frame = ctk.CTkFrame(
                self.scrollable_movimientos,
                fg_color="#3a3a3a" if idx % 2 == 0 else "#333333",
                corner_radius=3
            )
            fila_frame.grid(row=idx, column=0, sticky="ew", padx=5, pady=1)
            fila_frame.grid_columnconfigure(0, minsize=60)
            fila_frame.grid_columnconfigure(1, minsize=80)
            fila_frame.grid_columnconfigure(2, minsize=100)
            fila_frame.grid_columnconfigure(3, weight=1)
            fila_frame.grid_columnconfigure(4, minsize=120)
            
            # ID
            ctk.CTkLabel(
                fila_frame,
                text=str(mov.get('id', '')),
                font=ctk.CTkFont(size=10),
                text_color="#ffffff"
            ).grid(row=0, column=0, padx=8, pady=6, sticky="w")
            
            # Tipo
            tipo = mov.get('tipo', '').upper()
            tipo_color = "#4CAF50" if tipo == "PAGO" else "#FF9800"
            ctk.CTkLabel(
                fila_frame,
                text=tipo,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=tipo_color
            ).grid(row=0, column=1, padx=8, pady=6, sticky="w")
            
            # Monto
            ctk.CTkLabel(
                fila_frame,
                text=f"${mov.get('monto', 0):,.2f}",
                font=ctk.CTkFont(size=10),
                text_color="#66BB6A"
            ).grid(row=0, column=2, padx=8, pady=6, sticky="w")
            
            # Descripción
            ctk.CTkLabel(
                fila_frame,
                text=mov.get('descripcion', ''),
                font=ctk.CTkFont(size=10),
                text_color="#ffffff",
                anchor="w"
            ).grid(row=0, column=3, padx=8, pady=6, sticky="ew")
            
            # Fecha
            fecha = mov.get('fecha', '')[:16] if mov.get('fecha') else ''
            ctk.CTkLabel(
                fila_frame,
                text=fecha,
                font=ctk.CTkFont(size=10),
                text_color="#999999"
            ).grid(row=0, column=4, padx=8, pady=6, sticky="w")
            
            self.movimientos_widgets.append(fila_frame)
        
        # Actualizar región de scroll
        self.scrollable_movimientos.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
