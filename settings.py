import os

SECRET_KEY = "SECRET"
JWT_LIFETIME = int(os.environ.get('JWT_LIFETIME', 3600))
DATABASE_USER = os.environ.get('DATABASE_USER', 'user')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', 'password')
DATABASE_HOST = os.environ.get('DATABASE_HOST', '127.0.0.1')
DATABASE_PORT = int(os.environ.get('DATABASE_PORT', 5432))
DATABASE_DB = os.environ.get('DATABASE_DB', 'db')
DATABASE_URL = f'postgres://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}'