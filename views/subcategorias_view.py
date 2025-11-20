import customtkinter as ctk
from tkinter import messagebox


class SubcategoriasView(ctk.CTkFrame):
    """Vista de subcategorías con grid en lugar de tksheet."""

    COLUMNS = [
        ("id", "ID", 80),
        ("nombre", "Nombre", 300),
    ]

    def __init__(self, parent, controller=None, subcategorias=None):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)

        # datos locales
        self._subcategorias = list(subcategorias or [])
        self._selected_id = None
        self._selected_row_idx = None
        self._row_widgets = []
        self._editing_row = None

        # Acciones en una sola fila (más compacto)
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=(8, 6))

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

        titulo = ctk.CTkLabel(self, text="Subcategorías", font=ctk.CTkFont(size=18, weight="bold"))
        titulo.pack(anchor="nw", pady=(6, 8), padx=10)

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

    def build_rows(self, subcategorias=None):
        """Carga los datos en el grid desde `self._subcategorias` o `subcategorias` si se provee."""
        if subcategorias is not None:
            self._subcategorias = list(subcategorias)

        # Limpiar filas anteriores (excepto header en row 0)
        for widget_list in self._row_widgets:
            for widget in widget_list:
                widget.destroy()
        self._row_widgets.clear()
        self._selected_row_idx = None
        self._selected_id = None

        # Limitar a 50 registros
        subcategorias_display = self._subcategorias[:50]

        for idx, sub in enumerate(subcategorias_display):
            row_num = idx + 1  # Header está en row 0
            row_frame = ctk.CTkFrame(self.scrollable_grid, fg_color="#f9f9f9" if idx % 2 == 0 else "#ffffff", corner_radius=0)
            row_frame.grid(row=row_num, column=0, sticky="ew", padx=0, pady=0)

            # Configurar columnas
            for i, (key, label, width) in enumerate(self.COLUMNS):
                row_frame.grid_columnconfigure(i, minsize=width)

            row_widgets = []

            # ID
            id_val = sub.get("id", "")
            lbl_id = ctk.CTkLabel(row_frame, text=str(id_val) if id_val else "", anchor="w")
            lbl_id.grid(row=0, column=0, padx=10, pady=8, sticky="ew")
            row_widgets.append(lbl_id)

            # Nombre
            nombre_val = sub.get("nombre", "")
            lbl_nombre = ctk.CTkLabel(row_frame, text=str(nombre_val), anchor="w")
            lbl_nombre.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
            row_widgets.append(lbl_nombre)

            # Hacer clickeable la fila para seleccionar
            for widget in row_widgets:
                widget.bind("<Button-1>", lambda e, r=idx, s_id=sub.get("id"): self._on_row_select(r, s_id))

            self._row_widgets.append(row_widgets)

        # Actualizar scroll region
        self.scrollable_grid.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_row_select(self, row_idx, sub_id):
        """Selecciona una fila visualmente y habilita botones."""
        # Deseleccionar fila anterior
        if self._selected_row_idx is not None and self._selected_row_idx < len(self._row_widgets):
            for widget in self._row_widgets[self._selected_row_idx]:
                widget.configure(text_color="black")

        # Seleccionar nueva fila
        self._selected_row_idx = row_idx
        self._selected_id = sub_id

        if row_idx < len(self._row_widgets):
            for widget in self._row_widgets[row_idx]:
                widget.configure(text_color="#2196F3")

        self.btn_borrar.configure(state="normal")
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

        # ID (automático, no editable)
        lbl_id = ctk.CTkLabel(edit_frame, text="(Auto)", anchor="w", text_color="#666")
        lbl_id.grid(row=0, column=0, padx=10, pady=8, sticky="ew")

        # Nombre (editable)
        entry_nombre = ctk.CTkEntry(edit_frame, placeholder_text="Nombre")
        entry_nombre.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        entry_nombre.focus()

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
                "nombre": entry_nombre
            }
        }

        # Mover todas las filas existentes hacia abajo
        for idx in range(len(self._row_widgets)):
            row_num = idx + 3  # Header=0, edit=1, buttons=2, data starts at 3
            frame_parent = self._row_widgets[idx][0].master
            frame_parent.grid(row=row_num)

        # Configurar comandos
        btn_guardar.configure(command=self._on_guardar_nueva_subcategoria)
        btn_cancelar.configure(command=self._on_cancelar_nueva_subcategoria)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_guardar_nueva_subcategoria(self):
        """Valida y guarda la nueva subcategoría."""
        if self._editing_row is None:
            return

        entries = self._editing_row["entries"]
        nombre = entries["nombre"].get().strip()

        # Validación: nombre es obligatorio
        if not nombre:
            messagebox.showwarning("Validación", "El nombre es obligatorio")
            return

        # Delegar al controller
        if self.controller and hasattr(self.controller, "create_subcategory"):
            try:
                self.controller.create_subcategory(nombre)
                self._on_cancelar_nueva_subcategoria()
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear subcategoría: {e}")
        else:
            messagebox.showerror("Error", "No hay controller configurado")

    def _on_cancelar_nueva_subcategoria(self):
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
        """Elimina la subcategoría seleccionada delegando al controller si existe."""
        if self._selected_id is None:
            messagebox.showinfo("Eliminar subcategoría", "Seleccione una subcategoría primero.")
            return

        confirmar = messagebox.askyesno("Confirmar borrado", "¿Eliminar la subcategoría seleccionada?")
        if not confirmar:
            return

        # delegar al controller si existe
        if self.controller and hasattr(self.controller, "delete_subcategory"):
            try:
                self.controller.delete_subcategory(self._selected_id)
            except Exception as e:
                messagebox.showerror("Error al borrar", f"Ocurrió un error al borrar: {e}")

        # actualizar listas locales
        try:
            self._subcategorias = [s for s in self._subcategorias if s.get("id") != self._selected_id]
        except Exception:
            pass

        self._selected_id = None
        self.btn_borrar.configure(state="disabled")
        self.btn_editar.configure(state="disabled")
        self.build_rows()

    def set_subcategories(self, subcategories_list):
        """Recibe una lista de dicts con las subcategorías y recarga la vista."""
        self._subcategorias = list(subcategories_list or [])
        self._selected_id = None
        self.btn_borrar.configure(state="disabled")
        self.btn_editar.configure(state="disabled")
        self.build_rows()
