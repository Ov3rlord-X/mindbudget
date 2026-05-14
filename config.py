import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mindbudget-secret-key-2026'
    
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///mindbudget.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False