class Config:
    SECRET_KEY = 'your_secret_key'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True

class DevelopmentConfig(Config):
    DEBUG = True
    CORS_ORIGIN = 'http://127.0.0.1:3000'

class DatabaseConfig:
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PASSWORD = "Theerthan"
    DB_NAME = "minor_project"
