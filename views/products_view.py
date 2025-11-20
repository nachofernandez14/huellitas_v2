import customtkinter as ctk
from tkinter import messagebox
from tksheet import Sheet


class ProductsView(ctk.CTkFrame):
    """Vista de productos montada dentro de `frame_contenido`.

    Muestra una tabla scrollable con las columnas del modelo `articulos`.
    Permite seleccionar una fila; al seleccionar se habilitan Editar/Borrar.
    """
    COLUMNS = [
        ("id", "ID"),
        ("nombre", "Nombre"),
        ("id_categoria", "Cat. ID"),
        ("subcategoria", "Subcategoria"),
        ("id_proveedor", "Prov. ID"),
        ("precio_costo", "Precio Costo"),
        ("precio_venta", "Precio Venta"),
        ("cantidad", "Cantidad"),
        ("codigo_barras", "Código barras"),
    ]

    # Anchos por columna como porcentajes del ancho total
    COLUMN_WIDTHS = {
        "id": 50,
        "nombre": 300,  # La más ancha
        "id_categoria": 80,
        "subcategoria": 120,
        "id_proveedor": 80,
        "precio_costo": 100,
        "precio_venta": 100,
        "cantidad": 40,
        "codigo_barras": 180,  # Más ancho para códigos de 13 dígitos
    }
    
    # Peso relativo para expansión (basado en importancia visual)
    COLUMN_WEIGHTS = {
        "id": 1,
        "nombre": 4,  # La columna más importante, que se expande más
        "id_categoria": 1,
        "subcategoria": 2,
        "id_proveedor": 1,
        "precio_costo": 2,
        "precio_venta": 2,
        "cantidad": 1,  # Más pequeña - reducida de 1 a 0.8
        "codigo_barras": 3,  # Más grande - aumentada de 2 a 3
    }

    # Header background (verde claro) and text (negro)
    HEADER_BG_COLOR = "#bfecc0"  # verde claro de fondo para columnas
    HEADER_TEXT_COLOR = "#000000"  # texto negro sobre fondo verde
    # Row selection: un verde más pastel
    ROW_HIGHLIGHT = "#dff3df"

    def __init__(self, master, controller=None, productos=None):
        super().__init__(master)
        self.controller = controller
        
        # Inicializar atributos críticos PRIMERO
        self._editor_row = None
        self._selected_id = None
        self._selected_widget = None
        self._search_after_id = None
        self._last_query = None
        
        # mantener la lista local completa y una lista filtrada para la vista
        self._all_products = list(productos or [])
        self._productos = list(self._all_products)
        self.pack(fill="both", expand=True)

        # Buscador encima de los botones
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(10, 6))
        self.search_entry = ctk.CTkEntry(search_frame, width=320, placeholder_text="Buscar por nombre...")
        self.search_entry.pack(side="left", padx=(0, 6))
        
        search_btn = ctk.CTkButton(search_frame, text="Buscar", width=100, fg_color="#1976D2", hover_color="#155fa0", text_color="#ffffff")
        search_btn.pack(side="left", padx=(0, 6))
        clear_btn = ctk.CTkButton(search_frame, text="Limpiar", width=100, fg_color="#9e9e9e", hover_color="#7e7e7e", text_color="#ffffff")
        clear_btn.pack(side="left")
        
        # Exponer los botones de búsqueda para que el controller pueda configurarlos
        self.search_btn = search_btn
        self.clear_btn = clear_btn

        # Barra de acciones completa (todos los botones en el mismo frame horizontal)
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=(6, 6))

        # botones de acción principales en verde a la izquierda - SIN comandos (serán asignados por el controller)
        green = "#4CAF50"
        green_hover = "#43A047"
        self.btn_agregar = ctk.CTkButton(toolbar, text="Agregar", width=120, fg_color=green, hover_color=green_hover, text_color="#ffffff")
        self.btn_agregar.pack(side="left", padx=6)
        self.btn_borrar = ctk.CTkButton(toolbar, text="Borrar", width=120, fg_color=green, hover_color="#d32f2f", text_color="#ffffff")
        self.btn_borrar.pack(side="left", padx=6)

        # Botón "Aumentar productos" para ajuste masivo de precios
        self.btn_aumentar = ctk.CTkButton(toolbar, text="Aumentar productos", width=160, fg_color="#FF9800", hover_color="#F57C00", text_color="#ffffff")
        self.btn_aumentar.pack(side="left", padx=6)

        # inicialmente deshabilitado borrar
        self.btn_borrar.configure(state="disabled")

        # Título
        titulo = ctk.CTkLabel(self, text="Productos", font=ctk.CTkFont(size=22, weight="bold"))
        titulo.pack(anchor="nw", pady=(2, 8), padx=10)

        # Crear el Sheet (tksheet) para la tabla de productos
        self.sheet = Sheet(
            self,
            headers=[label for _, label in self.COLUMNS],
            height=400
        )
        # Habilitar todos los bindings incluyendo edición
        self.sheet.enable_bindings(
            "single_select",
            "row_select",
            "column_width_resize",
            "arrowkeys",
            "right_click_popup_menu",
            "rc_select",
            "rc_insert_row",
            "rc_delete_row",
            "copy",
            "cut",
            "paste",
            "delete",
            "undo",
            "edit_cell"
        )
        self.sheet.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar anchos mínimos de columna
        # Nombre y Código de barras serán más anchas
        column_config = [
            ("id", 10),
            ("nombre", 500),  # Mucho más ancha para nombres largos
            ("id_categoria", 80),
            ("subcategoria", 150),
            ("id_proveedor", 90),
            ("precio_costo", 120),
            ("precio_venta", 120),
            ("cantidad", 80),
            ("codigo_barras", 180),
        ]
        
        
        # Hacer que el sheet se expanda para llenar el espacio
        self.sheet.set_options(
            auto_resize_columns=True,  # Auto ajustar al contenido
            expand_sheet_if_paste_too_big=True,
            column_width=120,
            header_height=25,
            default_row_height=22
        )
        
        # Configurar colores y estilos
        self.sheet.set_options(
            font=("Arial", 10, "normal"),
            header_font=("Arial", 10, "bold"),
            header_bg="#bfecc0",
            header_fg="#000000",
            table_bg="white",
            table_fg="black",
            index_bg="#f0f0f0",
            top_left_bg="#f0f0f0",
            outline_color="#cccccc",
            outline_thickness=1
        )
        
        # Bind para detectar selección
        self.sheet.bind("<<SheetSelect>>", self._on_sheet_select)
        # Bind para detectar cuando se termina de editar una celda
        self.sheet.extra_bindings("end_edit_cell", self._on_cell_edit)

        # paginado: número de filas por página
        self.PAGE_SIZE = 50
        self._current_page = 0
        self._total = 0

        # frame de paginación (Prev / Page / Next)
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.prev_btn = ctk.CTkButton(self.pagination_frame, text="Anterior", width=100, command=lambda: self._change_page(-1), fg_color="#9e9e9e", hover_color="#7e7e7e", text_color="#ffffff")
        self.prev_btn.pack(side="left", padx=(0, 6))
        self.page_label = ctk.CTkLabel(self.pagination_frame, text="Página 0 / 0")
        self.page_label.pack(side="left")
        self.next_btn = ctk.CTkButton(self.pagination_frame, text="Siguiente", width=100, command=lambda: self._change_page(1), fg_color="#4CAF50", hover_color="#43A047", text_color="#ffffff")
        self.next_btn.pack(side="left", padx=(6, 0))

        # paginado: número de filas por página
        self.PAGE_SIZE = 50
        self._current_page = 0
        self._total = 0

        # construir filas desde la lista local (vista inicial vacía o con página inicial)
        self.build_rows()

    def build_rows(self, productos=None):
        """Construye la vista con las filas actualmente en `self._productos`.
        Espera que la lista ya contenga solo la página solicitada.
        """
        # Limpiar datos previos del sheet
        self.sheet.set_sheet_data([[]])
        
        # Preparar los datos para tksheet
        data = []
        for p in self._productos:
            row = []
            for key, _ in self.COLUMNS:
                value = p.get(key, "")
                
                # Manejo especial de valores None o vacíos
                if value is None:
                    display_value = ""
                elif key in ("precio_costo", "precio_venta") and str(value).strip() != "":
                    try:
                        display_value = f"${float(value):.2f}"
                    except Exception:
                        display_value = str(value) if value is not None else ""
                elif key in ("id_categoria", "id_proveedor", "cantidad"):
                    # Para campos numéricos, mostrar como entero o vacío
                    try:
                        display_value = str(int(value)) if value is not None and str(value).strip() != "" else ""
                    except Exception:
                        display_value = str(value) if value is not None else ""
                elif key == "codigo_barras":
                    # Para código de barras, mantener como texto exacto para preservar ceros
                    display_value = str(value) if value is not None and str(value).strip() != "" else ""
                else:
                    # Para texto normal
                    display_value = str(value) if value is not None else ""
                
                row.append(display_value)
            data.append(row)
        
        # Establecer los datos en el sheet
        if data:
            self.sheet.set_sheet_data(data)
            
            # Ajustar automáticamente el ancho de la columna "Nombre" (índice 1)
            try:
                # Calcular el ancho máximo necesario para la columna "Nombre"
                nombre_col_idx = 1  # La columna "Nombre" es la segunda (índice 1)
                max_length = len(self.COLUMNS[nombre_col_idx][1])  # Empezar con el ancho del header
                
                # Verificar el largo de cada nombre en los datos
                for row in data:
                    if nombre_col_idx < len(row):
                        cell_length = len(str(row[nombre_col_idx]))
                        if cell_length > max_length:
                            max_length = cell_length
                
                # Calcular el ancho en píxeles (aproximadamente 8 píxeles por carácter)
                # Agregar un margen de 20 píxeles para el padding
                optimal_width = max(200, min(500, max_length * 8 + 20))
                
                # Establecer el ancho de la columna "Nombre"
                self.sheet.column_width(column=nombre_col_idx, width=optimal_width)
                
                # Alinear todas las columnas a la izquierda
                for col_idx in range(len(self.COLUMNS)):
                    self.sheet.align_columns(columns=[col_idx], align="w")
            except Exception as e:
                print(f"Error ajustando ancho de columnas: {e}")
        else:
            self.sheet.set_sheet_data([[""] * len(self.COLUMNS)])

        
    
    
    def _on_sheet_select(self, event):
        """Maneja la selección de filas en el sheet."""
        selected = self.sheet.get_currently_selected()
        if selected and selected.row is not None:
            row_idx = selected.row
            if 0 <= row_idx < len(self._productos):
                producto = self._productos[row_idx]
                self._selected_id = producto.get("id")
                self._selected_widget = None  # No usado con tksheet
                # habilitar botón borrar
                self.btn_borrar.configure(state="normal")
    
    def _on_cell_edit(self, event):
        """Maneja cuando se termina de editar una celda y guarda en la BD."""
        try:
            # event es un objeto EditCellEvent con row, column, key, value
            row_idx = event.row
            col_idx = event.column
            new_value = event.value
            
            if 0 <= row_idx < len(self._productos):
                # Obtener el producto de esta fila
                producto = self._productos[row_idx]
                producto_id = producto.get("id")
                
                # Obtener el key de la columna editada
                if col_idx < len(self.COLUMNS):
                    key, _ = self.COLUMNS[col_idx]
                    
                    # No actualizar el ID
                    if key == "id":
                        return
                    
                    # Construir dict con el valor actualizado
                    updated_data = dict(producto)  # Copiar todo el producto
                    
                    # Formatear el nuevo valor según el tipo
                    if key in ("precio_costo", "precio_venta"):
                        try:
                            clean_value = str(new_value).replace("$", "").replace(",", "").strip()
                            updated_data[key] = float(clean_value) if clean_value else 0.0
                            # Actualizar la celda con formato de precio
                            if clean_value:
                                self.sheet.set_cell_data(row_idx, col_idx, f"${float(clean_value):.2f}")
                        except:
                            updated_data[key] = 0.0
                    elif key in ("id_categoria", "id_proveedor", "cantidad"):
                        try:
                            updated_data[key] = int(new_value) if new_value and str(new_value).strip() else None
                        except:
                            updated_data[key] = None
                    else:
                        updated_data[key] = str(new_value) if new_value else ""
                    
                    # Actualizar el producto local primero
                    self._productos[row_idx].update(updated_data)
                    
                    # Llamar al controller para actualizar en BD
                    if self.controller and hasattr(self.controller, "update_product_from_sheet"):
                        self.controller.update_product_from_sheet(producto_id, updated_data, row_idx)
        except Exception as e:
            print(f"Error al guardar edición: {e}")
            import traceback
            traceback.print_exc()

    # removed _append_rows (we render page-sized product lists directly)
    
    def add_new_row(self):
        """Agrega una fila vacía al inicio del sheet para crear un nuevo producto."""
        # Agregar un producto temporal a la lista interna
        new_product = {key: "" for key, _ in self.COLUMNS}
        new_product["id"] = None  # Sin ID todavía
        self._productos.insert(0, new_product)
        
        # Reconstruir la vista con el nuevo producto incluido
        self.build_rows()
        
        # Seleccionar la primera fila, columna "nombre" (segunda columna)
        self.sheet.see(0, 0)
        self.sheet.select_cell(0, 1)  # Seleccionar columna "nombre" para empezar a editar

    def _on_edit(self):
        """Handler para el botón Editar: delega al controller si existe.

        Si no hay selección, avisa al usuario. Si el controller no implementa
        `edit_product`, muestra un mensaje informativo.
        """
        if self._selected_id is None:
            messagebox.showinfo("Editar producto", "Seleccione un producto primero.")
            return

        if self.controller and hasattr(self.controller, "edit_product"):
            try:
                # delegar al controller (este debería manejar la UI de edición y el refresh)
                self.controller.edit_product(self._selected_id)
            except Exception as e:
                messagebox.showerror("Error al editar", f"Ocurrió un error al editar: {e}")
        else:
            messagebox.showinfo("Editar producto", "Funcionalidad de edición no disponible.")

    def set_page(self, rows, page, page_size, total):
        """Recibe una página de resultados desde el controller y actualiza la vista."""
        try:
            self._productos = list(rows or [])
            self._current_page = page
            self.PAGE_SIZE = page_size
            self._total = total

            total_pages = max(1, (total + page_size - 1) // page_size)
            self.page_label.configure(text=f"Página {page+1} / {total_pages}")
            # habilitar/deshabilitar botones
            if page <= 0:
                self.prev_btn.configure(state="disabled")
            else:
                self.prev_btn.configure(state="normal")
            if page >= total_pages - 1:
                self.next_btn.configure(state="disabled")
            else:
                self.next_btn.configure(state="normal")

            # limpiar selección previa
            try:
                if self._selected_widget is not None:
                    self._selected_widget.configure(fg_color="transparent")
            except Exception:
                pass
            self._selected_widget = None
            self._selected_id = None
            self.btn_borrar.configure(state="disabled")

            self.build_rows()
        except Exception:
            pass

    def _change_page(self, delta):
        """Cambia la página relativa (delta = -1 o +1) y pide datos al controller."""
        new_page = max(0, self._current_page + delta)
        # limitar según total
        try:
            total_pages = max(1, (self._total + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
            if new_page >= total_pages:
                new_page = total_pages - 1
        except Exception:
            pass

        if self.controller and hasattr(self.controller, "search_products"):
            try:
                self.controller.search_products(query=self._last_query, page=new_page, page_size=self.PAGE_SIZE, async_search=True)
            except Exception:
                pass

    def _on_delete(self):
        """Handler para el botón Borrar: confirma y delega al controller, luego actualiza la vista localmente."""
        if self._selected_id is None:
            messagebox.showinfo("Borrar producto", "Seleccione un producto primero.")
            return

        confirmar = messagebox.askyesno("Confirmar borrado", "¿Eliminar el producto seleccionado?")
        if not confirmar:
            return

        # delegar al controller si existe
        if self.controller and hasattr(self.controller, "delete_product"):
            try:
                self.controller.delete_product(self._selected_id)
            except Exception as e:
                messagebox.showerror("Error al borrar", f"Ocurrió un error al borrar: {e}")

        # también actualizar la lista local y la lista completa para mantener consistencia
        try:
            self._productos = [p for p in self._productos if p.get("id") != self._selected_id]
        except Exception:
            pass
        try:
            self._all_products = [p for p in self._all_products if p.get("id") != self._selected_id]
        except Exception:
            pass

        # limpiar selección y botones
        try:
            if self._selected_widget is not None:
                self._selected_widget.configure(fg_color="transparent")
        except Exception:
            pass
        self._selected_widget = None
        self._selected_id = None
        self.btn_borrar.configure(state="disabled")

        # reconstruir filas
        self.build_rows()
    

