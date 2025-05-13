from flask import render_template
from app.main import main_bp
from flask_login import current_user

@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('main/index.html')

@main_bp.route('/alur-pendaftaran')
def alur_pendaftaran():
    return render_template('main/alur_pendaftaran.html')

@main_bp.route('/pengumuman')
def pengumuman():
    pengumuman_list = []  # You can populate this from database later
    return render_template('main/pengumuman.html', pengumuman_list=pengumuman_list)