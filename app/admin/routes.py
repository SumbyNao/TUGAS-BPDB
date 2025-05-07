from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Pendaftar, Berkas
from app import db
from . import admin_bp

def is_admin():
    return current_user.is_authenticated and current_user.role == 'admin'

@admin_bp.before_request
@login_required
def check_admin():
    if not is_admin():
        flash('Hanya admin yang dapat mengakses halaman ini.', 'danger')
        return redirect(url_for('ppdb.status'))

@admin_bp.route('/dashboard')
def dashboard():
    semua_pendaftar = Pendaftar.query.all()
    return render_template('admin/dashboard.html', pendaftar_list=semua_pendaftar)

@admin_bp.route('/verifikasi/<int:pendaftar_id>')
def verifikasi(pendaftar_id):
    pendaftar = Pendaftar.query.get_or_404(pendaftar_id)
    pendaftar.status = 'Diverifikasi'
    db.session.commit()
    flash(f"Pendaftar {pendaftar.nama_lengkap} berhasil diverifikasi.", 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/hapus/<int:pendaftar_id>')
def hapus(pendaftar_id):
    pendaftar = Pendaftar.query.get_or_404(pendaftar_id)
    db.session.delete(pendaftar)
    db.session.commit()
    flash(f"Pendaftar {pendaftar.nama_lengkap} berhasil dihapus.", 'warning')
    return redirect(url_for('admin.dashboard'))
