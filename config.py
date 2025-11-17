"""
Archivo de configuración para el sistema Huellitas v2.0
Centraliza todas las configuraciones de la aplicación
"""

# Información de la aplicación
APP_NAME = "Huellitas Sistema"
APP_VERSION = "2.0"
APP_TITLE = f"{APP_NAME} v{APP_VERSION}"
DEVELOPER = "Ignacio Fernández"

# Configuración de ventana
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
WINDOW_RESIZABLE = False

# Configuración de CustomTkinter
CTK_APPEARANCE_MODE = "light"  # "light", "dark", "system"
CTK_COLOR_THEME = "green"      # "blue", "green", "dark-blue"

# Colores del sistema
class AppColors:
    # Colores principales
    GRIS_OSCURO = '#EBEBEB'
    GRIS_CLARO = '#8A8A8A'
    VERDE_CLARO = '#02FA66'
    VERDE_OSCURO = '#058A3B'
    VERDE_HOVER = '#046928'
    
    # Colores de estado
    ROJO_ERROR = '#FF4444'
    VERDE_EXITO = '#28A745'
    AMARILLO_WARNING = '#FFC107'
    AZUL_INFO = '#17A2B8'
    
    # Colores de texto
    TEXTO_PRINCIPAL = '#2B2B2B'
    TEXTO_SECUNDARIO = '#6C757D'
    TEXTO_PLACEHOLDER = '#ADB5BD'

# Configuración de fuentes
class AppFonts:
    # Familias de fuentes
    PRIMARY_FONT = "Ebrima"
    SECONDARY_FONT = "Myanmar Text"
    MONOSPACE_FONT = "Consolas"
    
    # Tamaños de fuente
    SIZE_SMALL = 11
    SIZE_NORMAL = 14
    SIZE_LARGE = 16
    SIZE_TITLE = 20
    SIZE_HEADER = 24
    SIZE_HUGE = 32

# Configuración de base de datos
class DatabaseConfig:
    DB_NAME = "negocio.db"
    APP_DATA_FOLDER = "MiNegocio"
    CONNECTION_TIMEOUT = 30.0
    
    # Configuraciones de SQLite
    PRAGMA_SETTINGS = {
        'journal_mode': 'DELETE',
        'synchronous': 'NORMAL',
        'temp_store': 'MEMORY',
        'cache_size': 10000
    }

# Configuración de validaciones
class ValidationConfig:
    # Usuario
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50
    ALLOWED_USERNAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    
    # Contraseña
    MIN_PASSWORD_LENGTH = 4
    MAX_PASSWORD_LENGTH = 100

# Mensajes del sistema
class Messages:
    # Errores comunes
    EMPTY_FIELDS = "Por favor complete todos los campos"
    INVALID_CREDENTIALS = "Usuario o contraseña incorrectos"
    PASSWORDS_DONT_MATCH = "Las contraseñas no coinciden"
    USER_EXISTS = "El usuario ya existe"
    USER_CREATED = "Usuario creado exitosamente"
    
    # Errores de validación
    USERNAME_TOO_SHORT = f"El usuario debe tener al menos {ValidationConfig.MIN_USERNAME_LENGTH} caracteres"
    PASSWORD_TOO_SHORT = f"La contraseña debe tener al menos {ValidationConfig.MIN_PASSWORD_LENGTH} caracteres"
    INVALID_USERNAME_CHARS = "El usuario solo puede contener letras, números, _ y -"
    
    # Éxito
    LOGIN_SUCCESS = "¡Bienvenido {username}!\n\nSistema iniciado correctamente."
    
    # Sistema
    APP_STARTING = "🐾 Iniciando Huellitas Sistema v2.0..."
    MVC_ARCHITECTURE = "📁 Arquitectura: Model-View-Controller (MVC)"
    SYSTEM_READY = "✅ Sistema iniciado correctamente"
    SHOWING_LOGIN = "🔐 Mostrando ventana de login..."

# Configuración de desarrollo
class DevConfig:
    DEBUG_MODE = True
    SHOW_SQL_QUERIES = False
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL