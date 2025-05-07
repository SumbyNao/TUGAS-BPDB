from flask import Blueprint

ppdb_bp = Blueprint('ppdb', __name__, url_prefix='/ppdb')

from . import routes
