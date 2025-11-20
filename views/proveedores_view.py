import customtkinter as ctk
from tkinter import messagebox


class ProveedoresView(ctk.CTkFrame):
    """Vista de proveedores con grid en lugar de tksheet."""

    COLUMNS = [
        ("nombre", "Nombre", 300),
        ("telefono", "Teléfono", 180),
        ("saldo", "Saldo", 150),
    ]

    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self.pack(fill="both", expand=True)
        
        # Guardar referencia al controller
        self.controller = controller

        # datos internos
        self._proveedores = []
        self._selected_proveedor = None
        self._selected_row_idx = None
        self._row_widgets = []
        self._editing_row = None

        # barra de herramientas
        toolbar = ctk.CTkFrame(self, height=40, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=(8, 0))

        # barra de búsqueda
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Nombre del proveedor...")
        self.search_entry.pack(side="left", padx=(0, 8))
        
        self.btn_search = ctk.CTkButton(search_frame, text="Buscar", width=80)
        self.btn_search.pack(side="left", padx=(0, 8))

        # Barra de acciones completa (todos los botones en el mismo frame horizontal)
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=(6, 6))

        # botones de acción principales en verde a la izquierda
        green = "#4CAF50"
        green_hover = "#43A047"
        self.btn_agregar = ctk.CTkButton(actions, text="Agregar", width=120, fg_color=green, hover_color=green_hover, text_color="#ffffff")
        self.btn_agregar.pack(side="left", padx=6)

        self.btn_editar = ctk.CTkButton(actions, text="Editar", width=120, fg_color="#2196F3", hover_color="#1976D2", text_color="#ffffff")
        self.btn_editar.pack(side="left", padx=6)
        self.btn_editar.configure(state="disabled")

        self.btn_borrar = ctk.CTkButton(actions, text="Borrar", width=120, fg_color=green, hover_color="#d32f2f", text_color="#ffffff")
        self.btn_borrar.pack(side="left", padx=6)
        self.btn_borrar.configure(state="disabled")

        # Botón Ver Saldo - más separado y con color diferente
        self.btn_ver_saldo = ctk.CTkButton(actions, text="Ver Saldo", width=120, fg_color="#2196F3", hover_color="#1976D2", text_color="#ffffff")
        self.btn_ver_saldo.pack(side="left", padx=(20, 6))
        self.btn_ver_saldo.configure(state="disabled")

        # Título
        titulo = ctk.CTkLabel(self, text="Proveedores", font=ctk.CTkFont(size=22, weight="bold"))
        titulo.pack(anchor="nw", pady=(2, 8), padx=10)

        # Grid container con scroll
        grid_container = ctk.CTkFrame(self, fg_color="transparent")
        grid_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Canvas y scrollbar
        self.canvas = ctk.CTkCanvas(grid_container, bg="#2b2b2b", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(grid_container, command=self.canvas.yview)
        self.scrollable_grid = ctk.CTkFrame(self.canvas, fg_color="transparent")

        self.scrollable_grid.grid_columnconfigure(0, weight=1)

        self.scrollable_window = self.canvas.create_window((0, 0), window=self.scrollable_grid, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Ajustar tamaño del frame al canvas
        def resize_scrollable_frame(event):
            self.canvas.itemconfig(self.scrollable_window, width=event.width)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.bind("<Configure>", resize_scrollable_frame)

        # Crear header
        self._create_grid_header()

        # Cargar datos iniciales
        self.build_rows()

    def _create_grid_header(self):
        """Crea el encabezado de la tabla con grid."""
        header_frame = ctk.CTkFrame(self.scrollable_grid, fg_color="#bfecc0", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        for i, (key, label, width) in enumerate(self.COLUMNS):
            header_frame.grid_columnconfigure(i, minsize=width)
            lbl = ctk.CTkLabel(
                header_frame,
                text=label,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#000000",
                anchor="w"
            )
            lbl.grid(row=0, column=i, padx=10, pady=8, sticky="ew")

    def build_rows(self, proveedores=None):
        """Carga los datos en el grid desde `self._proveedores` o `proveedores` si se provee."""
        if proveedores is not None:
            self._proveedores = list(proveedores)

        # Limpiar filas anteriores (excepto header en row 0)
        for widget_list in self._row_widgets:
            for widget in widget_list:
                widget.destroy()
        self._row_widgets.clear()
        self._selected_row_idx = None
        self._selected_proveedor = None

        # Limitar a 50 registros
        proveedores_display = self._proveedores[:50]

        for idx, prov in enumerate(proveedores_display):
            row_num = idx + 1  # Header está en row 0
            row_frame = ctk.CTkFrame(self.scrollable_grid, fg_color="#f9f9f9" if idx % 2 == 0 else "#ffffff", corner_radius=0)
            row_frame.grid(row=row_num, column=0, sticky="ew", padx=0, pady=0)

            # Configurar columnas
            for i, (key, label, width) in enumerate(self.COLUMNS):
                row_frame.grid_columnconfigure(i, minsize=width)

            row_widgets = []

            # Nombre
            nombre_val = prov.get("nombre", "")
            lbl_nombre = ctk.CTkLabel(row_frame, text=str(nombre_val), anchor="w")
            lbl_nombre.grid(row=0, column=0, padx=10, pady=8, sticky="ew")
            row_widgets.append(lbl_nombre)

            # Teléfono
            telefono_val = prov.get("telefono", "")
            lbl_telefono = ctk.CTkLabel(row_frame, text=str(telefono_val), anchor="w")
            lbl_telefono.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
            row_widgets.append(lbl_telefono)

            # Saldo
            saldo_val = prov.get("saldo", "")
            lbl_saldo = ctk.CTkLabel(row_frame, text=str(saldo_val), anchor="w")
            lbl_saldo.grid(row=0, column=2, padx=10, pady=8, sticky="ew")
            row_widgets.append(lbl_saldo)

            # Hacer clickeable la fila para seleccionar
            for widget in row_widgets:
                widget.bind("<Button-1>", lambda e, r=idx, p=prov: self._on_row_select(r, p))

            self._row_widgets.append(row_widgets)

        # Actualizar scroll region
        self.scrollable_grid.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_row_select(self, row_idx, proveedor):
        """Selecciona una fila visualmente y habilita botones."""
        # Deseleccionar fila anterior
        if self._selected_row_idx is not None and self._selected_row_idx < len(self._row_widgets):
            for widget in self._row_widgets[self._selected_row_idx]:
                widget.configure(text_color="black")

        # Seleccionar nueva fila
        self._selected_row_idx = row_idx
        self._selected_proveedor = proveedor

        if row_idx < len(self._row_widgets):
            for widget in self._row_widgets[row_idx]:
                widget.configure(text_color="#2196F3")

        self.btn_borrar.configure(state="normal")
        self.btn_ver_saldo.configure(state="normal")
        self.btn_editar.configure(state="normal")

    def add_new_row(self):
        """Inserta una fila editable en posición 1 con campos de entrada y botones Guardar/Cancelar."""
        if self._editing_row is not None:
            messagebox.showwarning("Advertencia", "Ya hay una fila en edición")
            return

        # Crear frame editable en row 1
        edit_frame = ctk.CTkFrame(self.scrollable_grid, fg_color="#fff3cd", corner_radius=0)
        edit_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)

        # Configurar columnas
        for i, (key, label, width) in enumerate(self.COLUMNS):
            edit_frame.grid_columnconfigure(i, minsize=width)

        # Nombre (editable)
        entry_nombre = ctk.CTkEntry(edit_frame, placeholder_text="Nombre")
        entry_nombre.grid(row=0, column=0, padx=10, pady=8, sticky="ew")
        entry_nombre.focus()

        # Teléfono (editable)
        entry_telefono = ctk.CTkEntry(edit_frame, placeholder_text="Teléfono")
        entry_telefono.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        # Saldo (editable)
        entry_saldo = ctk.CTkEntry(edit_frame, placeholder_text="Saldo (0.00)")
        entry_saldo.grid(row=0, column=2, padx=10, pady=8, sticky="ew")

        # Botones Guardar y Cancelar
        btn_frame = ctk.CTkFrame(self.scrollable_grid, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        btn_guardar = ctk.CTkButton(btn_frame, text="Guardar", width=100, fg_color="#4CAF50", hover_color="#43A047")
        btn_guardar.pack(side="left", padx=5)

        btn_cancelar = ctk.CTkButton(btn_frame, text="Cancelar", width=100, fg_color="#f44336", hover_color="#d32f2f")
        btn_cancelar.pack(side="left", padx=5)

        # Guardar referencias
        self._editing_row = {
            "edit_frame": edit_frame,
            "btn_frame": btn_frame,
            "entries": {
                "nombre": entry_nombre,
                "telefono": entry_telefono,
                "saldo": entry_saldo
            }
        }

        # Mover todas las filas existentes hacia abajo
        for idx in range(len(self._row_widgets)):
            row_num = idx + 3  # Header=0, edit=1, buttons=2, data starts at 3
            frame_parent = self._row_widgets[idx][0].master
            frame_parent.grid(row=row_num)

        # Configurar comandos
        btn_guardar.configure(command=self._on_guardar_nuevo_proveedor)
        btn_cancelar.configure(command=self._on_cancelar_nuevo_proveedor)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_guardar_nuevo_proveedor(self):
        """Valida y guarda el nuevo proveedor."""
        if self._editing_row is None:
            return

        entries = self._editing_row["entries"]
        nombre = entries["nombre"].get().strip()
        telefono = entries["telefono"].get().strip()
        saldo_str = entries["saldo"].get().strip()

        # Validación: nombre es obligatorio
        if not nombre:
            messagebox.showwarning("Validación", "El nombre es obligatorio")
            return

        # Validar saldo (debe ser numérico)
        saldo = 0.0
        if saldo_str:
            try:
                saldo = float(saldo_str)
            except ValueError:
                messagebox.showwarning("Validación", "El saldo debe ser un número")
                return

        # Delegar al controller
        if self.controller and hasattr(self.controller, "create_proveedor"):
            try:
                self.controller.create_proveedor(nombre, telefono, saldo)
                self._on_cancelar_nuevo_proveedor()
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear proveedor: {e}")
        else:
            messagebox.showerror("Error", "No hay controller configurado")

    def _on_cancelar_nuevo_proveedor(self):
        """Cancela la creación y elimina la fila editable."""
        if self._editing_row is None:
            return

        # Destruir widgets
        self._editing_row["edit_frame"].destroy()
        self._editing_row["btn_frame"].destroy()
        self._editing_row = None

        # Restaurar posiciones de filas
        self.build_rows()

    def delete_selected(self):
        """Elimina el proveedor seleccionado delegando al controller si existe."""
        if self._selected_proveedor is None:
            messagebox.showinfo("Eliminar proveedor", "Seleccione un proveedor primero.")
            return

        confirmar = messagebox.askyesno("Confirmar borrado", "¿Eliminar el proveedor seleccionado?")
        if not confirmar:
            return

        # delegar al controller si existe
        if self.controller and hasattr(self.controller, "delete_proveedor"):
            try:
                nombre = self._selected_proveedor.get("nombre")
                self.controller.delete_proveedor(nombre)
            except Exception as e:
                messagebox.showerror("Error al borrar", f"Ocurrió un error al borrar: {e}")

        # actualizar listas locales
        try:
            self._proveedores = [p for p in self._proveedores if p.get("nombre") != self._selected_proveedor.get("nombre")]
        except Exception:
            pass

        self._selected_proveedor = None
        self.btn_borrar.configure(state="disabled")
        self.btn_ver_saldo.configure(state="disabled")
        self.btn_editar.configure(state="disabled")
        self.build_rows()

    def set_proveedores(self, proveedores_list):
        """Recibe una lista de proveedores y recarga la vista."""
        self._proveedores = list(proveedores_list or [])
        self._selected_proveedor = None
        self.btn_borrar.configure(state="disabled")
        self.btn_ver_saldo.configure(state="disabled")
        self.btn_editar.configure(state="disabled")
        self.build_rows()

    def get_search_query(self):
        return self.search_entry.get().strip()

    def clear_search(self):
        self.search_entry.delete(0, 'end')

    def get_selected_proveedor(self):
        return self._selected_proveedor
