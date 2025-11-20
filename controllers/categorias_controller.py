import threading
from tkinter import messagebox, simpledialog
from views.categorias_view import CategoriasView


class CategoriasController:
    """Controlador mínimo para CategoriasView.

    - Si existe `models.categorias_model.CategoriasModel` lo usa para persistencia.
    - Soporta crear/editar/eliminar desde el Sheet delegando al modelo cuando esté disponible.
    """

    def __init__(self, master, app_controller=None):
        self.master = master
        self.app_controller = app_controller
        self.view = CategoriasView(master, controller=self)

        # intentar cargar modelo opcional
        try:
            from models.categorias_model import CategoriasModel
            self.model = CategoriasModel()
        except Exception:
            self.model = None

        self._setup_button_commands()
        self._load_initial_data()

    def _setup_button_commands(self):
        try:
            self.view.btn_agregar.configure(command=self.on_add_category)
            self.view.btn_borrar.configure(command=self.on_delete_category)
            self.view.btn_editar.configure(command=self.on_edit_category)
            self.view.btn_search.configure(command=self.on_search)
            # botón para abrir gestión de subcategorías
            try:
                self.view.btn_subcategorias.configure(command=self.open_subcategories_window)
            except Exception:
                pass
            self.view.search_entry.bind("<Return>", lambda e: self.on_search())
        except Exception:
            pass

    def _load_initial_data(self):
        if self.model:
            try:
                categorias = self.model.list_categories()
            except Exception:
                categorias = []
        else:
            categorias = []
        self.view.set_categories(categorias)
    
    def create_category(self, nombre, parent_id, descripcion):
        """Crea una nueva categoría con ID autoincremntal."""
        if not self.model:
            messagebox.showerror('Error', 'No hay modelo configurado')
            return
        
        data = {
            'nombre': nombre,
            'parent_id': parent_id,
            'descripcion': descripcion,
            'estado': 'activo'
        }
        
        try:
            new_id = self.model.create_category(data)
            if new_id:
                messagebox.showinfo('Éxito', f'Categoría "{nombre}" creada correctamente')
                self._load_initial_data()
        except Exception as e:
            raise e
    
    def on_cell_edit(self, row_idx, col_idx, categoria_data, key, new_value):
        """Maneja la edición de una celda.
        
        Si es una nueva categoría (sin ID en BD) y se ingresa el NOMBRE,
        crea la categoría automáticamente.
        Si es una categoría existente, actualiza el campo.
        """
        if not self.model:
            return
        
        categoria_id = categoria_data.get('id')
        
        # Caso 1: Nueva categoría (sin ID en BD) y se está ingresando el NOMBRE
        if categoria_id is None and key == 'nombre' and new_value and new_value.strip():
            nombre = new_value.strip()
            
            # Crear categoría con solo el nombre (ID autoincremental)
            data = {
                'nombre': nombre,
                'parent_id': categoria_data.get('parent_id', '').strip() or None,
                'descripcion': categoria_data.get('descripcion', '').strip() or '',
                'estado': 'activo'
            }
            
            try:
                new_cat_id = self.model.create_category(data)
                if new_cat_id:
                    self.view.after(0, lambda: messagebox.showinfo('Éxito', f'Categoría "{nombre}" creada correctamente'))
                    self._load_initial_data()
            except Exception as e:
                self.view.after(0, lambda: messagebox.showerror('Error', f'Error al crear categoría: {e}'))
                self._load_initial_data()
        
        # Caso 2: Categoría existente, actualizar campo
        elif categoria_id is not None:
            try:
                # Actualizar solo el campo modificado
                update_data = {key: new_value.strip() if new_value else ''}
                self.model.update_category(categoria_id, update_data)
            except Exception as e:
                self.view.after(0, lambda: messagebox.showerror('Error', f'Error al actualizar: {e}'))
                self._load_initial_data()

    def on_add_category(self):
        """Agrega una fila vacía al sheet para crear una nueva categoría inline."""
        self.view.add_new_row()

    def on_edit_category(self):
        """Habilita la edición inline de la categoría seleccionada."""
        # TODO: Implementar edición inline
        messagebox.showinfo("Información", "Función de edición en desarrollo")

    def on_delete_category(self):
        # La vista ya confirma y delega a controller.delete_category
        self.view.delete_selected()

    def on_search(self):
        query = self.view.get_search_query()
        if not query:
            # recargar todos
            self._load_initial_data()
            return

        # Si existe modelo, delegar búsqueda, sino filtrar localmente
        if self.model and hasattr(self.model, 'search_categories'):
            try:
                rows = self.model.search_categories(query)
            except Exception:
                rows = []
        else:
            rows = [c for c in getattr(self.view, '_categorias', []) if query.lower() in str(c.get('nombre','')).lower()]
        self.view.set_categories(rows)

    # Métodos que la vista puede llamar
    def update_category_from_sheet(self, category_id, updated_data, row_idx=None):
        """Actualizar categoría existente o crear si `category_id` es None."""
        try:
            if category_id is None:
                # Crear solo si tiene nombre e ID
                if not updated_data.get('nombre') or not updated_data.get('id'):
                    # Si falta el ID, pedirlo
                    if updated_data.get('nombre') and not updated_data.get('id'):
                        cat_id = simpledialog.askstring("ID requerido", f"Ingrese ID para la categoría '{updated_data.get('nombre')}':", parent=self.view)
                        if not cat_id or not cat_id.strip():
                            return
                        updated_data['id'] = cat_id.strip()
                    else:
                        return
                
                # Validar que no exista
                if self.model and hasattr(self.model, 'get_by_id'):
                    existing = self.model.get_by_id(updated_data['id'])
                    if existing:
                        messagebox.showerror('Error', f'Ya existe una categoría con ID "{updated_data["id"]}"')
                        return
                
                if self.model and hasattr(self.model, 'create_category'):
                    new_id = self.model.create_category(updated_data)
                    if new_id and row_idx is not None:
                        self.view._categorias[row_idx]['id'] = new_id
                        messagebox.showinfo('Éxito', 'Categoría creada correctamente')
                    # recargar
                    self._load_initial_data()
                else:
                    # crear local temporario y recargar
                    if row_idx is not None:
                        self.view._categorias[row_idx]['id'] = None
                    self.view.set_categories(self.view._categorias)
            else:
                if self.model and hasattr(self.model, 'update_category'):
                    self.model.update_category(category_id, updated_data)
                # actualizar vista localmente ya hecho por la vista
        except Exception as e:
            messagebox.showerror('Error', f'Error al guardar categoría: {e}')
            raise e

    def create_category_from_sheet(self, category_data, row_idx):
        # Similar a create en update_category_from_sheet
        try:
            if not category_data.get('nombre'):
                return
            if self.model and hasattr(self.model, 'create_category'):
                new_id = self.model.create_category(category_data)
                if new_id and row_idx is not None:
                    self.view._categorias[row_idx]['id'] = new_id
                self._load_initial_data()
            else:
                # Simplemente refrescar vista
                self.view.set_categories(self.view._categorias)
        except Exception as e:
            messagebox.showerror('Error', f'Error al crear categoría: {e}')
            raise e

    def delete_category(self, category_id):
        try:
            if self.model and hasattr(self.model, 'delete_category'):
                self.model.delete_category(category_id)
                self._load_initial_data()
            else:
                # eliminar localmente
                self.view._categorias = [c for c in self.view._categorias if c.get('id') != category_id]
                self.view.set_categories(self.view._categorias)
        except Exception as e:
            messagebox.showerror('Error', f'Error al borrar categoría: {e}')
            raise e

    def open_subcategories_window(self):
        """Abre una ventana Toplevel con la vista de subcategorías."""
        try:
            import customtkinter as ctk
            top = ctk.CTkToplevel(self.view)
            top.title("Subcategorías")
            # Ventana más amplia por defecto y redimensionable
            top.geometry("900x600")
            top.minsize(700, 400)
            top.resizable(True, True)
            # crear el controlador de subcategorías dentro del toplevel
            from controllers.subcategorias_controller import SubcategoriasController
            SubcategoriasController(top, app_controller=self.app_controller)
            # centrar y mostrar modal
            top.transient(self.view)
            top.grab_set()
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo abrir ventana de subcategorías: {e}')
