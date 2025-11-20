import customtkinter as ctk
from views.app_view import AppView
from controllers.products_controller import ProductsController
from controllers.proveedores_controller import ProveedoresController
from controllers.categorias_controller import CategoriasController
from controllers.ventas_controller import VentasController


class App_controller:
    def __init__(self):
        # Crear la vista principal y enlazar los comandos de los botones
        self.vista = AppView(controlador=self)
        self.vista_actual = None

        # Enlazar botones del navbar a los métodos del controlador
        self.vista.boton_productos.configure(command=self.show_productos)
        self.vista.boton_categorias.configure(command=self.show_categorias)
        self.vista.boton_proveedores.configure(command=self.show_proveedores)
        self.vista.boton_ventas.configure(command=self.show_ventas)
        self.vista.boton_config.configure(command=self.show_configuracion)

    def clear_contenido(self):
        """Elimina todo el contenido actual del frame_contenido."""
        for child in self.vista.frame_contenido.winfo_children():
            child.destroy()

    def show_productos(self):
        self.clear_contenido()
        # Instanciar el ProductsController para montar la vista dentro del frame_contenido
        ProductsController(self.vista.frame_contenido, app_controller=self)
        self.vista_actual = "productos"

    def show_categorias(self):
        self.clear_contenido()
        # Montar el controlador de categorías
        self.categorias_controller = CategoriasController(self.vista.frame_contenido, app_controller=self)
        self.vista_actual = "categorias"

    def show_proveedores(self):
        self.clear_contenido()
        # Montar el controlador de proveedores
        self.proveedores_controller = ProveedoresController(self.vista.frame_contenido)
        self.vista_actual = "proveedores"
    
    def show_ventas(self):
        self.clear_contenido()
        # Montar el controlador de ventas
        self.ventas_controller = VentasController(self.vista.frame_contenido, app_controller=self)
        self.vista_actual = "ventas"
    
    def show_configuracion(self):
        self.clear_contenido()
        # Placeholder: en el futuro montar ConfigController
        self.vista_actual = "configuracion"

