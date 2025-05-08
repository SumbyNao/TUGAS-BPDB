from flask import Flask, render_template 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Silakan login terlebih dahulu.'
login_manager.login_message_category = 'warning'
csrf = CSRFProtect()
migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        # Import blueprints
        from app.auth import auth_bp
        from app.main import main_bp
        from app.ppdb import ppdb_bp
        from app.admin import admin_bp

        # Register blueprints
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(ppdb_bp, url_prefix='/ppdb')
        app.register_blueprint(main_bp)

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app
