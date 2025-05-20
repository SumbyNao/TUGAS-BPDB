from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_mail import Mail
from config import Config
from datetime import datetime
from werkzeug.utils import secure_filename
import os

# Inisialisasi ekstensi
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()

# Import model setelah inisialisasi db untuk menghindari circular import
from app.models import User

# Fungsi untuk memuat user login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inisialisasi ekstensi dengan aplikasi
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    # Registrasi blueprint
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.ppdb.routes import ppdb_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(ppdb_bp, url_prefix='/ppdb')

    # Set konfigurasi login manager setelah blueprint auth terdaftar
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu.'
    login_manager.login_message_category = 'info'

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def too_large(error):
        return render_template('errors/413.html'), 413

    # Konteks tambahan ke semua template
    @app.context_processor
    def utility_processor():
        return {
            'current_year': datetime.now().year
        }

    # Sebelum setiap request, perbarui waktu terakhir aktif user
    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()

    return app
