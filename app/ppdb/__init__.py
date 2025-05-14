from flask import Blueprint

ppdb_bp = Blueprint('ppdb', __name__)

from app.ppdb import routes