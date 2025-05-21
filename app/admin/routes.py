from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_from_directory, current_app, send_file
from flask_login import login_required, current_user
from functools import wraps
from app.models import Pendaftaran, Berkas, User, Pembayaran, Pengumuman, KategoriPengumuman
from app.admin.forms import FilterPendaftarForm
from app import db
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pandas as pd
import io
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

# Decorator untuk membatasi akses admin
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Akses ditolak!', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def get_last_six_months():
    """Get list of datetime objects for the last 6 months"""
    today = datetime.today()
    months = []
    for i in range(6):
        month = today.replace(day=1) - relativedelta(months=i)
        months.append(month)
    return sorted(months)  # Return in ascending order

def get_monthly_counts():
    """Get registration counts for the last 6 months"""
    start_date = datetime.today().replace(day=1) - relativedelta(months=5)
    
    monthly_counts = db.session.query(
        func.strftime('%Y-%m', Pendaftaran.created_at).label('month'),
        func.count(Pendaftaran.id).label('count')
    ).filter(
        Pendaftaran.created_at >= start_date
    ).group_by(
        'month'
    ).order_by(
        'month'
    ).all()
    
    # Create a dict of month: count
    counts_dict = {m[0]: m[1] for m in monthly_counts}
    
    # Fill in missing months with zero
    counts = []
    for month in get_last_six_months():
        month_key = month.strftime('%Y-%m')
        counts.append(counts_dict.get(month_key, 0))
    
    return counts

def get_jurusan_stats():
    """Get registration counts by jurusan"""
    return db.session.query(
        Pendaftaran.jurusan_pilihan,
        func.count(Pendaftaran.id)
    ).group_by(
        Pendaftaran.jurusan_pilihan
    ).all()


@admin_bp.route('/profil')
@admin_required
def profil():
    return render_template('admin/profil.html')


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Basic statistics with explicit type conversion
    stats = {
        'total_pendaftar': int(Pendaftaran.query.count()),
        'menunggu': int(Pendaftaran.query.filter_by(status='Menunggu').count()),
        'terverifikasi': int(Pendaftaran.query.filter_by(status='Diverifikasi').count()),
        'ditolak': int(Pendaftaran.query.filter_by(status='Ditolak').count())
    }

    # Chart data processing
    today = datetime.today()
    start_month = today.replace(day=1) - relativedelta(months=5)
    
    # Monthly registration data
    monthly_data = []
    for i in range(6):
        current_month = start_month + relativedelta(months=i)
        next_month = current_month + relativedelta(months=1)
        
        count = int(Pendaftaran.query.filter(
            Pendaftaran.created_at >= current_month,
            Pendaftaran.created_at < next_month
        ).count())
        
        monthly_data.append({
            'month': current_month.strftime('%B %Y'),
            'count': count
        })

    # Process jurusan statistics
    jurusan_stats = db.session.query(
        Pendaftaran.jurusan_pilihan,
        db.func.count(Pendaftaran.id).label('total')
    ).group_by(Pendaftaran.jurusan_pilihan).all()

    jurusan_data = [{
        'name': str(stat[0]),
        'count': int(stat[1])
    } for stat in jurusan_stats]

    # Recent activities
    recent_activities = []
    recent_pendaftar = Pendaftaran.query.order_by(
        Pendaftaran.created_at.desc()
    ).limit(5).all()

    for p in recent_pendaftar:
        activity = {
            'type': 'pendaftaran',
            'name': str(p.nama_lengkap),
            'date': p.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'status': str(p.status)
        }
        recent_activities.append(activity)

    return render_template('admin/dashboard.html',
                         stats=stats,
                         monthly_data=monthly_data,
                         jurusan_data=jurusan_data,
                         activities=recent_activities)
# List pendaftar dengan filte
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
    return render_template('admin/list_pendaftar.html', form=form, pendaftars=pendaftars)

# Detail pendaftar
@admin_bp.route('/pendaftar/<int:id>')
@admin_required
def detail_pendaftar(id):
    pendaftar = Pendaftaran.query.get_or_404(id)
    return render_template('admin/detail_pendaftar.html', pendaftar=pendaftar)

# Verifikasi pendaftar
@admin_bp.route('/pendaftar/<int:id>/verifikasi', methods=['POST'])
@admin_required
def verifikasi_pendaftar(id):
    pendaftar = Pendaftaran.query.get_or_404(id)
    pendaftar.status = 'Diverifikasi'
    db.session.commit()
    flash(f'Pendaftar {pendaftar.nama_lengkap} telah diverifikasi.', 'success')
    return redirect(url_for('admin.list_pendaftar'))

# Tolak pendaftar
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

# Hapus pendaftar beserta berkasnya (jika ada)
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

# List berkas
@admin_bp.route('/berkas')
@admin_required
def list_berkas():
    berkas_list = Berkas.query.order_by(Berkas.uploaded_at.desc()).all()
    return render_template('admin/berkas.html', berkas_list=berkas_list)

# Verifikasi berkas
@admin_bp.route('/berkas/<int:berkas_id>/verifikasi', methods=['POST'])
@admin_required
def verifikasi_berkas(berkas_id):
    berkas = Berkas.query.get_or_404(berkas_id)
    berkas.status = 'Diverifikasi'
    db.session.commit()
    flash(f'Berkas {berkas.jenis_berkas} telah diverifikasi.', 'success')
    return jsonify({'status': 'success'})

# Tolak berkas
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

# Lihat berkas (download/view file)
@admin_bp.route('/berkas/<int:berkas_id>/view')
@admin_required
def lihat_berkas(berkas_id):
    berkas = Berkas.query.get_or_404(berkas_id)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], berkas.nama_file)

# List pembayaran
@admin_bp.route('/pembayaran')
@admin_required
def list_pembayaran():
    pembayaran_list = Pembayaran.query.order_by(Pembayaran.tanggal_bayar.desc()).all()
    return render_template('admin/pembayaran.html', pembayaran_list=pembayaran_list)

# Verifikasi pembayaran
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

# Tolak pembayaran
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

# Lihat bukti pembayaran
@admin_bp.route('/pembayaran/<int:pembayaran_id>/bukti')
@admin_required
def lihat_bukti(pembayaran_id):
    pembayaran = Pembayaran.query.get_or_404(pembayaran_id)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], pembayaran.bukti_pembayaran)

# Statistik pendaftar berdasarkan jurusan dan jalur
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
    
    return render_template('admin/statistik.html', jurusan_stats=jurusan_stats, jalur_stats=jalur_stats)

# Export data pendaftar ke Excel
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

@admin_bp.route('/pengumuman')
@admin_required
def pengumuman():
    pengumuman_list = Pengumuman.query.order_by(Pengumuman.updated_at.desc()).all()
    kategori_list = KategoriPengumuman.query.all()
    return render_template('admin/pengumuman.html', pengumuman_list=pengumuman_list, kategori_list=kategori_list)

@admin_bp.route('/pengumuman/<int:id>')
@admin_required
def get_pengumuman(id):
    pengumuman = Pengumuman.query.get_or_404(id)
    return jsonify({
        'judul': pengumuman.judul,
        'kategori_id': pengumuman.kategori_id,
        'kategori_nama': pengumuman.kategori.nama if pengumuman.kategori else '',
        'publish_date': pengumuman.publish_date.strftime('%Y-%m-%dT%H:%M') if pengumuman.publish_date else '',
        'konten': pengumuman.konten
    })

@admin_bp.route('/pengumuman/<int:id>/edit', methods=['POST'])
@admin_required
def edit_pengumuman(id):
    pengumuman = Pengumuman.query.get_or_404(id)
    data = request.form
    pengumuman.judul = data.get('judul')
    pengumuman.kategori_id = int(data.get('kategori_id')) if data.get('kategori_id') else None
    publish_date_str = data.get('publish_date')
    if publish_date_str:
        pengumuman.publish_date = datetime.strptime(publish_date_str, '%Y-%m-%dT%H:%M')
    else:
        pengumuman.publish_date = None
    pengumuman.konten = data.get('konten')
    pengumuman.updated_at = datetime.utcnow()
    db.session.commit()
    flash('Pengumuman berhasil diperbarui.', 'success')
    return redirect(url_for('admin.pengumuman'))

@admin_bp.route('/pengumuman/tambah', methods=['POST'])
@admin_required
def tambah_pengumuman():
    data = request.form
    publish_date = None
    if data.get('publish_date'):
        publish_date = datetime.strptime(data.get('publish_date'), '%Y-%m-%dT%H:%M')
    pengumuman = Pengumuman(
        judul=data.get('judul'),
        kategori_id=int(data.get('kategori_id')) if data.get('kategori_id') else None,
        publish_date=publish_date,
        konten=data.get('konten'),
        is_published=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by=current_user.id
    )
    db.session.add(pengumuman)
    db.session.commit()
    flash('Pengumuman berhasil ditambahkan.', 'success')
    return redirect(url_for('admin.pengumuman'))

@admin_bp.route('/pengumuman/<int:id>/delete', methods=['POST'])
@admin_required
def delete_pengumuman(id):
    pengumuman = Pengumuman.query.get_or_404(id)
    db.session.delete(pengumuman)
    db.session.commit()
    flash('Pengumuman berhasil dihapus.', 'success')
    return jsonify({'status': 'success'})

@admin_bp.route('/pengumuman/<int:id>/toggle', methods=['POST'])
@admin_required
def toggle_pengumuman(id):
    pengumuman = Pengumuman.query.get_or_404(id)
    pengumuman.is_published = not pengumuman.is_published
    pengumuman.updated_at = datetime.utcnow()
    db.session.commit()
    status = 'diterbitkan' if pengumuman.is_published else 'disembunyikan'
    flash(f'Pengumuman berhasil {status}.', 'info')
    return jsonify({'status': 'success', 'published': pengumuman.is_published})

