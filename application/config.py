
class Config(object):
    ENVIRONMENT = 'development' # production, staging, development
    DEVELOPMENT_MODE = True
    RELEASE_VERSION = '1.0.1'
    SQLALCHEMY_DATABASE_URI = 'postgresql://schedule_exuser:123456@localhost:5432/schedule'

    # DEMAIN = 'https://upstart.vn'
    # HOST = 'https://upstart.vn/furama'
    # STATIC_URL = 'static'

    REQUEST_TIMEOUT = 86400
    RESPONSE_TIMEOUT = 86400
    AUTH_LOGIN_ENDPOINT = 'login'
    AUTH_PASSWORD_HASH = 'sha512_crypt'
    AUTH_PASSWORD_SALT = 'add_salt'
    SECRET_KEY = 'acndef'
    SESSION_COOKIE_SALT = 'salt_key'
    SESSION_COOKIE_DOMAIN = '.upstart.vn'

    SESSION_REDIS_ADDR = 'localhost'
    SESSION_REDIS_PORT = 6379
    SESSION_REDIS_DB = 5
    SESSION_REDIS_URI = "redis://" + \
        str(SESSION_REDIS_ADDR)+":" + \
        str(SESSION_REDIS_PORT)+"/"+str(SESSION_REDIS_DB)

    BARCODE_TYPE = 'code128'
    # BARCODE_STORAGE_PATH = 'static/images/barcodes/'

    UPSTART_COMMON_SERVICES = 'https://upstart.vn/services'
    UPSTART_INSTANTGAME_URL = 'https://upstart.vn/instantgame'
    UPSTART_CRM_URL = 'https://upstart.vn/crm'
    UPSTART_WIFI_URL = 'https://upstart.vn/wifi'
    UPSTART_CHATBOT_URL = 'https://upstart.vn/chatbot'
    UPSTART_FIREBASE_KEY = '07jZNydE4C9OXqC4IjNcMyBk7hCpivz9qIW37ZvZsuBdK35gdIhN4IY1NqfTJCSZ'
    UPSTART_WEB_SOCKET_KEY = '07jZNydE4C9OXqC4IjNcMyBk7hCpivz9qIW37ZvZsuBdK35gdIhN4IY1NqfTJCSZ'

    ALLOWED_APPS = ['upstart_manager', 'upstart_crm', 'upstart_pos', 'upgo_furama']
