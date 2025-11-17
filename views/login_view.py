import customtkinter as ctk
from PIL import Image
from tkinter import PhotoImage
class VentanaLogin(ctk.CTkToplevel):
    def __init__(self, master):
        #El super es para que herede de ctk.CTkToplevel
        super().__init__(master)
        self.title("Sistema Huellitas")
        self.grab_set()  # Hace que la ventana sea modal
        self.focus()
        
        #Centramos la ventana en el medio de la pantalla
        ancho = self.winfo_screenwidth()
        alto = self.winfo_screenheight()
        ancho_ventana = 800
        alto_ventana = 500
        x = (ancho // 2) - (ancho_ventana // 2)
        y = (alto // 2) - (alto_ventana // 2)
        self.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

        frame_izq = ctk.CTkFrame(self, width=400, height=500, corner_radius=0, fg_color="#00fe67")
        frame_derecha = ctk.CTkFrame(self, width=400, height=500, fg_color="#E4E4E4", corner_radius=0)
        frame_izq.pack(side="left", fill="both", expand=True)
        frame_izq.pack_propagate(False)
        frame_derecha.pack(side="right", fill="both", expand=True)
        frame_derecha.pack_propagate(False)

        # Logo
        logo = Image.open("assets/images/huellitasLogo.png")
        self.img_logo = ctk.CTkImage(dark_image=logo, size=(250,200))
        logo_letras = Image.open("assets/images/huellitas_titulo.png")
        self.img_logo_letras = ctk.CTkImage(dark_image=logo_letras, size=(200,100))
        person = Image.open("assets/images/persona.png")
        self.img_person = ctk.CTkImage(dark_image=person, size=(80,80))
        self.label_footer = ctk.CTkLabel(frame_izq, text="Desarrollado por Ignacio Fernandez © 2025", font=ctk.CTkFont(size=12), fg_color="transparent")
        self.label_logo = ctk.CTkLabel(frame_izq, text="", image=self.img_logo)
        self.label_logo_letras = ctk.CTkLabel(frame_izq, text="", image=self.img_logo_letras)
        self.label_person = ctk.CTkLabel(frame_derecha, text="", image=self.img_person)
        #Labels y entries de inicio de sesion
        # Entradas de login: texto negro, sin borde, fondo verde (coincide con diseño)
        self.entry_usuario = ctk.CTkEntry(
            frame_derecha,
            placeholder_text="Usuario",
            width=280,
            font=ctk.CTkFont(size=16),
            fg_color="#00fe67",
            text_color="#000000",
            border_width=0,
            placeholder_text_color="#555555",
        )
        self.entry_password = ctk.CTkEntry(
            frame_derecha,
            placeholder_text="Contraseña",
            show="*",
            width=280,
            font=ctk.CTkFont(size=16),
            fg_color="#00fe67",
            text_color="#000000",
            border_width=0,
            placeholder_text_color="#555555",
        )
        # Botones de login: usar color verde para destacarlos sobre el fondo gris
        # Botones de login: usar color azul consistente y texto blanco
        BLUE = "#0078D7"
        self.boton_ingresar = ctk.CTkButton(
            frame_derecha,
            text="Ingresar",
            width=200,
            font=ctk.CTkFont(size=14),
            fg_color=BLUE,
            text_color="#303030",
        )
        self.boton_crear_user = ctk.CTkButton(
            frame_derecha,
            text="Crear Usuario",
            width=200,
            command=self.mostrar_register,
            font=ctk.CTkFont(size=14),
            fg_color=BLUE,
            text_color="#303030",
        )

        
        #Labels y entries de registro de usuario
        self.label_registro = ctk.CTkLabel(frame_derecha, text="Ingrese los datos para crear su usuario", font=ctk.CTkFont(size=16, weight="bold"), text_color="black")
        # Entradas de registro: texto negro, sin borde, fondo igual al frame para integrar
        # Entradas de registro: fondo blanco y borde para tener contraste sobre el frame gris
        self.entry_nuevo_usuario = ctk.CTkEntry(
            frame_derecha,
            placeholder_text="Ingresa tu usuario",
            width=280,
            font=ctk.CTkFont(size=16),
            fg_color="#00fe67",
            text_color="#303030",
            border_width=1,
            border_color="#cccccc",
            corner_radius=6,
            placeholder_text_color="#666666",
        )
        self.entry_nueva_password = ctk.CTkEntry(
            frame_derecha,
            placeholder_text="Ingresa tu contraseña",
            show="*",
            width=280,
            font=ctk.CTkFont(size=14),
            fg_color="#00fe67",
            text_color="#303030",
            border_width=1,
            border_color="#cccccc",
            corner_radius=6,
            placeholder_text_color="#666666",
        )
        # Botones de registro: registrar en verde, volver en blanco con borde
        self.boton_registrar = ctk.CTkButton(
            frame_derecha,
            text="Registrar",
            width=200,
            font=ctk.CTkFont(size=14),
            fg_color=BLUE,
            text_color="#303030",
        )
        self.boton_volver = ctk.CTkButton(
            frame_derecha,
            text="Volver",
            width=200,
            command=self.mostrar_login,
            font=ctk.CTkFont(size=14),
            fg_color=BLUE,
            text_color="#303030",
        )
    
    def mostrar_login(self):
        self.boton_volver.pack_forget()
        self.label_registro.pack_forget()
        self.entry_nuevo_usuario.pack_forget()
        self.entry_nueva_password.pack_forget()
        self.boton_registrar.pack_forget()
        # Mostramos los elementos del frame izquierdo
        self.label_logo.pack(pady=(50,10))
        self.label_logo_letras.pack(pady=(0,100))
        self.label_footer.pack(side="bottom", pady=10)
        # Mostramos los elementos del frame derecho
        self.label_person.pack(pady=(60,20))
        self.entry_usuario.pack(pady=(10,10))
        self.entry_password.pack(pady=10)
        self.boton_ingresar.pack(pady=10)
        self.boton_crear_user.pack(pady=10)
        
    def mostrar_register(self):
        self.entry_usuario.pack_forget()
        self.entry_password.pack_forget()
        self.boton_ingresar.pack_forget()
        self.boton_crear_user.pack_forget()
        
        self.label_registro.pack(pady=14)
        self.entry_nuevo_usuario.pack(pady=10)
        self.entry_nueva_password.pack(pady=10)
        self.boton_registrar.pack(pady=10)
        self.boton_volver.pack(pady=10)
