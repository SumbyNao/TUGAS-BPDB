from flask import render_template, redirect, url_for
from flask_login import current_user
from app.main import main_bp

@main_bp.route('/')
def index():
    if current_user.is_authenticated and current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    return render_template('main/index.html')