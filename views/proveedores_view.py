import customtkinter as ctk
from tkinter import messagebox
import threading
from tksheet import Sheet


class ProveedoresView(ctk.CTkFrame):
    # Definir las columnas para la tabla de proveedores (con saldo)
    COLUMNS = [
        ("nombre", "Nombre"),
        ("telefono", "Teléfono"),
        ("saldo", "Saldo"),
    ]

    # Anchos por columna
    COLUMN_WIDTHS = {
        "nombre": 300,  # Ancho para el nombre
        "telefono": 150,  # Ancho para teléfono
        "saldo": 120,   # Ancho para saldo
    }
    
    # Peso relativo para expansión
    COLUMN_WEIGHTS = {
        "nombre": 3,  # La más importante
        "telefono": 2,
        "saldo": 2,   # Importante para mostrar montos
    }

    # Header background (verde claro) and text (negro)
    HEADER_BG_COLOR = "#bfecc0"
    HEADER_TEXT_COLOR = "#000000"

    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self.pack(fill="both", expand=True)
        
        # Guardar referencia al controller
        self.controller = controller

        # datos internos
        self._proveedores = []
        self._selected_proveedor = None
        self._editor_row = None

        # barra de herramientas
        toolbar = ctk.CTkFrame(self, height=40, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=(8, 0))

        # barra de búsqueda
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(search_frame, text="Buscar:").pack(side="left", padx=(0, 8))
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Nombre del proveedor...")
        self.search_entry.pack(side="left", padx=(0, 8))
        
        self.btn_search = ctk.CTkButton(search_frame, text="Buscar", width=80)
        self.btn_search.pack(side="left", padx=(0, 8))

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

        # Botón Ver Saldo - más separado y con color diferente
        self.btn_ver_saldo = ctk.CTkButton(toolbar, text="Ver Saldo", width=120, fg_color="#2196F3", hover_color="#1976D2", text_color="#ffffff")
        self.btn_ver_saldo.pack(side="left", padx=(20, 6))  # Más separación a la izquierda

        # botones de control de edición a la derecha
        self.btn_cancelar = ctk.CTkButton(toolbar, text="Cancelar", state="disabled", fg_color="#9e9e9e", hover_color="#7e7e7e", text_color="#ffffff")
        self.btn_cancelar.pack(side="right", padx=(10, 0))

        self.btn_guardar = ctk.CTkButton(toolbar, text="Guardar", state="disabled", fg_color="#2e7d32", hover_color="#27632a", text_color="#ffffff")
        self.btn_guardar.pack(side="right")

        # inicialmente deshabilitados borrar/ver saldo
        self.btn_borrar.configure(state="disabled")
        self.btn_ver_saldo.configure(state="disabled")
        self.btn_guardar.configure(state="disabled")
        self.btn_cancelar.configure(state="disabled")

        # Título
        titulo = ctk.CTkLabel(self, text="Proveedores", font=ctk.CTkFont(size=22, weight="bold"))
        titulo.pack(anchor="nw", pady=(2, 8), padx=10)

        # Crear el Sheet (tksheet) para la tabla de proveedores
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
        self.sheet.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Configurar anchos mínimos de columna
        column_config = {
            "nombre": 500,  # Muy ancha para nombres largos
            "telefono": 180,
            "saldo": 150,
        }
        
        for i, (key, _) in enumerate(self.COLUMNS):
            width = column_config.get(key, 150)
            self.sheet.column_width(column=i, width=width)
        
        # Hacer que el sheet se expanda para llenar el espacio
        self.sheet.set_options(
            auto_resize_columns=True,  # Auto ajustar al contenido
            column_width=150,
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

        # Controles de paginación
        pagination = ctk.CTkFrame(self, height=40, fg_color="transparent")
        pagination.pack(fill="x", padx=10, pady=(0, 8))

        self.btn_prev = ctk.CTkButton(pagination, text="< Anterior", width=100, state="disabled")
        self.btn_prev.pack(side="left")

        self.page_label = ctk.CTkLabel(pagination, text="Página 1")
        self.page_label.pack(side="left", padx=20)

        self.btn_next = ctk.CTkButton(pagination, text="Siguiente >", width=100, state="disabled")
        self.btn_next.pack(side="left")

        # Info de resultados
        self.info_label = ctk.CTkLabel(pagination, text="0 proveedores")
        self.info_label.pack(side="right")

    def build_rows(self):
        """Construye las filas de proveedores en la tabla."""
        # Limpiar datos previos del sheet
        self.sheet.set_sheet_data([[]])
        
        # Preparar los datos para tksheet
        data = []
        for p in self._proveedores:
            row = []
            for key, _ in self.COLUMNS:
                value = p.get(key, "")
                
                # Manejo especial de valores None o vacíos
                if value is None:
                    display_value = ""
                elif key == "saldo":
                    # Para saldo, mostrar como moneda
                    try:
                        display_value = f"${float(value):.2f}" if value is not None and str(value).strip() != "" else "$0.00"
                    except Exception:
                        display_value = str(value) if value is not None else "$0.00"
                else:
                    # Para texto normal
                    display_value = str(value) if value is not None else ""
                
                row.append(display_value)
            data.append(row)
        
        # Establecer los datos en el sheet
        if data:
            self.sheet.set_sheet_data(data)
            # Ajustar automáticamente el ancho de las columnas al contenido
            try:
                for col_idx in range(len(self.COLUMNS)):
                    self.sheet.align_columns(columns=[col_idx], align="w")
            except:
                pass
        else:
            self.sheet.set_sheet_data([[""] * len(self.COLUMNS)])
    
    def _on_sheet_select(self, event):
        """Maneja la selección de filas en el sheet."""
        selected = self.sheet.get_currently_selected()
        if selected and selected.row is not None:
            row_idx = selected.row
            if 0 <= row_idx < len(self._proveedores):
                proveedor_data = self._proveedores[row_idx]
                self._selected_proveedor = proveedor_data
                self._selected_row = None  # No usado con tksheet
                # habilitar botones borrar/ver saldo
                self.btn_borrar.configure(state="normal")
                self.btn_ver_saldo.configure(state="normal")
    
    def _on_cell_edit(self, event):
        """Maneja cuando se termina de editar una celda y guarda en la BD."""
        try:
            # event es un objeto EditCellEvent con row, column, value
            row_idx = event.row
            col_idx = event.column
            new_value = event.value
            
            if 0 <= row_idx < len(self._proveedores):
                # Obtener el proveedor de esta fila
                proveedor = self._proveedores[row_idx]
                proveedor_id = proveedor.get("id")
                
                # Obtener el key de la columna editada
                if col_idx < len(self.COLUMNS):
                    key, _ = self.COLUMNS[col_idx]
                    
                    # Construir dict con el valor actualizado
                    updated_data = dict(proveedor)  # Copiar todo el proveedor
                    
                    # Formatear el nuevo valor según el tipo
                    if key == "saldo":
                        try:
                            clean_value = str(new_value).replace("$", "").replace(",", "").strip()
                            updated_data[key] = float(clean_value) if clean_value else 0.0
                        except:
                            updated_data[key] = 0.0
                    else:
                        updated_data[key] = str(new_value) if new_value else ""
                    
                    # Llamar al controller para actualizar en BD
                    if self.controller and hasattr(self.controller, "update_proveedor_from_sheet"):
                        self.controller.update_proveedor_from_sheet(proveedor_id, updated_data)
                        # Actualizar el proveedor local
                        self._proveedores[row_idx].update(updated_data)
                    elif proveedor_id is None:
                        # Es un proveedor nuevo, llamar al controller para crear
                        if self.controller and hasattr(self.controller, "create_proveedor_from_sheet"):
                            self.controller.create_proveedor_from_sheet(updated_data, row_idx)
        except Exception as e:
            print(f"Error al guardar edición: {e}")
            import traceback
            traceback.print_exc()
    
    def add_new_row(self):
        """Agrega una fila vacía al inicio del sheet para crear un nuevo proveedor."""
        # Insertar fila vacía en la primera posición
        self.sheet.insert_row(values=[""] * len(self.COLUMNS), idx=0)
        # Agregar un proveedor temporal a la lista interna
        new_proveedor = {key: "" for key, _ in self.COLUMNS}
        new_proveedor["id"] = None  # Sin ID todavía
        new_proveedor["saldo"] = 0.0
        self._proveedores.insert(0, new_proveedor)
        # Seleccionar la primera celda para empezar a editar
        self.sheet.see(0, 0)
        self.sheet.select_cell(0, 0)  # Seleccionar columna "nombre"

    # Note: Adding/editing functionality should be handled via dialogs, not inline editing

    def get_editor_data(self):
        """Obtiene los datos del editor actual."""
        if not hasattr(self, '_editor_entries') or not self._editor_entries:
            return None

        data = {}
        for key, entry in self._editor_entries.items():
            data[key] = entry.get().strip()
        return data

    def set_proveedores(self, proveedores_list):
        """Actualiza la lista de proveedores y reconstruye la tabla."""
        self._proveedores = proveedores_list or []
        self.build_rows()

    def update_pagination_info(self, current_page, total_pages, total_items):
        """Actualiza la información de paginación."""
        self.page_label.configure(text=f"Página {current_page} de {total_pages}")
        self.info_label.configure(text=f"{total_items} proveedores")
        
        self.btn_prev.configure(state="normal" if current_page > 1 else "disabled")
        self.btn_next.configure(state="normal" if current_page < total_pages else "disabled")

    def get_search_query(self):
        """Obtiene el texto de búsqueda."""
        return self.search_entry.get().strip()

    def clear_search(self):
        """Limpia el campo de búsqueda."""
        self.search_entry.delete(0, 'end')

    def show_message(self, title, message, type_="info"):
        """Muestra un mensaje al usuario."""
        if type_ == "error":
            messagebox.showerror(title, message)
        elif type_ == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)


class SaldoProveedorWindow(ctk.CTkToplevel):
    """Ventana para mostrar el saldo detallado de un proveedor."""
    
    def __init__(self, parent, proveedor_data):
        super().__init__(parent)
        
        self.proveedor_data = proveedor_data
        
        # Configuración de la ventana
        self.title(f"Saldo - {proveedor_data.get('nombre', 'Proveedor')}")
        self.geometry("1200x800")
        self.resizable(False, False)
        
        # Centrar la ventana
        self.transient(parent)
        self.grab_set()  # Hacer modal
        
        # Configurar el contenido
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz de usuario de la ventana."""
        
        # Título principal
        titulo_frame = ctk.CTkFrame(self, fg_color="transparent")
        titulo_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        titulo = ctk.CTkLabel(
            titulo_frame, 
            text="Información de Saldo y Movimientos", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titulo.pack()
        
        # Frame superior para información del proveedor
        info_superior_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_superior_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Información del proveedor en layout horizontal
        proveedor_info_frame = ctk.CTkFrame(info_superior_frame)
        proveedor_info_frame.pack(fill="x", pady=10)
        
        # Frame izquierdo para datos del proveedor
        left_info = ctk.CTkFrame(proveedor_info_frame, fg_color="transparent")
        left_info.pack(side="left", fill="both", expand=True, padx=20, pady=15)
        
        # Nombre del proveedor
        ctk.CTkLabel(
            left_info, 
            text=f"Proveedor: {self.proveedor_data.get('nombre', 'N/A')}", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w")
        
        # Teléfono
        ctk.CTkLabel(
            left_info, 
            text=f"Teléfono: {self.proveedor_data.get('telefono', 'N/A')}", 
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=(5, 0))
        
        # Frame derecho para saldo actual
        right_info = ctk.CTkFrame(proveedor_info_frame, fg_color="#e8f5e8", corner_radius=10)
        right_info.pack(side="right", padx=20, pady=15)
        
        ctk.CTkLabel(
            right_info, 
            text="Saldo Actual:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2e7d32"
        ).pack(pady=(15, 5))
        
        # Formatear el saldo
        saldo_value = self.proveedor_data.get('saldo', 0)
        try:
            saldo_formatted = f"${float(saldo_value):,.2f}"
        except:
            saldo_formatted = "$0.00"
            
        ctk.CTkLabel(
            right_info, 
            text=saldo_formatted, 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1b5e20"
        ).pack(pady=(0, 15))
        
        # Frame para la tabla de movimientos
        tabla_frame = ctk.CTkFrame(self)
        tabla_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Título de la tabla
        tabla_titulo = ctk.CTkLabel(
            tabla_frame, 
            text="Historial de Movimientos", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        tabla_titulo.pack(pady=(15, 10))
        
        # Definir columnas y sus anchos
        self.columnas = [
            ("fecha", "Fecha", 120),
            ("movimiento", "Tipo", 100),
            ("monto_movimiento", "Monto Mov.", 120),
            ("monto_boleta", "Monto Boleta", 120),
            ("saldo", "Saldo", 120)
        ]
        
        # Crear el Sheet para los movimientos
        self.movimientos_sheet = Sheet(
            tabla_frame,
            headers=[header for _, header, _ in self.columnas],
            height=300,
            width=600
        )
        self.movimientos_sheet.enable_bindings()
        self.movimientos_sheet.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Configurar anchos de columna
        for i, (_, _, width) in enumerate(self.columnas):
            self.movimientos_sheet.column_width(column=i, width=width)
        
        # Configurar colores y estilos
        self.movimientos_sheet.set_options(
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
        
        # Cargar datos de movimientos
        self._cargar_movimientos()
        
        # Botón cerrar
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        btn_cerrar = ctk.CTkButton(
            btn_frame,
            text="Cerrar",
            width=100,
            fg_color="#9e9e9e",
            hover_color="#7e7e7e",
            command=self.destroy
        )
        btn_cerrar.pack(side="right")
        
    def _cargar_movimientos(self):
        """Carga los movimientos de cuenta del proveedor en la tabla."""
        # Importar el modelo de cuentas
        from models.cuentas_model import CuentasModel
        
        cuentas_model = CuentasModel()
        proveedor_id = self.proveedor_data.get('id')
        
        if not proveedor_id:
            # Si no hay ID, mostrar mensaje en el sheet
            self.movimientos_sheet.set_sheet_data([["No se pudo obtener el ID del proveedor", "", "", "", ""]])
            return
        
        # Obtener movimientos
        movimientos = cuentas_model.get_movimientos_by_proveedor(proveedor_id)
        
        if not movimientos:
            # Si no hay movimientos, mostrar mensaje
            self.movimientos_sheet.set_sheet_data([["No hay movimientos registrados", "", "", "", ""]])
            return
        
        # Preparar datos para el sheet
        data = []
        for movimiento in movimientos:
            row = []
            for key, _, _ in self.columnas:
                value = movimiento.get(key, "")
                
                # Formatear valores según el tipo
                if key in ["monto_movimiento", "monto_boleta", "saldo"]:
                    try:
                        display_value = f"${float(value):,.2f}" if value is not None else "$0.00"
                    except:
                        display_value = "$0.00"
                elif key == "movimiento":
                    # Interpretar el tipo de movimiento
                    tipo_movimiento = {
                        1: "Compra",
                        2: "Pago",
                        3: "Ajuste",
                        4: "Devolución"
                    }.get(int(value) if value else 0, "Desconocido")
                    display_value = tipo_movimiento
                elif key == "fecha":
                    display_value = str(value) if value else ""
                else:
                    display_value = str(value) if value is not None else ""
                
                row.append(display_value)
            data.append(row)
        
        # Establecer los datos en el sheet
        self.movimientos_sheet.set_sheet_data(data)