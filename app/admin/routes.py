from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_from_directory, current_app, send_file
from flask_login import login_required, current_user
from functools import wraps
from app.models import Pendaftaran, Berkas, User, Pembayaran
from app.admin.forms import FilterPendaftarForm  # Add this import
from app import db
from datetime import datetime
import pandas as pd
import io

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Akses ditolak!', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_pendaftar': Pendaftaran.query.count(),
        'menunggu_verifikasi': Pendaftaran.query.filter_by(status='Menunggu').count(),
        'terverifikasi': Pendaftaran.query.filter_by(status='Diverifikasi').count(),
        'ditolak': Pendaftaran.query.filter_by(status='Ditolak').count()
    }
    pendaftars = Pendaftaran.query.order_by(Pendaftaran.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, pendaftars=pendaftars)

# Pendaftar Management Routes
@admin_bp.route('/pendaftar')
@admin_required
def list_pendaftar():
    form = FilterPendaftarForm()
    query = Pendaftaran.query
    
    if form.validate():
        if form.jalur.data:
            query = query.filter_by(jalur_pendaftaran=form.jalur.data)
        if form.jurusan.data:
            query = query.filter_by(jurusan_pilihan=form.jurusan.data)
        if form.status.data:
            query = query.filter_by(status=form.status.data)
        if form.asal_sekolah.data:
            query = query.filter(Pendaftaran.asal_sekolah.ilike(f'%{form.asal_sekolah.data}%'))
        if form.tanggal_awal.data:
            query = query.filter(Pendaftaran.created_at >= form.tanggal_awal.data)
        if form.tanggal_akhir.data:
            query = query.filter(Pendaftaran.created_at <= form.tanggal_akhir.data)
        if form.search.data:
            search = f"%{form.search.data}%"
            query = query.filter(
                db.or_(
                    Pendaftaran.nisn.ilike(search),
                    Pendaftaran.nama_lengkap.ilike(search)
                )
            )
    
    pendaftars = query.order_by(Pendaftaran.created_at.desc()).all()
    return render_template('admin/list_pendaftar.html', 
                         form=form, 
                         pendaftars=pendaftars)

@admin_bp.route('/pendaftar/<int:id>')
@admin_required
def detail_pendaftar(id):
    pendaftar = Pendaftaran.query.get_or_404(id)
    return render_template('admin/detail_pendaftar.html', pendaftar=pendaftar)

@admin_bp.route('/pendaftar/<int:id>/verifikasi', methods=['POST'])
@admin_required
def verifikasi_pendaftar(id):
    pendaftar = Pendaftaran.query.get_or_404(id)
    pendaftar.status = 'Diverifikasi'
    db.session.commit()
    flash(f'Pendaftar {pendaftar.nama_lengkap} telah diverifikasi.', 'success')
    return redirect(url_for('admin.list_pendaftar'))

@admin_bp.route('/pendaftar/<int:id>/tolak', methods=['POST'])
@admin_required
def tolak_pendaftar(id):
    pendaftar = Pendaftaran.query.get_or_404(id)
    alasan = request.form.get('alasan')
    pendaftar.status = 'Ditolak'
    pendaftar.alasan_penolakan = alasan
    db.session.commit()
    flash(f'Pendaftaran {pendaftar.nama_lengkap} ditolak.', 'warning')
    return redirect(url_for('admin.list_pendaftar'))

@admin_bp.route('/pendaftar/<int:id>/hapus', methods=['POST'])
@admin_required
def hapus_pendaftar(id):
    pendaftar = Pendaftaran.query.get_or_404(id)
    berkas = Berkas.query.filter_by(pendaftar_id=pendaftar.id).first()
    if berkas:
        db.session.delete(berkas)
    db.session.delete(pendaftar)
    db.session.commit()
    flash(f"Pendaftar {pendaftar.nama_lengkap} berhasil dihapus.", 'warning')
    return redirect(url_for('admin.list_pendaftar'))

# Berkas Management Routes
@admin_bp.route('/berkas')
@admin_required
def list_berkas():
    berkas_list = Berkas.query.order_by(Berkas.uploaded_at.desc()).all()
    return render_template('admin/berkas.html', berkas_list=berkas_list)

@admin_bp.route('/berkas/<int:berkas_id>/verifikasi', methods=['POST'])
@admin_required
def verifikasi_berkas(berkas_id):
    berkas = Berkas.query.get_or_404(berkas_id)
    berkas.status = 'Diverifikasi'
    db.session.commit()
    flash(f'Berkas {berkas.jenis_berkas} telah diverifikasi.', 'success')
    return jsonify({'status': 'success'})

@admin_bp.route('/berkas/<int:berkas_id>/tolak', methods=['POST'])
@admin_required
def tolak_berkas(berkas_id):
    berkas = Berkas.query.get_or_404(berkas_id)
    data = request.get_json()
    berkas.status = 'Ditolak'
    berkas.alasan_penolakan = data.get('alasan')
    db.session.commit()
    flash(f'Berkas {berkas.jenis_berkas} telah ditolak.', 'warning')
    return jsonify({'status': 'success'})

@admin_bp.route('/berkas/<int:berkas_id>/view')
@admin_required
def lihat_berkas(berkas_id):
    berkas = Berkas.query.get_or_404(berkas_id)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], berkas.nama_file)

# Pembayaran Management Routes
@admin_bp.route('/pembayaran')
@admin_required
def list_pembayaran():
    pembayaran_list = Pembayaran.query.order_by(Pembayaran.tanggal_bayar.desc()).all()
    return render_template('admin/pembayaran.html', pembayaran_list=pembayaran_list)

@admin_bp.route('/pembayaran/<int:pembayaran_id>/verifikasi', methods=['POST'])
@admin_required
def verifikasi_pembayaran(pembayaran_id):
    pembayaran = Pembayaran.query.get_or_404(pembayaran_id)
    pembayaran.status = 'Diverifikasi'
    pembayaran.verified_at = datetime.utcnow()
    pembayaran.verified_by = current_user.id
    db.session.commit()
    flash(f'Pembayaran dari {pembayaran.pendaftar.nama_lengkap} telah diverifikasi.', 'success')
    return jsonify({'status': 'success'})

@admin_bp.route('/pembayaran/<int:pembayaran_id>/tolak', methods=['POST'])
@admin_required
def tolak_pembayaran(pembayaran_id):
    pembayaran = Pembayaran.query.get_or_404(pembayaran_id)
    data = request.get_json()
    pembayaran.status = 'Ditolak'
    pembayaran.alasan_penolakan = data.get('alasan')
    db.session.commit()
    flash(f'Pembayaran dari {pembayaran.pendaftar.nama_lengkap} telah ditolak.', 'warning')
    return jsonify({'status': 'success'})

@admin_bp.route('/pembayaran/<int:pembayaran_id>/bukti')
@admin_required
def lihat_bukti(pembayaran_id):
    pembayaran = Pembayaran.query.get_or_404(pembayaran_id)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], pembayaran.bukti_pembayaran)

# Statistics and Export Routes
@admin_bp.route('/statistik')
@admin_required
def statistik():
    jurusan_stats = db.session.query(
        Pendaftaran.jurusan_pilihan,
        db.func.count(Pendaftaran.id).label('total'),
        db.func.sum(db.case([(Pendaftaran.status == 'Diverifikasi', 1)], else_=0)).label('diterima')
    ).group_by(Pendaftaran.jurusan_pilihan).all()
    
    jalur_stats = db.session.query(
        Pendaftaran.jalur_pendaftaran,
        db.func.count(Pendaftaran.id).label('total')
    ).group_by(Pendaftaran.jalur_pendaftaran).all()
    
    return render_template('admin/statistik.html', 
                         jurusan_stats=jurusan_stats,
                         jalur_stats=jalur_stats)

@admin_bp.route('/export-data')
@admin_required
def export_data():
    pendaftars = Pendaftaran.query.all()
    data = []
    
    for p in pendaftars:
        data.append({
            'NISN': p.nisn,
            'Nama Lengkap': p.nama_lengkap,
            'Tempat Lahir': p.tempat_lahir,
            'Tanggal Lahir': p.tanggal_lahir,
            'Jenis Kelamin': p.jenis_kelamin,
            'Agama': p.agama,
            'Asal Sekolah': p.asal_sekolah,
            'Jurusan': p.jurusan_pilihan,
            'Jalur': p.jalur_pendaftaran,
            'Status': p.status
        })
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Data Pendaftar', index=False)
    writer.save()
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'data_pendaftar_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )
