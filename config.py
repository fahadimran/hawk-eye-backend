"""Flask configuration"""
from os import environ, path
from datetime import timedelta
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY')
SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False
