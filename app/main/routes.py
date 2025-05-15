from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.models import Jurusan, Pengumuman

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Halaman utama"""
    pengumuman_list = Pengumuman.query.filter_by(is_published=True).order_by(Pengumuman.created_at.desc()).limit(3)
    return render_template('main/index.html', pengumuman_list=pengumuman_list)

@main_bp.route('/alur-pendaftaran')
def alur_pendaftaran():
    """Halaman alur pendaftaran"""
    return render_template('main/alur_pendaftaran.html')

@main_bp.route('/pengumuman')
def pengumuman():
    """Halaman daftar pengumuman"""
    pengumuman_list = Pengumuman.query.filter_by(is_published=True).order_by(Pengumuman.created_at.desc()).all()
    return render_template('main/pengumuman.html', pengumuman_list=pengumuman_list)

@main_bp.route('/pengumuman/<int:id>')
def detail_pengumuman(id):
    """Halaman detail pengumuman"""
    pengumuman = Pengumuman.query.get_or_404(id)
    return render_template('main/detail_pengumuman.html', pengumuman=pengumuman)

@main_bp.route('/info')
def info():
    """Halaman informasi program keahlian"""
    jurusan_list = Jurusan.query.all()
    return render_template('main/info.html', jurusan_list=jurusan_list)

@main_bp.route('/kontak')
def kontak():
    """Halaman kontak"""
    return render_template('main/kontak.html')