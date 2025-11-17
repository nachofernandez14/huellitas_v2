import customtkinter as ctk
from views.login_view import VentanaLogin
from controllers.login_controller import LoginController
from views.app_view import AppView
if __name__ == "__main__":
    app = AppView()
    app.withdraw()  # ocultamos la ventana principal
    LoginController(app) # iniciamos el controlador de login
    app.mainloop()