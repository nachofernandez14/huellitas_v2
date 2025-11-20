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
		
		# Botón Aumentar productos
		try:
			self.view.btn_aumentar.configure(command=self.on_aumentar_productos)
		except Exception:
			pass
		
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

	def delete_product(self, product_id):
		"""Elimina un producto a través del modelo."""
		try:
			self.model.delete_product(product_id)
			return True
		except Exception as e:
			raise e
	
	def update_product_from_sheet(self, product_id, updated_data, row_idx=None):
		"""Actualiza un producto editado desde el sheet."""
		try:
			if product_id is None:
				# Es un producto nuevo, crear en BD solo si tiene nombre
				if not updated_data.get("nombre"):
					# Aún no tiene nombre, esperar a que lo complete
					return
				
				# Crear el producto en la BD
				new_id = self.model.create_product(updated_data)
				if new_id:
					# Actualizar el ID en la vista
					if row_idx is not None and hasattr(self.view, '_productos'):
						self.view._productos[row_idx]["id"] = new_id
					messagebox.showinfo("Éxito", "Producto creado correctamente.")
					# Refrescar para mostrar el nuevo producto con ID en la primera página
					self.search_products(query=self.view._last_query, page=0, page_size=50, async_search=True)
			else:
				# Actualizar producto existente
				self.model.update_product(product_id, updated_data)
				# No mostrar mensaje para cada edición individual
		except Exception as e:
			messagebox.showerror("Error", f"Error al guardar: {e}")
			raise e

	# === MÉTODOS DE SOPORTE ===

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

	def on_aumentar_productos(self):
		"""Abre la ventana de aumentar productos."""
		try:
			from views.aumentar_productos_view import AumentarProductosWindow
			# Crear ventana
			ventana = AumentarProductosWindow(self.view, controller=self)
			# Configurar comandos de los botones
			ventana.btn_buscar.configure(command=lambda: self._buscar_productos_aumentar(ventana))
			ventana.btn_cargar_todos.configure(command=lambda: self._cargar_todos_productos_aumentar(ventana))
			ventana.btn_aplicar.configure(command=lambda: self._aplicar_aumento_precios(ventana))
			ventana.btn_eliminar.configure(command=lambda: ventana.eliminar_producto_seleccionado())
		except Exception as e:
			messagebox.showerror("Error", f"No se pudo abrir la ventana: {e}")
	
	def _buscar_productos_aumentar(self, ventana):
		"""Busca productos por nombre y los carga en la ventana."""
		query = ventana.entry_buscar.get().strip()
		if not query:
			messagebox.showwarning("Advertencia", "Ingrese un texto para buscar")
			return
		
		try:
			# Buscar productos que contengan el texto en el nombre
			productos, _ = self.model.search_products(query=query, limit=1000, offset=0)
			if not productos:
				messagebox.showinfo("Sin resultados", f"No se encontraron productos con '{query}' en el nombre")
				return
			
			ventana.cargar_productos(productos)
			messagebox.showinfo("Éxito", f"Se cargaron {len(productos)} productos")
		except Exception as e:
			messagebox.showerror("Error", f"Error al buscar productos: {e}")
	
	def _cargar_todos_productos_aumentar(self, ventana):
		"""Carga todos los productos en la ventana."""
		confirmar = messagebox.askyesno(
			"Confirmar",
			"¿Desea cargar TODOS los productos?\nEsto puede tardar si hay muchos registros."
		)
		if not confirmar:
			return
		
		try:
			productos = self.model.get_all()
			if not productos:
				messagebox.showinfo("Sin datos", "No hay productos en la base de datos")
				return
			
			ventana.cargar_productos(productos)
			messagebox.showinfo("Éxito", f"Se cargaron {len(productos)} productos")
		except Exception as e:
			messagebox.showerror("Error", f"Error al cargar productos: {e}")
	
	def _aplicar_aumento_precios(self, ventana):
		"""Aplica el aumento de precios y actualiza la base de datos."""
		porcentaje = ventana.entry_porcentaje.get().strip()
		if not porcentaje:
			messagebox.showwarning("Advertencia", "Ingrese un porcentaje de aumento")
			return
		
		if not ventana.productos_cargados:
			messagebox.showwarning("Advertencia", "No hay productos cargados")
			return
		
		# Calcular nuevos precios
		ventana.calcular_precios_nuevos(porcentaje)
		
		# Confirmar aplicación
		confirmar = messagebox.askyesno(
			"Confirmar aumento",
			f"¿Confirma aplicar el aumento del {porcentaje}% a {len(ventana.productos_cargados)} productos?\n\nEsta acción actualizará los precios en la base de datos."
		)
		
		if not confirmar:
			return
		
		# Actualizar en BD
		try:
			productos_actualizados = ventana.obtener_productos_actualizados()
			exitosos = 0
			
			for prod_data in productos_actualizados:
				try:
					self.model.update_product(prod_data['id'], {'precio_venta': prod_data['precio_venta']})
					exitosos += 1
				except Exception as e:
					print(f"Error actualizando producto {prod_data['id']}: {e}")
			
			messagebox.showinfo("Éxito", f"Se actualizaron {exitosos} de {len(productos_actualizados)} productos correctamente")
			
			# Refrescar vista principal
			self._refresh_view()
			
			# Cerrar ventana
			ventana.destroy()
			
		except Exception as e:
			messagebox.showerror("Error", f"Error al aplicar aumento: {e}")



