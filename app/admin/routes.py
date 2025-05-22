from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_from_directory, current_app, send_file
from flask_login import login_required, current_user
from functools import wraps
from app.models import Pendaftaran, Berkas, User, Pembayaran, Pengumuman, KategoriPengumuman
from app.admin.forms import FilterPendaftarForm, PengumumanForm, AdminProfileForm  # Update this line
from app import db
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pandas as pd
import io
from sqlalchemy import func, case

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
    try:
        # Ambil semua data pendaftar
        pendaftar = Pendaftaran.query.order_by(Pendaftaran.created_at.desc()).all()
        
        # Debug info
        current_app.logger.info(f"Total pendaftar: {len(pendaftar)}")

        # Statistik dasar
        stats = {
            'total_pendaftar': int(Pendaftaran.query.count()),
            'menunggu': int(Pendaftaran.query.filter_by(status='Menunggu').count()),
            'terverifikasi': int(Pendaftaran.query.filter_by(status='Diverifikasi').count()),
            'ditolak': int(Pendaftaran.query.filter_by(status='Ditolak').count())
        }

        # Data grafik bulanan
        monthly_data = []
        today = datetime.today()
        start_month = today.replace(day=1) - relativedelta(months=5)
        
        for i in range(6):
            current_month = start_month + relativedelta(months=i)
            next_month = current_month + relativedelta(months=1)
            
            count = Pendaftaran.query.filter(
                Pendaftaran.created_at >= current_month,
                Pendaftaran.created_at < next_month
            ).count()
            
            monthly_data.append({
                'month': current_month.strftime('%B %Y'),
                'count': int(count)
            })

        # Statistik jurusan
        jurusan_stats = db.session.query(
            Pendaftaran.jurusan_pilihan,
            db.func.count(Pendaftaran.id).label('total')
        ).group_by(Pendaftaran.jurusan_pilihan).all()

        jurusan_data = [{
            'name': str(stat[0]) if stat[0] else 'Belum memilih',
            'count': int(stat[1])
        } for stat in jurusan_stats]

        # Aktivitas terbaru
        recent_activities = []
        for p in pendaftar[:5]:  # Ambil 5 pendaftar terbaru
            activity = {
                'created_at': p.created_at,
                'description': f"Pendaftaran baru dari {p.nama_lengkap}",
                'user': {'nama_lengkap': p.nama_lengkap},
                'status': p.status,
                'status_color': 'warning' if p.status == 'Menunggu'
                               else 'success' if p.status == 'Diverifikasi'
                               else 'danger'
            }
            recent_activities.append(activity)

        return render_template('admin/dashboard.html',
                             stats=stats,
                             pendaftar=pendaftar,  # Tambahkan ini
                             monthly_data=monthly_data,
                             jurusan_data=jurusan_data,
                             activities=recent_activities)

    except Exception as e:
        current_app.logger.error(f"Error di dashboard admin: {str(e)}")
        flash('Terjadi kesalahan saat memuat data.', 'danger')
        return redirect(url_for('admin.index'))

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
    try:
        pendaftar = Pendaftaran.query.get_or_404(id)
        berkas = Berkas.query.filter_by(pendaftar_id=pendaftar.id).all()
        pembayaran = Pembayaran.query.filter_by(pendaftar_id=pendaftar.id).first()
        
        return render_template('admin/detail_pendaftar.html',
                             pendaftar=pendaftar,
                             berkas=berkas,
                             pembayaran=pembayaran)
                             
    except Exception as e:
        current_app.logger.error(f"Error saat melihat detail: {str(e)}")
        flash('Terjadi kesalahan saat memuat detail pendaftar.', 'danger')
        return redirect(url_for('admin.dashboard'))

# Verifikasi pendaftar
@admin_bp.route('/pendaftar/<int:id>/verifikasi', methods=['POST'])
@admin_required
def verifikasi_pendaftar(id):
    try:
        pendaftar = Pendaftaran.query.get_or_404(id)
        action = request.form.get('action')
        
        if action == 'terima':
            pendaftar.status = 'Diverifikasi'
            message = f'Pendaftar {pendaftar.nama_lengkap} telah diterima'
        elif action == 'tolak':
            pendaftar.status = 'Ditolak'
            pendaftar.alasan_penolakan = request.form.get('alasan')
            message = f'Pendaftar {pendaftar.nama_lengkap} telah ditolak'
        
        pendaftar.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log aktivitas
        current_app.logger.info(f"Admin {current_user.nama_lengkap} {message}")
        flash(message, 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saat verifikasi: {str(e)}")
        flash('Terjadi kesalahan saat memverifikasi pendaftar.', 'danger')
    
    return redirect(url_for('admin.dashboard'))

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
    try:
        berkas = Berkas.query.get_or_404(berkas_id)
        berkas.status = 'Diverifikasi'
        db.session.commit()
        flash(f'Berkas {berkas.jenis_berkas} telah diverifikasi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error verifikasi berkas: {str(e)}")
        flash('Terjadi kesalahan saat verifikasi berkas.', 'danger')
    return redirect(url_for('admin.list_berkas'))

@admin_bp.route('/berkas/<int:berkas_id>/tolak', methods=['POST'])
@admin_required
def tolak_berkas(berkas_id):
    try:
        berkas = Berkas.query.get_or_404(berkas_id)
        alasan = request.form.get('alasan')
        berkas.status = 'Ditolak'
        berkas.alasan_penolakan = alasan
        db.session.commit()
        flash(f'Berkas {berkas.jenis_berkas} telah ditolak.', 'warning')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error tolak berkas: {str(e)}")
        flash('Terjadi kesalahan saat menolak berkas.', 'danger')
    return redirect(url_for('admin.list_berkas'))

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
    try:
        pembayaran = Pembayaran.query.get_or_404(pembayaran_id)
        pembayaran.status = 'Diverifikasi'
        pembayaran.verified_at = datetime.utcnow()
        pembayaran.verified_by = current_user.id
        db.session.commit()
        flash(f'Pembayaran dari {pembayaran.pendaftar.nama_lengkap} telah diverifikasi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error verifikasi pembayaran: {str(e)}")
        flash('Terjadi kesalahan saat verifikasi pembayaran.', 'danger')
    return redirect(url_for('admin.list_pembayaran'))

# Tolak pembayaran
@admin_bp.route('/pembayaran/<int:pembayaran_id>/tolak', methods=['POST'])
@admin_required
def tolak_pembayaran(pembayaran_id):
    try:
        pembayaran = Pembayaran.query.get_or_404(pembayaran_id)
        alasan = request.form.get('alasan')
        pembayaran.status = 'Ditolak'
        pembayaran.alasan_penolakan = alasan
        db.session.commit()
        flash(f'Pembayaran dari {pembayaran.pendaftar.nama_lengkap} telah ditolak.', 'warning')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error tolak pembayaran: {str(e)}")
        flash('Terjadi kesalahan saat menolak pembayaran.', 'danger')
    return redirect(url_for('admin.list_pembayaran'))

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
    try:
        # Statistik per jurusan
        jurusan_stats = db.session.query(
            Pendaftaran.jurusan_pilihan,
            db.func.count(Pendaftaran.id).label('total'),
            db.func.count(case(
                (Pendaftaran.status == 'Diverifikasi', 1),
            )).label('diterima')
        ).group_by(
            Pendaftaran.jurusan_pilihan
        ).all()

        jurusan_data = [{
            'jurusan_pilihan': stat[0] if stat[0] else 'Belum memilih',
            'total': int(stat[1]),
            'diterima': int(stat[2])
        } for stat in jurusan_stats]

        # Statistik per jalur pendaftaran
        jalur_stats = db.session.query(
            Pendaftaran.jalur_pendaftaran,
            db.func.count(Pendaftaran.id).label('total')
        ).group_by(
            Pendaftaran.jalur_pendaftaran
        ).all()

        jalur_data = [{
            'jalur_pendaftaran': stat[0] if stat[0] else 'Tidak ada jalur',
            'total': int(stat[1])
        } for stat in jalur_stats]

        return render_template('admin/statistik.html',
                             jurusan_stats=jurusan_data,
                             jalur_stats=jalur_data)

    except Exception as e:
        current_app.logger.error(f"Error in statistik: {str(e)}")
        flash('Terjadi kesalahan saat memuat statistik.', 'danger')
        return redirect(url_for('admin.dashboard'))

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
    try:
        # Buat instance form
        form = PengumumanForm()
        
        # Set pilihan kategori
        kategori_list = KategoriPengumuman.query.all()
        form.kategori.choices = [(k.id, k.nama) for k in kategori_list]
        
        # Ambil daftar pengumuman
        pengumuman_list = Pengumuman.query.order_by(Pengumuman.created_at.desc()).all()
        
        # Format data pengumuman
        formatted_pengumuman = []
        for p in pengumuman_list:
            kategori_color = 'primary'
            if p.kategori:
                if p.kategori.nama.lower() == 'penting':
                    kategori_color = 'danger'
                elif p.kategori.nama.lower() == 'info':
                    kategori_color = 'info'
                    
            formatted_pengumuman.append({
                'id': p.id,
                'judul': p.judul,
                'kategori': p.kategori.nama if p.kategori else '-',
                'kategori_color': kategori_color,
                'is_published': p.is_published,
                'publish_date': p.publish_date,
                'updated_at': p.updated_at,
                'konten': p.konten
            })
        
        return render_template('admin/pengumuman.html',
                             form=form,
                             pengumuman_list=formatted_pengumuman)
                             
    except Exception as e:
        current_app.logger.error(f"Error di halaman pengumuman: {str(e)}")
        flash('Terjadi kesalahan saat memuat data pengumuman.', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/pengumuman/tambah', methods=['POST'])
@admin_required
def tambah_pengumuman():
    form = PengumumanForm()
    # Set choices sebelum validasi
    kategori_list = KategoriPengumuman.query.all()
    form.kategori.choices = [(k.id, k.nama) for k in kategori_list]
    
    if form.validate_on_submit():
        try:
            pengumuman = Pengumuman(
                judul=form.judul.data,
                konten=form.konten.data,
                kategori_id=form.kategori.data,
                publish_date=form.publish_date.data,
                created_by=current_user.id
            )
            db.session.add(pengumuman)
            db.session.commit()
            flash('Pengumuman berhasil ditambahkan!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error tambah pengumuman: {str(e)}")
            flash('Terjadi kesalahan saat menambah pengumuman.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('admin.pengumuman'))

@admin_bp.route('/pengumuman/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_pengumuman(id):
    pengumuman = Pengumuman.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify({
            'judul': pengumuman.judul,
            'kategori_id': pengumuman.kategori_id,
            'konten': pengumuman.konten,
            'publish_date': pengumuman.publish_date.isoformat() if pengumuman.publish_date else None
        })
    
    form = PengumumanForm()
    if form.validate_on_submit():
        try:
            pengumuman.judul = form.judul.data
            pengumuman.kategori_id = form.kategori.data
            pengumuman.konten = form.konten.data
            pengumuman.publish_date = form.publish_date.data
            pengumuman.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Pengumuman berhasil diperbarui!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error edit pengumuman: {str(e)}")
            flash('Terjadi kesalahan saat memperbarui pengumuman.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')
                
    return redirect(url_for('admin.pengumuman'))

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_admin:
        flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
        return redirect(url_for('main.index'))
        
    form = AdminProfileForm()
    if form.validate_on_submit():
        try:
            current_user.nama = form.nama.data
            current_user.email = form.email.data
            
            if form.password.data:
                if form.password.data != form.password_confirm.data:
                    flash('Password tidak cocok.', 'danger')
                    return render_template('admin/profile.html', form=form)
                current_user.set_password(form.password.data)
                
            db.session.commit()
            flash('Profil berhasil diperbarui.', 'success')
            return redirect(url_for('admin.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat memperbarui profil.', 'danger')
            
    elif request.method == 'GET':
        form.nama.data = current_user.nama
        form.email.data = current_user.email
        
    return render_template('admin/profile.html', form=form)

