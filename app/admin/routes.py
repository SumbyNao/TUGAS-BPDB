from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.models import Pendaftar, Berkas
from app import db

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)  # Add this to preserve function metadata
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Akses ditolak. Anda bukan admin.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = {
        'total_pendaftar': Pendaftar.query.count(),
        'menunggu_verifikasi': Pendaftar.query.filter_by(status='Menunggu').count(),
        'terverifikasi': Pendaftar.query.filter_by(status='Diverifikasi').count()
    }
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/verifikasi/<int:pendaftar_id>')
@admin_required
def verifikasi(pendaftar_id):
    pendaftar = Pendaftar.query.get_or_404(pendaftar_id)
    pendaftar.status = 'Diverifikasi'
    db.session.commit()
    flash(f"Pendaftar {pendaftar.nama_lengkap} berhasil diverifikasi.", 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/hapus/<int:pendaftar_id>')
@admin_required
def hapus(pendaftar_id):
    pendaftar = Pendaftar.query.get_or_404(pendaftar_id)
    berkas = Berkas.query.filter_by(pendaftar_id=pendaftar.id).first()
    if berkas:
        db.session.delete(berkas)
    db.session.delete(pendaftar)
    db.session.commit()
    flash(f"Pendaftar {pendaftar.nama_lengkap} berhasil dihapus.", 'warning')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/pendaftar')
@admin_required
def list_pendaftar():
    return render_template('admin/pendaftar.html')

@admin_bp.route('/berkas')
@admin_required
def list_berkas():
    return render_template('admin/berkas.html')

@admin_bp.route('/pembayaran')
@admin_required
def list_pembayaran():
    return render_template('admin/pembayaran.html')
