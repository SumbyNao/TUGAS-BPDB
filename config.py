import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

# Define upload folder path
UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = UPLOAD_FOLDER
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    
    # Add additional upload configurations
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

