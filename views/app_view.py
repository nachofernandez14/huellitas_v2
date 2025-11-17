import customtkinter as ctk

class AppView(ctk.CTk):
    def __init__(self, controlador=None):
        super().__init__()
        self.controlador = controlador
        self.title("Sistema Omar Fernandez")
        self.geometry("1024x768")
        
        
        # Frame de navegación superior
        self.frame_navbar = ctk.CTkFrame(self, height=72, corner_radius=0, fg_color="#00fe67")
        self.frame_navbar.pack(side="top", fill="x") 
        self.frame_navbar.pack_propagate(False)    
        
        self.boton_productos = ctk.CTkButton(self.frame_navbar, text="Productos", fg_color="#00fe67", hover_color="#08863b", font=ctk.CTkFont(size=16), border_width=0, text_color="#006400")
        self.boton_productos.pack(side="left", fill="y")

        self.boton_categorias = ctk.CTkButton(self.frame_navbar, text="Categorias", fg_color="#00fe67", hover_color="#08863b", font=ctk.CTkFont(size=16), border_width=0, text_color="#006400")
        self.boton_categorias.pack(side="left", fill="y")
        self.boton_proveedores = ctk.CTkButton(self.frame_navbar, text="Proveedores", fg_color="#00fe67", hover_color="#08863b", font=ctk.CTkFont(size=16), border_width=0, text_color="#006400")
        self.boton_proveedores.pack(side="left", fill="y")
        self.boton_config = ctk.CTkButton(self.frame_navbar, text="Configuracion", fg_color="#00fe67", hover_color="#08863b", font=ctk.CTkFont(size=16), border_width=0, text_color="#006400")
        self.boton_config.pack(side="right", fill="y")
        
        # Frame principal para el contenido
        self.frame_contenido = ctk.CTkFrame(self, corner_radius=0)
        self.frame_contenido.pack(fill="both", expand=True)

       
    
    def cerrar_sesion(self):
        from controllers.login_controller import LoginController
        self.withdraw()
        LoginController(self)
