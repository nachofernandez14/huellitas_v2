from tkinter import messagebox, simpledialog
from views.subcategorias_view import SubcategoriasView


class SubcategoriasController:
    def __init__(self, master, app_controller=None):
        # master is expected to be a frame or Toplevel where the view will be placed
        self.master = master
        self.app_controller = app_controller
        self.view = SubcategoriasView(master, controller=self)

        try:
            from models.categorias_model import CategoriasModel
            self.model = CategoriasModel()
        except Exception:
            self.model = None

        self._setup()
        self._load()

    def _setup(self):
        try:
            self.view.btn_agregar.configure(command=self.on_add)
            self.view.btn_borrar.configure(command=self.on_delete)
            self.view.btn_editar.configure(command=self.on_edit)
        except Exception:
            pass

    def _load(self):
        if self.model:
            try:
                subs = self.model.list_subcategories()
            except Exception:
                subs = []
        else:
            subs = []
        self.view.set_subcategories(subs)

    def on_add(self):
        """Agrega una fila vacía al sheet para crear una nueva subcategoría inline."""
        self.view.add_new_row()
    
    def create_subcategory(self, nombre):
        """Crea una nueva subcategoría con ID autoincremental."""
        if not self.model:
            messagebox.showerror('Error', 'No hay modelo configurado')
            return
        
        data = {
            'nombre': nombre
        }
        
        try:
            new_id = self.model.create_subcategory(data)
            if new_id:
                messagebox.showinfo('Éxito', f'Subcategoría "{nombre}" creada correctamente')
                self._load()
        except Exception as e:
            raise e
    
    def on_edit(self):
        """Habilita la edición inline de la subcategoría seleccionada."""
        # TODO: Implementar edición inline
        messagebox.showinfo("Información", "Función de edición en desarrollo")
    
    def on_cell_edit(self, row_idx, col_idx, sub_data, key, new_value):
        """Maneja la edición de una celda de subcategoría.
        
        Si es nueva (sin ID en BD) y se ingresa el NOMBRE, crea la subcategoría.
        Si es existente, actualiza el campo.
        """
        if not self.model:
            return
        
        sub_id = sub_data.get('id')
        
        # Caso 1: Nueva subcategoría (sin ID en BD) y se está ingresando el NOMBRE
        if sub_id is None and key == 'nombre' and new_value and str(new_value).strip():
            nombre = str(new_value).strip()
            
            # Crear subcategoría con solo el nombre (ID autoincremental)
            data = {
                'nombre': nombre
            }
            
            try:
                new_sub_id = self.model.create_subcategory(data)
                if new_sub_id:
                    self.view.after(0, lambda: messagebox.showinfo('Éxito', f'Subcategoría "{nombre}" creada correctamente'))
                    self._load()
            except Exception as e:
                self.view.after(0, lambda: messagebox.showerror('Error', f'Error al crear subcategoría: {e}'))
                self._load()
        
        # Caso 2: Subcategoría existente, actualizar campo
        elif sub_id is not None:
            try:
                update_data = {key: new_value.strip() if new_value else ''}
                if hasattr(self.model, 'update_subcategory'):
                    self.model.update_subcategory(sub_id, update_data)
            except Exception as e:
                self.view.after(0, lambda: messagebox.showerror('Error', f'Error al actualizar: {e}'))
                self._load()

    def on_delete(self):
        if not hasattr(self.view, '_selected_id') or self.view._selected_id is None:
            messagebox.showinfo('Eliminar', 'Seleccione una subcategoría primero')
            return
        self.view.delete_selected()

    def create_subcategory_from_sheet(self, sub_data, row_idx):
        try:
            # Si falta id o nombre, pedir al usuario que complete lo necesario.
            if not sub_data.get('nombre'):
                # Sin nombre no podemos crear
                return

            if not sub_data.get('id'):
                # Preguntar por el id (entero) al usuario
                ask_id = simpledialog.askinteger("ID subcategoría", "Ingrese ID (entero) para la subcategoría:", parent=self.view)
                if ask_id is None:
                    # Usuario canceló
                    return
                sub_data['id'] = ask_id

            # Validar que el id no exista ya
            if self.model and hasattr(self.model, 'get_subcategory_by_id'):
                existing = self.model.get_subcategory_by_id(sub_data['id'])
                if existing:
                    messagebox.showerror('Error', f"Ya existe una subcategoría con id {sub_data['id']}")
                    return
            if self.model and hasattr(self.model, 'create_subcategory'):
                new_id = self.model.create_subcategory(sub_data)
                if new_id and row_idx is not None:
                    self.view._subcategorias[row_idx]['id'] = new_id
                self._load()
            else:
                self.view.set_subcategories(self.view._subcategorias)
        except Exception as e:
            messagebox.showerror('Error', f'Error al crear subcategoría: {e}')
            raise e

    def update_subcategory_from_sheet(self, sub_id, updated_data, row_idx=None):
        try:
            if sub_id is None:
                # creación delegada a create_subcategory_from_sheet
                return
            if self.model and hasattr(self.model, 'update_subcategory'):
                self.model.update_subcategory(sub_id, updated_data)
        except Exception as e:
            messagebox.showerror('Error', f'Error al actualizar subcategoría: {e}')
            raise e

    def delete_subcategory(self, sub_id):
        try:
            if self.model and hasattr(self.model, 'delete_subcategory'):
                self.model.delete_subcategory(sub_id)
                self._load()
            else:
                self.view._subcategorias = [s for s in self.view._subcategorias if s.get('id') != sub_id]
                self.view.set_subcategories(self.view._subcategorias)
        except Exception as e:
            messagebox.showerror('Error', f'Error al borrar subcategoría: {e}')
            raise e
