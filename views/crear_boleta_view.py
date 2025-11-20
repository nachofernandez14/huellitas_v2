import customtkinter as ctk
from tkinter import messagebox, simpledialog
from datetime import datetime


class CrearBoletaWindow(ctk.CTkToplevel):
    """Ventana para crear una boleta de pedido con productos."""
    
    def __init__(self, parent, controller=None, proveedor=None):
        super().__init__(parent)
        self.controller = controller
        self.proveedor = proveedor
        
        self.title(f"Crear Boleta - {proveedor.get('nombre', 'Proveedor')}")
        self.geometry("900x750")
        self.minsize(800, 650)
        
        # Centrar ventana
        self.transient(parent)
        self.grab_set()
        
        # Variables
        self.items_boleta = []
        self.items_widgets = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        # Header
        header = ctk.CTkFrame(self, fg_color="#FF9800", height=60)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        titulo = ctk.CTkLabel(
            header,
            text="📋 Nueva Boleta de Pedido",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        )
        titulo.pack(pady=15)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Sección de agregar producto
        agregar_frame = ctk.CTkFrame(main_frame, fg_color="#2b2b2b", corner_radius=10)
        agregar_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            agregar_frame,
            text="Agregar Producto a la Boleta",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Grid para inputs
        inputs_frame = ctk.CTkFrame(agregar_frame, fg_color="transparent")
        inputs_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Nombre del producto
        ctk.CTkLabel(
            inputs_frame,
            text="Producto:",
            font=ctk.CTkFont(size=13)
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.entry_producto = ctk.CTkEntry(
            inputs_frame,
            placeholder_text="Nombre del producto",
            width=250
        )
        self.entry_producto.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=5)
        
        # Cantidad
        ctk.CTkLabel(
            inputs_frame,
            text="Cantidad:",
            font=ctk.CTkFont(size=13)
        ).grid(row=0, column=2, sticky="w", padx=(0, 10), pady=5)
        
        self.entry_cantidad = ctk.CTkEntry(
            inputs_frame,
            placeholder_text="Ej: 10",
            width=100
        )
        self.entry_cantidad.grid(row=0, column=3, sticky="w", padx=(0, 20), pady=5)
        
        # Precio unitario
        ctk.CTkLabel(
            inputs_frame,
            text="Precio Unit.:",
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.entry_precio = ctk.CTkEntry(
            inputs_frame,
            placeholder_text="Ej: 1500.50",
            width=120
        )
        self.entry_precio.grid(row=1, column=1, sticky="w", pady=5)
        
        # Fecha de llegada
        ctk.CTkLabel(
            inputs_frame,
            text="Fecha Llegada:",
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=2, sticky="w", padx=(20, 10), pady=5)
        
        self.entry_fecha = ctk.CTkEntry(
            inputs_frame,
            placeholder_text=datetime.now().strftime("%Y-%m-%d"),
            width=120
        )
        self.entry_fecha.grid(row=1, column=3, sticky="w", pady=5)
        self.entry_fecha.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Fecha actual por defecto
        
        # Botón agregar
        self.btn_agregar_item = ctk.CTkButton(
            inputs_frame,
            text="➡ Agregar",
            fg_color="#4CAF50",
            hover_color="#43A047",
            width=120,
            command=self.on_agregar_item
        )
        self.btn_agregar_item.grid(row=2, column=3, sticky="w", pady=(10, 5))
        
        # Lista de items con GRID
        lista_frame = ctk.CTkFrame(main_frame, fg_color="#2b2b2b", corner_radius=10)
        lista_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        ctk.CTkLabel(
            lista_frame,
            text="Productos en la Boleta",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Canvas con scroll para items
        items_container = ctk.CTkFrame(lista_frame, fg_color="transparent")
        items_container.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        canvas = ctk.CTkCanvas(items_container, bg="#2b2b2b", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(items_container, command=canvas.yview)
        self.scrollable_items = ctk.CTkFrame(canvas, fg_color="transparent")
        
        self.scrollable_items.grid_columnconfigure(0, weight=1)
        
        self.scrollable_window = canvas.create_window((0, 0), window=self.scrollable_items, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas = canvas
        
        # Ajustar tamaño del frame al canvas
        def resize_scrollable_frame(event):
            canvas.itemconfig(self.scrollable_window, width=event.width)
            canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.bind("<Configure>", resize_scrollable_frame)
        
        # Header de la lista
        self._create_items_header()
        
        # Botón eliminar item
        btn_eliminar_frame = ctk.CTkFrame(lista_frame, fg_color="transparent")
        btn_eliminar_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.btn_eliminar_item = ctk.CTkButton(
            btn_eliminar_frame,
            text="🗑️ Eliminar Seleccionado",
            fg_color="#f44336",
            hover_color="#d32f2f",
            width=180,
            command=self.on_eliminar_item
        )
        self.btn_eliminar_item.pack(side="right")
        
        # Total y botones finales
        footer_frame = ctk.CTkFrame(main_frame, fg_color="#333333", corner_radius=10)
        footer_frame.pack(fill="x")
        
        # Total
        total_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        total_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            total_frame,
            text="TOTAL:",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        self.lbl_total = ctk.CTkLabel(
            total_frame,
            text="$0.00",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#4CAF50"
        )
        self.lbl_total.pack(side="left", padx=20)
        
        # Botones
        botones_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        botones_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        btn_cancelar = ctk.CTkButton(
            botones_frame,
            text="Cancelar",
            fg_color="#9e9e9e",
            hover_color="#7e7e7e",
            width=120,
            command=self.destroy
        )
        btn_cancelar.pack(side="right", padx=5)
        
        self.btn_guardar = ctk.CTkButton(
            botones_frame,
            text="✓ Guardar Boleta",
            fg_color="#FF9800",
            hover_color="#F57C00",
            width=150,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.on_guardar_boleta
        )
        self.btn_guardar.pack(side="right", padx=5)
    
    def _create_items_header(self):
        """Crea el encabezado de la lista de items con grid."""
        header_frame = ctk.CTkFrame(self.scrollable_items, fg_color="#424242", corner_radius=5)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 2))
        header_frame.grid_columnconfigure(0, weight=3)  # Producto
        header_frame.grid_columnconfigure(1, minsize=80)  # Cantidad
        header_frame.grid_columnconfigure(2, minsize=100)  # Precio Unit.
        header_frame.grid_columnconfigure(3, minsize=100)  # Subtotal
        
        headers = ["Producto", "Cantidad", "Precio Unit.", "Subtotal"]
        for i, header_text in enumerate(headers):
            lbl = ctk.CTkLabel(
                header_frame,
                text=header_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white"
            )
            lbl.grid(row=0, column=i, padx=8, pady=8, sticky="w")
    
    def on_agregar_item(self):
        """Agrega un item a la boleta."""
        # Validar campos
        producto = self.entry_producto.get().strip()
        if not producto:
            messagebox.showwarning("Advertencia", "Ingrese el nombre del producto")
            return
        
        try:
            cantidad = int(self.entry_cantidad.get().strip())
            if cantidad <= 0:
                raise ValueError()
        except:
            messagebox.showwarning("Advertencia", "Ingrese una cantidad válida")
            return
        
        try:
            precio = float(self.entry_precio.get().strip())
            if precio <= 0:
                raise ValueError()
        except:
            messagebox.showwarning("Advertencia", "Ingrese un precio válido")
            return
        
        # Agregar item
        subtotal = cantidad * precio
        item = {
            'producto_nombre': producto,
            'cantidad': cantidad,
            'precio_unitario': precio,
            'subtotal': subtotal
        }
        self.items_boleta.append(item)
        
        # Actualizar vista
        self._actualizar_grid()
        
        # Limpiar campos
        self.entry_producto.delete(0, 'end')
        self.entry_cantidad.delete(0, 'end')
        self.entry_precio.delete(0, 'end')
        self.entry_producto.focus()
    
    def on_eliminar_item(self):
        """Elimina el item seleccionado (el último agregado)."""
        if not self.items_boleta:
            messagebox.showwarning("Advertencia", "No hay items para eliminar")
            return
        
        # Eliminar el último item
        self.items_boleta.pop()
        self._actualizar_grid()
    
    def _actualizar_grid(self):
        """Actualiza el grid de items y el total."""
        # Limpiar widgets anteriores
        for widget in self.items_widgets:
            widget.destroy()
        self.items_widgets.clear()
        
        total = 0
        
        # Crear fila para cada item
        for idx, item in enumerate(self.items_boleta, start=1):
            fila_frame = ctk.CTkFrame(
                self.scrollable_items,
                fg_color="#3a3a3a" if idx % 2 == 0 else "#333333",
                corner_radius=3
            )
            fila_frame.grid(row=idx, column=0, sticky="ew", padx=5, pady=1)
            fila_frame.grid_columnconfigure(0, weight=3)
            fila_frame.grid_columnconfigure(1, minsize=80)
            fila_frame.grid_columnconfigure(2, minsize=100)
            fila_frame.grid_columnconfigure(3, minsize=100)
            
            # Producto
            ctk.CTkLabel(
                fila_frame,
                text=item['producto_nombre'],
                font=ctk.CTkFont(size=10),
                text_color="#ffffff",
                anchor="w"
            ).grid(row=0, column=0, padx=8, pady=6, sticky="ew")
            
            # Cantidad
            ctk.CTkLabel(
                fila_frame,
                text=str(item['cantidad']),
                font=ctk.CTkFont(size=10),
                text_color="#ffffff"
            ).grid(row=0, column=1, padx=8, pady=6, sticky="w")
            
            # Precio unitario
            ctk.CTkLabel(
                fila_frame,
                text=f"${item['precio_unitario']:,.2f}",
                font=ctk.CTkFont(size=10),
                text_color="#66BB6A"
            ).grid(row=0, column=2, padx=8, pady=6, sticky="w")
            
            # Subtotal
            ctk.CTkLabel(
                fila_frame,
                text=f"${item['subtotal']:,.2f}",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#FFA726"
            ).grid(row=0, column=3, padx=8, pady=6, sticky="w")
            
            self.items_widgets.append(fila_frame)
            total += item['subtotal']
        
        self.lbl_total.configure(text=f"${total:,.2f}")
        
        # Actualizar región de scroll
        self.scrollable_items.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_guardar_boleta(self):
        """Guarda la boleta en la base de datos."""
        if not self.items_boleta:
            messagebox.showwarning("Advertencia", "Agregue al menos un producto a la boleta")
            return
        
        # Obtener fecha
        fecha = self.entry_fecha.get().strip()
        if not fecha:
            messagebox.showwarning("Advertencia", "Ingrese la fecha de llegada")
            return
        
        # Pedir descripción opcional
        descripcion = simpledialog.askstring(
            "Descripción",
            "Ingrese una descripción para el pedido (opcional):"
        ) or ""
        
        try:
            boleta_id = self.controller.crear_pedido_con_items(self.items_boleta, descripcion, fecha)
            messagebox.showinfo("Éxito", f"Boleta #{boleta_id} creada correctamente para la fecha {fecha}")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear boleta: {e}")
