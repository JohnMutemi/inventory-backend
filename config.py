import os

class Config:
    """Base config class."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Set default if not provided
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///inventory.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)
