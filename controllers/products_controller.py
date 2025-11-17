from models.products_model import ProductsModel
from views.products_view import ProductsView
from tkinter import simpledialog, messagebox
import threading


class ProductsController:
	"""Controlador de productos: monta la vista dentro de un contenedor dado."""
	def __init__(self, master, app_controller=None):
		self.master = master
		self.app_controller = app_controller
		
		# Crear modelo y vista
		self.model = ProductsModel()
		self.view = ProductsView(master, controller=self)
		
		# Configurar comandos de los botones (Controller asigna comandos)
		self._setup_button_commands()
		
		# Cargar datos iniciales
		self._load_initial_data()

	def _setup_button_commands(self):
		"""Asigna los comandos a los botones de la vista."""
		# Botones principales
		self.view.btn_agregar.configure(command=self.on_add_product)
		self.view.btn_borrar.configure(command=self.on_delete_product)
		self.view.btn_guardar.configure(command=self.on_save_product)
		self.view.btn_cancelar.configure(command=self.on_cancel_edit)
		
		# Botones de búsqueda
		self.view.search_btn.configure(command=self.on_search)
		self.view.clear_btn.configure(command=self.on_clear_search)
		
		# Configurar eventos de búsqueda en tiempo real
		try:
			self.view.search_entry.bind("<Return>", lambda e: self.on_search())
			self.view.search_entry.bind("<KP_Enter>", lambda e: self.on_search())
			self.view.search_entry.bind("<KeyRelease>", lambda e: self._schedule_search())
		except Exception:
			pass

	def _load_initial_data(self):
		"""Carga los datos iniciales en la vista."""
		self.search_products(query=None, page=0, page_size=50, async_search=True)

	# === MÉTODOS DE COMANDOS (llamados por los botones) ===
	
	def on_add_product(self):
		"""Comando del botón Agregar - Agrega una fila nueva en el sheet."""
		self.view.add_new_row()
	
	def on_edit_product(self):
		"""Comando del botón Editar - Maneja la edición de producto."""
		if self.view._selected_id is None:
			messagebox.showinfo("Editar producto", "Seleccione un producto primero.")
			return
		
		# Habilitar modo edición en la vista
		self._enable_edit_mode()
	
	def on_delete_product(self):
		"""Comando del botón Borrar - Llama al modelo para eliminar."""
		if self.view._selected_id is None:
			messagebox.showinfo("Borrar producto", "Seleccione un producto primero.")
			return

		confirmar = messagebox.askyesno("Confirmar borrado", "¿Eliminar el producto seleccionado?")
		if not confirmar:
			return

		try:
			# Llamar al modelo para eliminar
			self.model.delete_product(self.view._selected_id)
			messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
			# Refrescar vista
			self._refresh_view()
		except Exception as e:
			messagebox.showerror("Error al borrar", f"Ocurrió un error al borrar: {e}")
	
	def on_save_product(self):
		"""Comando del botón Guardar - Guarda el producto editado o nuevo."""
		# Implementar según si es edición o nuevo producto
		pass
	
	def on_cancel_edit(self):
		"""Comando del botón Cancelar - Cancela la edición actual."""
		self._disable_edit_mode()
		if hasattr(self.view, '_editor_row') and self.view._editor_row is not None:
			self.view._cancel_new(self.view._editor_row)
	
	def on_search(self):
		"""Comando del botón Buscar - Busca productos."""
		try:
			query = self.view.search_entry.get().strip()
		except Exception:
			query = ""
		
		query = query if query != "" else None
		self.search_products(query=query, page=0, page_size=50, async_search=True)
	
	def on_clear_search(self):
		"""Comando del botón Limpiar - Limpia la búsqueda."""
		self.view.search_entry.delete(0, "end")
		self.search_products(query=None, page=0, page_size=50, async_search=True)

	# === MÉTODOS DE MODELO (interactúan con la base de datos) ===

	def add_product(self, product_data):
		"""Añade un producto a través del modelo."""
		try:
			product_id = self.model.add_product(product_data)
			messagebox.showinfo("Éxito", "Producto agregado correctamente.")
			self._refresh_view()
			return product_id
		except Exception as e:
			messagebox.showerror("Error al agregar", f"Ocurrió un error al agregar: {e}")
			return None

	def edit_product(self, product_id):
		"""Edita un producto existente."""
		# Este método puede ser llamado desde la vista
		self._enable_edit_mode()

	def delete_product(self, product_id):
		"""Elimina un producto a través del modelo."""
		try:
			self.model.delete_product(product_id)
			return True
		except Exception as e:
			raise e
	
	def update_product_from_sheet(self, product_id, updated_data):
		"""Actualiza un producto editado desde el sheet."""
		try:
			if product_id is None:
				# Es un producto nuevo, crear en BD
				if not updated_data.get("nombre"):
					messagebox.showwarning("Advertencia", "El nombre del producto es obligatorio.")
					return
				
				new_id = self.model.create_product(updated_data)
				if new_id:
					messagebox.showinfo("Éxito", "Producto creado correctamente.")
					self._refresh_view()
			else:
				# Actualizar producto existente
				self.model.update_product(product_id, updated_data)
				messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
		except Exception as e:
			messagebox.showerror("Error", f"Error al guardar: {e}")
			raise e

	# === MÉTODOS DE SOPORTE ===

	def _enable_edit_mode(self):
		"""Habilita el modo de edición."""
		self.view.btn_guardar.configure(state="normal")
		self.view.btn_cancelar.configure(state="normal")
		self.view.btn_agregar.configure(state="disabled")
		self.view.btn_editar.configure(state="disabled")
		self.view.btn_borrar.configure(state="disabled")

	def _disable_edit_mode(self):
		"""Deshabilita el modo de edición."""
		self.view.btn_guardar.configure(state="disabled")
		self.view.btn_cancelar.configure(state="disabled")
		self.view.btn_agregar.configure(state="normal")
		# Los botones borrar se habilitan según selección
		if self.view._selected_id is not None:
			self.view.btn_editar.configure(state="normal")
			self.view.btn_borrar.configure(state="normal")

	def _schedule_search(self, delay=300):
		"""Programa una búsqueda con retraso (debounce)."""
		# Cancelar búsqueda programada anterior
		if hasattr(self.view, '_search_after_id') and self.view._search_after_id:
			try:
				self.view.after_cancel(self.view._search_after_id)
			except Exception:
				pass
		
		# Programar nueva búsqueda
		try:
			self.view._search_after_id = self.view.after(delay, self.on_search)
		except Exception:
			pass


	def _refresh_view(self):
		"""Refrescar la vista pidiendo la misma página y consulta actuales."""
		if self.view:
			page = getattr(self.view, "_current_page", 0)
			page_size = getattr(self.view, "PAGE_SIZE", 50)
			query = getattr(self.view, "_last_query", None)
			self.search_products(query=query, page=page, page_size=page_size, async_search=True)

	def search_products(self, query=None, page=0, page_size=50, async_search=True):
		"""Busca productos paginados. Si async_search es True, ejecuta en hilo y actualiza la vista con after."""
		def worker():
			try:
				offset = page * page_size
				rows, total = self.model.search_products(query=query, limit=page_size, offset=offset)
				# enviar al hilo principal
				self.master.after(0, lambda: self._deliver_page(rows, page, page_size, total))
			except Exception as e:
				# En caso de error, entregar lista vacía
				self.master.after(0, lambda: self._deliver_page([], page, page_size, 0))

		if async_search:
			th = threading.Thread(target=worker, daemon=True)
			th.start()
		else:
			worker()

	def _deliver_page(self, rows, page, page_size, total):
		"""Entrega una página de resultados a la vista."""
		if self.view:
			self.view.set_page(rows, page, page_size, total)


