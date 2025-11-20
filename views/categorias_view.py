import customtkinter as ctk
from tkinter import messagebox


class CategoriasView(ctk.CTkFrame):
    """Vista de categorías con grid en lugar de tksheet."""

    COLUMNS = [
        ("id", "ID", 60),
        ("nombre", "Nombre", 350),
        ("parent_id", "Padre ID", 100),
        ("descripcion", "Descripción", 250),
    ]

    def __init__(self, parent, controller=None, categorias=None):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True)

        # datos locales
        self._categorias = list(categorias or [])
        self._selected_id = None
        self._selected_row_idx = None
        self._row_widgets = []
        self._editing_row = None

        # Barra superior con búsqueda y botones
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=(8, 0))

        # búsqueda
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Buscar categoría...")
        self.search_entry.pack(side="left", padx=(0, 8))

        self.btn_search = ctk.CTkButton(search_frame, text="Buscar", width=80)
        self.btn_search.pack(side="left", padx=(0, 8))

        # Acciones
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=(6, 6))

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
        
        # Botón para abrir la gestión de subcategorías
        self.btn_subcategorias = ctk.CTkButton(actions, text="Subcategorías", width=140, fg_color="#9C27B0", hover_color="#7B1FA2", text_color="#ffffff")
        self.btn_subcategorias.pack(side="left", padx=(12, 6))

        # Título
        titulo = ctk.CTkLabel(self, text="Categorías", font=ctk.CTkFont(size=22, weight="bold"))
        titulo.pack(anchor="nw", pady=(2, 8), padx=10)

        # Grid container con scroll
        grid_container = ctk.CTkFrame(self, fg_color="#ffffff")
        grid_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Canvas y scrollbar
        self.canvas = ctk.CTkCanvas(grid_container, bg="#ffffff", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(grid_container, command=self.canvas.yview)
        self.scrollable_grid = ctk.CTkFrame(self.canvas, fg_color="#ffffff")

        # Expandir columnas para ocupar todo el ancho
        for i in range(len(self.COLUMNS)):
            self.scrollable_grid.grid_columnconfigure(i, weight=1)

        self.scrollable_window = self.canvas.create_window((0, 0), window=self.scrollable_grid, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def resize_scrollable_frame(event):
            self.canvas.itemconfig(self.scrollable_window, width=event.width)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.bind("<Configure>", resize_scrollable_frame)

        self._create_grid_header()
        self.build_rows()

        # Botones Guardar/Cancelar a la derecha (solo inicialización, no pack)
        self.btn_guardar = ctk.CTkButton(toolbar, text="Guardar", width=100, fg_color="#4CAF50", hover_color="#43A047", command=self._on_guardar_nueva_categoria)
        self.btn_cancelar = ctk.CTkButton(toolbar, text="Cancelar", width=100, fg_color="#f44336", hover_color="#d32f2f", command=self._on_cancelar_nueva_categoria)

    def _create_grid_header(self):
        """Crea el encabezado de la tabla con grid y tonos verdes, cada celda con borde."""
        header_green = "#43A047"
        header_text = "#ffffff"
        border_color = "#e0e0e0"
        for i, (key, label, width) in enumerate(self.COLUMNS):
            cell = ctk.CTkFrame(self.scrollable_grid, fg_color=header_green, border_width=1, border_color=border_color)
            cell.grid(row=0, column=i, sticky="nsew")
            lbl = ctk.CTkLabel(
                cell,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=header_text,
                anchor="w"
            )
            lbl.pack(fill="both", padx=10, pady=8)

    def build_rows(self, categorias=None):
        """Carga los datos en el grid desde `self._categorias` o `categorias` si se provee."""
        if categorias is not None:
            self._categorias = list(categorias)

        # Limpiar filas anteriores (excepto header en row 0)
        for widget_list in self._row_widgets:
            for widget in widget_list:
                widget.destroy()
        self._row_widgets.clear()
        self._selected_row_idx = None
        self._selected_id = None

        # Limitar a 50 registros
        categorias_display = self._categorias[:50]

        row_bg1 = "#f9f9f9"
        row_bg2 = "#ffffff"
        selected_bg = "#43A047"
        selected_text = "#ffffff"
        border_color = "#e0e0e0"

        for idx, cat in enumerate(categorias_display):
            row_num = idx + 1
            row_widgets = []
            for i, (key, label, width) in enumerate(self.COLUMNS):
                cell_bg = selected_bg if False else (row_bg1 if idx % 2 == 0 else row_bg2)
                cell = ctk.CTkFrame(self.scrollable_grid, fg_color=cell_bg, border_width=1, border_color=border_color)
                cell.grid(row=row_num, column=i, sticky="nsew")
                value = cat.get(key, "")
                lbl = ctk.CTkLabel(cell, text=str(value), anchor="w", text_color="black")
                lbl.pack(fill="both", padx=10, pady=8)
                lbl.bind("<Button-1>", lambda e, r=idx, c_id=cat.get("id"): self._on_row_select(r, c_id))
                row_widgets.append((cell, lbl))
            self._row_widgets.append(row_widgets)

        # Actualizar scroll region
        self.scrollable_grid.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_row_select(self, row_idx, cat_id):
        """Selecciona una fila visualmente y habilita botones. La fila seleccionada se pinta de verde en todas sus celdas."""
        selected_bg = "#43A047"
        selected_text = "#ffffff"
        row_bg1 = "#f9f9f9"
        row_bg2 = "#ffffff"

        # Deseleccionar fila anterior
        if self._selected_row_idx is not None and self._selected_row_idx < len(self._row_widgets):
            prev_row = self._row_widgets[self._selected_row_idx]
            for i, (cell, lbl) in enumerate(prev_row):
                cell.configure(fg_color=row_bg1 if self._selected_row_idx % 2 == 0 else row_bg2)
                lbl.configure(text_color="black")

        # Seleccionar nueva fila
        self._selected_row_idx = row_idx
        self._selected_id = cat_id

        if row_idx < len(self._row_widgets):
            row = self._row_widgets[row_idx]
            for i, (cell, lbl) in enumerate(row):
                cell.configure(fg_color=selected_bg)
                lbl.configure(text_color=selected_text)

        self.btn_borrar.configure(state="normal")
        self.btn_editar.configure(state="normal")

    def add_new_row(self):
        """Inserta una fila editable en posición 1 con campos de entrada. Botones Guardar/Cancelar van en la toolbar."""
        if self._editing_row is not None:
            messagebox.showwarning("Advertencia", "Ya hay una fila en edición")
            return

        # Mostrar botones en la toolbar si no están visibles
        if not self.btn_guardar.winfo_ismapped():
            self.btn_guardar.pack(side="right", padx=5)
        if not self.btn_cancelar.winfo_ismapped():
            self.btn_cancelar.pack(side="right", padx=5)

        # Crear frame editable en row 1 (fondo blanco)
        edit_frame = ctk.CTkFrame(self.scrollable_grid, fg_color="#FFFFFF")
        for i, (key, label, width) in enumerate(self.COLUMNS):
            edit_frame.grid_columnconfigure(i, weight=1)
        edit_frame.grid(row=1, column=0, columnspan=len(self.COLUMNS), sticky="nsew")

        # ID (automático, no editable)
        lbl_id = ctk.CTkLabel(edit_frame, text="(Auto)", anchor="w", text_color="#666")
        lbl_id.grid(row=0, column=0, padx=(16,4), pady=8, sticky="ew")

        # Nombre (editable, borde amarillo)
        entry_nombre = ctk.CTkEntry(edit_frame, placeholder_text="Nombre", border_color="#FFD600", border_width=2)
        entry_nombre.grid(row=0, column=1, padx=(16,4), pady=8, sticky="ew")
        entry_nombre.focus()

        # Parent ID (editable, borde amarillo)
        entry_parent = ctk.CTkEntry(edit_frame, placeholder_text="Padre ID (opcional)", border_color="#FFD600", border_width=2)
        entry_parent.grid(row=0, column=2, padx=(16,4), pady=8, sticky="ew")

        # Descripción (editable, borde amarillo)
        entry_desc = ctk.CTkEntry(edit_frame, placeholder_text="Descripción", border_color="#FFD600", border_width=2)
        entry_desc.grid(row=0, column=3, padx=(16,4), pady=8, sticky="ew")

        # Guardar referencias
        self._editing_row = {
            "edit_frame": edit_frame,
            "entries": {
                "nombre": entry_nombre,
                "parent_id": entry_parent,
                "descripcion": entry_desc
            }
        }

        # Mover todas las filas existentes hacia abajo
        for idx in range(len(self._row_widgets)):
            for i, (cell, lbl) in enumerate(self._row_widgets[idx]):
                cell.grid(row=idx + 2, column=i, sticky="nsew")

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_guardar_nueva_categoria(self):
        """Valida y guarda la nueva categoría."""
        if self._editing_row is None:
            return

        entries = self._editing_row["entries"]
        nombre = entries["nombre"].get().strip()
        parent_id_str = entries["parent_id"].get().strip()
        descripcion = entries["descripcion"].get().strip()

        # Validación: nombre es obligatorio
        if not nombre:
            messagebox.showwarning("Validación", "El nombre es obligatorio")
            return

        # Convertir parent_id
        parent_id = None
        if parent_id_str:
            try:
                parent_id = int(parent_id_str)
            except ValueError:
                messagebox.showwarning("Validación", "Padre ID debe ser un número")
                return

        # Delegar al controller
        if self.controller and hasattr(self.controller, "create_category"):
            try:
                self.controller.create_category(nombre, parent_id, descripcion)
                self._on_cancelar_nueva_categoria()
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear categoría: {e}")
        else:
            messagebox.showerror("Error", "No hay controller configurado")

    def _on_cancelar_nueva_categoria(self):
        """Cancela la creación y elimina la fila editable."""
        if self._editing_row is None:
            return

        # Ocultar botones de la toolbar
        if self.btn_guardar.winfo_ismapped():
            self.btn_guardar.pack_forget()
        if self.btn_cancelar.winfo_ismapped():
            self.btn_cancelar.pack_forget()

        # Destruir widgets
        self._editing_row["edit_frame"].destroy()
        self._editing_row = None

        # Restaurar posiciones de filas
        self.build_rows()

    def delete_selected(self):
        """Elimina la categoría seleccionada delegando al controller si existe.

        Si la eliminación es exitosa, se actualiza la lista local y la tabla.
        """
        if self._selected_id is None:
            messagebox.showinfo("Eliminar categoría", "Seleccione una categoría primero.")
            return

        confirmar = messagebox.askyesno("Confirmar borrado", "¿Eliminar la categoría seleccionada?")
        if not confirmar:
            return

        # delegar al controller si existe
        if self.controller and hasattr(self.controller, "delete_category"):
            try:
                self.controller.delete_category(self._selected_id)
            except Exception as e:
                messagebox.showerror("Error al borrar", f"Ocurrió un error al borrar: {e}")

        # actualizar listas locales
        try:
            self._categorias = [c for c in self._categorias if c.get("id") != self._selected_id]
        except Exception:
            pass

        self._selected_id = None
        self.btn_borrar.configure(state="disabled")
        self.btn_editar.configure(state="disabled")
        self.build_rows()

    def set_categories(self, categories_list):
        """Recibe una lista de dicts con las categorías y recarga la vista."""
        self._categorias = list(categories_list or [])
        self._selected_id = None
        self.btn_borrar.configure(state="disabled")
        self.btn_editar.configure(state="disabled")
        self.build_rows()

    def get_search_query(self):
        return self.search_entry.get().strip()

    def clear_search(self):
        self.search_entry.delete(0, 'end')
