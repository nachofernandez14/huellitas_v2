from views.login_view import VentanaLogin
from models.login_model import UsuarioModel
from controllers.app_controller import App_controller
from tkinter import messagebox

class LoginController:
    def __init__(self, master):
        self.master = master
        # ocultar la ventana principal inmediatamente para que no se muestre detrás del login
        self.master.withdraw()
        self.vista = VentanaLogin(master)
        # hacer el Toplevel transitivo/modo modal con respecto a la ventana principal
        self.vista.transient(self.master)
        VentanaLogin.mostrar_login(self.vista)
        self.model = UsuarioModel()
        self.vista.boton_ingresar.configure(command=self.ingresar)
        self.vista.boton_registrar.configure(command=self.crear_usuario)
        self.model.crear_tabla()  # Asegura que la tabla de usuarios exista

    def ingresar(self):
        usuario = self.vista.entry_usuario.get()
        password = self.vista.entry_password.get()
        if self.model.verificar_credenciales(usuario, password):
           # Destruir ventana de login primero
            self.vista.destroy()
            # Crear y mostrar la aplicación principal con su controlador
            self.master.destroy()  # destruir la ventana vacía
            app_controller = App_controller()  # esto crea VentanaPrincipal con controlador
            app_controller.vista.after(1, lambda: app_controller.vista.state('zoomed'))
            app_controller.vista.mainloop()  # iniciar bucle de eventos
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def crear_usuario(self):
        new_username = self.vista.entry_nuevo_usuario.get()
        new_password = self.vista.entry_nueva_password.get()
        if self.model.crear_usuario(new_username, new_password):
            messagebox.showinfo("Éxito", "Usuario creado correctamente")
            VentanaLogin.mostrar_login(self.vista)
        else:
            messagebox.showerror("Error", "El usuario ya existe")
            VentanaLogin.mostrar_register(self.vista)