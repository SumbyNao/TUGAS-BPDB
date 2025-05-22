from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Pengumuman, Jurusan
from app.main.forms import ContactForm
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Halaman utama"""
    if current_user.is_authenticated:
        return redirect(url_for('ppdb.dashboard'))
    return render_template('main/index.html')

@main_bp.route('/visi-misi')
def visi_misi():
    """Halaman visi misi sekolah"""
    return render_template('main/visi_misi.html')

@main_bp.route('/alur-pendaftaran')
def alur_pendaftaran():
    """Halaman alur pendaftaran"""
    return render_template('main/alur_pendaftaran.html')

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

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Halaman dashboard - hanya untuk user yang sudah login"""
    try:
        pengumuman_list = Pengumuman.query.filter(
            Pengumuman.is_published == True,
            Pengumuman.publish_date <= datetime.utcnow()
        ).order_by(
            Pengumuman.publish_date.desc()
        ).limit(5).all()
        
        return render_template('main/dashboard.html',
                             pengumuman_list=pengumuman_list)
    except Exception as e:
        current_app.logger.error(f"Error di dashboard: {str(e)}")
        flash('Terjadi kesalahan saat memuat dashboard.', 'danger')
        return redirect(url_for('main.index'))