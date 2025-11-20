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
        self.view.btn_editar.configure(command=self.on_edit_proveedor)
        self.view.btn_borrar.configure(command=self.on_delete_proveedor)
        self.view.btn_ver_saldo.configure(command=self.on_ver_saldo)
        self.view.btn_search.configure(command=self.on_search)
        
        # Enter en búsqueda
        self.view.search_entry.bind("<Return>", lambda e: self.on_search())

    def on_add_proveedor(self):
        """Inicia el modo de agregar proveedor."""
        self.view.add_new_row()
    
    def create_proveedor(self, nombre, telefono, saldo):
        """Crea un nuevo proveedor en la base de datos."""
        try:
            proveedor_data = {
                "nombre": nombre,
                "telefono": telefono,
                "saldo": saldo
            }
            success = self.model.add_proveedor(proveedor_data)
            if success:
                messagebox.showinfo("Éxito", f"Proveedor '{nombre}' creado correctamente")
                self.search_proveedores()
            else:
                messagebox.showerror("Error", "No se pudo crear el proveedor")
        except Exception as e:
            raise e

    def on_edit_proveedor(self):
        """Habilita la edición inline del proveedor seleccionado."""
        # TODO: Implementar edición inline
        messagebox.showinfo("Información", "Función de edición en desarrollo")

    def on_delete_proveedor(self):
        """Borra el proveedor seleccionado."""
        self.view.delete_selected()

    def delete_proveedor(self, nombre):
        """Elimina un proveedor de la base de datos."""
        try:
            # Buscar el proveedor por nombre
            proveedores = self.model.search_proveedores(nombre)
            proveedor = None
            for p in proveedores:
                if p.get("nombre") == nombre:
                    proveedor = p
                    break
            
            if not proveedor:
                messagebox.showerror("Error", "No se encontró el proveedor")
                return
            
            # borrar en BD
            success = self.model.delete_proveedor(proveedor.get("id"))
            if success:
                messagebox.showinfo("Éxito", "Proveedor eliminado correctamente")
                self.search_proveedores()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el proveedor")
        except Exception as e:
            raise e

    def _on_delete_success(self):
        """Callback cuando se elimina exitosamente."""
        self.view.show_message("Éxito", "Proveedor eliminado correctamente")
        # recargar datos
        self.search_proveedores()

    def on_ver_saldo(self):
        """Abre la ventana de gestión de saldo del proveedor seleccionado."""
        if not hasattr(self.view, '_selected_proveedor') or not self.view._selected_proveedor:
            self.view.show_message("Error", "Seleccione un proveedor para ver su saldo", "error")
            return

        proveedor = self.view._selected_proveedor
        
        # Asegurar que el proveedor tenga su ID
        if not proveedor.get('id'):
            self.view.show_message("Error", "No se pudo obtener la información del proveedor", "error")
            return
        
        # Crear ventana toplevel para saldos
        ventana_saldos = ctk.CTkToplevel(self.view)
        ventana_saldos.title(f"Saldo - {proveedor.get('nombre', 'Proveedor')}")
        ventana_saldos.geometry("1100x700")
        ventana_saldos.minsize(900, 600)
        
        # Centrar ventana
        ventana_saldos.transient(self.view)
        ventana_saldos.grab_set()
        
        # Crear controller de saldos dentro de la ventana
        from controllers.saldos_proveedores_controller import SaldosProveedoresController
        SaldosProveedoresController(ventana_saldos, proveedor, app_controller=None)

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