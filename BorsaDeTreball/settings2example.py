# global
# crear random SECRET_KEY
SECRET_KEY = 'o(#%baw0jmayi2szr^gww5d09#aalru258l7^tkn)g+=(w3nhr'
ALLOWED_HOSTS = ['*']
DEBUG = True

# set2 example
EMAIL_HOST = "Asignar el host por el cual se enviaran los mails"
EMAIL_PORT = "Asignar el puerto por el que se envia el mail"
EMAIL_FROM_NAME = "Borsa de Treball IETI (noreply)"
EMAIL_HOST_USER = "El correo electronico que enviara los mails"
EMAIL_HOST_PASSWORD = "Password correspondiente al email"
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

#OAuth
SOCIAL_AUTH_URL_NAMESPACE = ""
SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/"
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "Clave que recibimos de Google"
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "Clave secreta que recibimos de Google para usar este plugin"
# Microsoft no hi es en aquest plugin
# per crear Microsoft app:
# https://docs.microsoft.com/en-us/dynamics365/customer-engagement/portals/configure-oauth2-settings
#SOCIAL_AUTH_MICROSOFT_OAUTH2_KEY = "Clave que recibimos de Microsoft"
#SOCIAL_AUTH_MICROSOFT_OAUTH2_SECRET = "Clave secreta de Microsoft"

# DB
DB_TYPE = "postgre" # postgre, mysql
DB_HOST = "localhost"
DB_PORT = None # None = auto
DB_NAME = "borsApp"
DB_USER = "user001"
DB_PASS = "123456789"



