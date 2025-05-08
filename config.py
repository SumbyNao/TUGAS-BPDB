import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

# Define UPLOAD_FOLDER at module level
UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-this'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = UPLOAD_FOLDER
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)

