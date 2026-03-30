import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smartcampus-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///smartcampus.db')
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOGETHER_API_KEY = os.environ.get('TOGETHER_API_KEY', '0357f4e3014d4d9183adb943e8d0aa0fe146034c20a12e408bd6a0ee748d45fe')
    TOGETHER_API_URL = 'https://api.together.xyz/v1/chat/completions'
    TOGETHER_MODEL = 'meta-llama/Llama-4-Maverick-17B-128E-Instruct'
