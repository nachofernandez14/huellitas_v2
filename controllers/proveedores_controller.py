import threading
import customtkinter as ctk
from tkinter import messagebox
from models.proveedores_model import ProveedoresModel
from views.proveedores_view import ProveedoresView


class ProveedoresController:
    def __init__(self, parent_frame):
        self.model = ProveedoresModel()
        self.view = ProveedoresView(parent_frame, controller=self)
        
        # Estado de paginación
        self.current_page = 1
        self.items_per_page = 50
        self.total_items = 0
        
        # Configurar comandos de botones
        self._setup_button_commands()
        
        # Cargar datos iniciales
        self.search_proveedores()

    def _setup_button_commands(self):
        """Configura los comandos de los botones de la vista."""
        self.view.btn_agregar.configure(command=self.on_add_proveedor)
        self.view.btn_borrar.configure(command=self.on_delete_proveedor)
        self.view.btn_ver_saldo.configure(command=self.on_ver_saldo)
        self.view.btn_guardar.configure(command=self.on_save_proveedor)
        self.view.btn_cancelar.configure(command=self.on_cancel_edit)
        self.view.btn_search.configure(command=self.on_search)
        self.view.btn_prev.configure(command=self.on_prev_page)
        self.view.btn_next.configure(command=self.on_next_page)
        
        # Enter en búsqueda
        self.view.search_entry.bind("<Return>", lambda e: self.on_search())

    def on_add_proveedor(self):
        """Inicia el modo de agregar proveedor."""
        self.view.add_new_row()

    def on_edit_proveedor(self):
        """El proveedor se edita directamente en el sheet haciendo doble clic en la celda."""
        messagebox.showinfo("Edición", "Haga doble clic en una celda para editarla directamente.")

    def on_delete_proveedor(self):
        """Borra el proveedor seleccionado."""
        if not hasattr(self.view, '_selected_proveedor') or not self.view._selected_proveedor:
            self.view.show_message("Error", "Seleccione un proveedor para borrar", "error")
            return

        proveedor = self.view._selected_proveedor
        nombre = proveedor.get("nombre", "")
        
        # confirmación
        result = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el proveedor '{nombre}'?\n\nEsta acción no se puede deshacer."
        )
        
        if result:
            # borrar en BD en hilo separado
            def delete_thread():
                try:
                    success = self.model.delete_proveedor(proveedor.get("id"))
                    if success:
                        # actualizar vista en hilo principal
                        self.view.after(0, lambda: self._on_delete_success())
                    else:
                        self.view.after(0, lambda: self.view.show_message("Error", "No se pudo eliminar el proveedor", "error"))
                except Exception as e:
                    self.view.after(0, lambda: self.view.show_message("Error", f"Error al eliminar: {str(e)}", "error"))

            threading.Thread(target=delete_thread, daemon=True).start()

    def _on_delete_success(self):
        """Callback cuando se elimina exitosamente."""
        self.view.show_message("Éxito", "Proveedor eliminado correctamente")
        # recargar datos
        self.search_proveedores()

    def on_ver_saldo(self):
        """Abre la ventana de saldo del proveedor seleccionado."""
        if not hasattr(self.view, '_selected_proveedor') or not self.view._selected_proveedor:
            self.view.show_message("Error", "Seleccione un proveedor para ver su saldo", "error")
            return

        proveedor = self.view._selected_proveedor
        
        # Asegurar que el proveedor tenga su ID
        if not proveedor.get('id'):
            self.view.show_message("Error", "No se pudo obtener la información del proveedor", "error")
            return
        
        # Importar la clase de ventana de saldo
        from views.proveedores_view import SaldoProveedorWindow
        
        # Crear y mostrar la ventana de saldo
        saldo_window = SaldoProveedorWindow(self.view, proveedor)
        
        # Centrar la ventana respecto a la ventana principal
        saldo_window.update_idletasks()
        x = self.view.winfo_rootx() + (self.view.winfo_width() // 2) - (saldo_window.winfo_width() // 2)
        y = self.view.winfo_rooty() + (self.view.winfo_height() // 2) - (saldo_window.winfo_height() // 2)
        saldo_window.geometry(f"+{x}+{y}")

    def on_save_proveedor(self):
        """Guarda el proveedor (nuevo o editado)."""
        data = self.view.get_editor_data()
        if not data:
            return

        # validación básica
        if not data.get("nombre", "").strip():
            self.view.show_message("Error", "El nombre del proveedor es requerido", "error")
            return

        # determinar si es edición o creación
        is_editing = hasattr(self.view, '_editing_proveedor_id')
        
        def save_thread():
            try:
                if is_editing:
                    # actualizar
                    proveedor_id = self.view._editing_proveedor_id
                    success = self.model.update_proveedor(proveedor_id, data)
                    message = "Proveedor actualizado correctamente" if success else "No se pudo actualizar el proveedor"
                else:
                    # crear nuevo
                    proveedor_id = self.model.create_proveedor(data)
                    success = proveedor_id is not None
                    message = "Proveedor creado correctamente" if success else "No se pudo crear el proveedor"
                
                # actualizar vista en hilo principal
                if success:
                    self.view.after(0, lambda: self._on_save_success(message))
                else:
                    self.view.after(0, lambda: self.view.show_message("Error", message, "error"))
                    
            except Exception as e:
                self.view.after(0, lambda: self.view.show_message("Error", f"Error al guardar: {str(e)}", "error"))

        threading.Thread(target=save_thread, daemon=True).start()

    def _on_save_success(self, message):
        """Callback cuando se guarda exitosamente."""
        self.view.show_message("Éxito", message)
        self.on_cancel_edit()  # limpiar editor
        self.search_proveedores()  # recargar datos

    def on_cancel_edit(self):
        """Cancela la edición."""
        # si estaba editando, restaurar fila oculta
        if hasattr(self.view, '_hidden_row') and self.view._hidden_row:
            self.view._hidden_row.pack(fill="x", pady=2)
            delattr(self.view, '_hidden_row')
        
        # limpiar referencias de edición
        if hasattr(self.view, '_editing_proveedor_id'):
            delattr(self.view, '_editing_proveedor_id')
        
        # llamar al método de cancelar de la vista
        self.view._on_cancel()

    def on_search(self):
        """Realiza búsqueda de proveedores."""
        self.current_page = 1  # resetear a primera página
        self.search_proveedores()

    def on_prev_page(self):
        """Ir a página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            self.search_proveedores()

    def on_next_page(self):
        """Ir a página siguiente."""
        total_pages = max(1, (self.total_items + self.items_per_page - 1) // self.items_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.search_proveedores()

    def search_proveedores(self):
        """Busca proveedores con paginación en hilo separado."""
        query = self.view.get_search_query()
        offset = (self.current_page - 1) * self.items_per_page
        
        def search_thread():
            try:
                proveedores, total = self.model.search_proveedores(
                    query if query else None,
                    limit=self.items_per_page,
                    offset=offset
                )
                
                # actualizar vista en hilo principal
                self.view.after(0, lambda: self._update_search_results(proveedores, total))
                
            except Exception as e:
                self.view.after(0, lambda: self.view.show_message("Error", f"Error en búsqueda: {str(e)}", "error"))

        threading.Thread(target=search_thread, daemon=True).start()

    def _update_search_results(self, proveedores, total):
        """Actualiza los resultados de búsqueda en la vista."""
        self.total_items = total
        self.view.set_proveedores(proveedores)
        
        # actualizar info de paginación
        total_pages = max(1, (total + self.items_per_page - 1) // self.items_per_page)
        self.view.update_pagination_info(self.current_page, total_pages, total)
    
    def update_proveedor_from_sheet(self, proveedor_id, updated_data):
        """Actualiza un proveedor editado desde el sheet."""
        try:
            if proveedor_id is None:
                # Es un proveedor nuevo, crear en BD
                if not updated_data.get("nombre"):
                    messagebox.showwarning("Advertencia", "El nombre del proveedor es obligatorio.")
                    return
                
                # Agregar estado por defecto
                updated_data["estado"] = "activo"
                
                new_id = self.model.create_proveedor(updated_data)
                if new_id:
                    messagebox.showinfo("Éxito", "Proveedor creado correctamente.")
                    self.search_proveedores()
            else:
                # Actualizar proveedor existente
                self.model.update_proveedor(proveedor_id, updated_data)
                messagebox.showinfo("Éxito", "Proveedor actualizado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {e}")
            raise e
    
    def create_proveedor_from_sheet(self, proveedor_data, row_idx):
        """Crea un proveedor nuevo desde el sheet."""
        try:
            if not proveedor_data.get("nombre"):
                messagebox.showwarning("Advertencia", "El nombre del proveedor es obligatorio.")
                return
            
            # Agregar estado por defecto
            proveedor_data["estado"] = "activo"
            
            new_id = self.model.create_proveedor(proveedor_data)
            if new_id:
                # Actualizar el ID en la vista
                self.view._proveedores[row_idx]["id"] = new_id
                messagebox.showinfo("Éxito", "Proveedor creado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear proveedor: {e}")