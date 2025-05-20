from flask import Blueprint, render_template, redirect, url_for, send_from_directory, current_app, flash
from flask_login import current_user
from app.models import Jurusan, Pengumuman
from app.main.forms import ContactForm
from datetime import datetime

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
    pengumuman_list = Pengumuman.query.filter_by(
        is_published=True
    ).order_by(
        Pengumuman.created_at.desc()
    ).all()
    return render_template('main/pengumuman.html', pengumuman_list=pengumuman_list)

@main_bp.route('/pengumuman/<int:id>')
def detail_pengumuman(id):
    """Halaman detail pengumuman"""
    pengumuman = Pengumuman.query.get_or_404(id)
    
    if not pengumuman.is_published:
        return redirect(url_for('main.pengumuman'))
        
    return render_template(
        'main/detail_pengumuman.html',
        pengumuman=pengumuman,
        current_time=datetime.utcnow()
    )

@main_bp.route('/uploads/<path:filename>')
def download_file(filename):
    """Handle download lampiran"""
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )

@main_bp.route('/info')
def info():
    """Halaman informasi program keahlian"""
    jurusan_list = Jurusan.query.all()
    return render_template('main/info.html', jurusan_list=jurusan_list)

@main_bp.route('/kontak', methods=['GET', 'POST'])
def kontak():
    """Halaman kontak"""
    form = ContactForm()
    if form.validate_on_submit():
        flash('Pesan Anda telah terkirim. Kami akan segera menghubungi Anda.', 'success')
        return redirect(url_for('main.kontak'))
    return render_template('main/kontak.html', form=form)