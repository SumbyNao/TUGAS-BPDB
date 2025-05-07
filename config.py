import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "devsecret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///ppdb.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
