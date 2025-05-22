import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Pengumuman, Pendaftaran, Berkas, Pembayaran
from app.ppdb.forms import FormulirPPDB, UploadBerkasForm, PembayaranForm
from config import UPLOAD_FOLDER

ppdb_bp = Blueprint('ppdb', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ppdb_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        # Check if user is admin
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
            
        # Get user's registration data
        pendaftaran = Pendaftaran.query.filter_by(user_id=current_user.id).first()
        
        # Get berkas if pendaftaran exists
        berkas = []
        if pendaftaran:
            berkas = Berkas.query.filter_by(pendaftar_id=pendaftaran.id).all()
            
        # Get pembayaran if pendaftaran exists
        pembayaran = None
        if pendaftaran:
            pembayaran = Pembayaran.query.filter_by(pendaftar_id=pendaftaran.id).first()
            
        # Calculate progress
        progress = 0
        if pendaftaran:
            progress += 33  # Formulir terisi
            if berkas and len(berkas) >= 4:
                progress += 33  # Berkas lengkap
            if pembayaran and pembayaran.status == 'Diverifikasi':
                progress += 34  # Pembayaran diverifikasi
                
        # Get pengumuman
        pengumuman_list = Pengumuman.query.filter(
            Pengumuman.is_published == True,
            Pengumuman.publish_date <= datetime.utcnow()
        ).order_by(Pengumuman.publish_date.desc()).limit(5).all()
        
        return render_template('ppdb/dashboard.html',
                             pendaftaran=pendaftaran,
                             berkas=berkas,
                             pembayaran=pembayaran,
                             progress=progress,
                             pengumuman_list=pengumuman_list)
                             
    except Exception as e:
        current_app.logger.error(f"Error in dashboard: {str(e)}")
        flash('Terjadi kesalahan saat memuat dashboard.', 'danger')
        return redirect(url_for('main.index'))

@ppdb_bp.route('/formulir', methods=['GET', 'POST'])
@login_required
def formulir():
    # Cek status pendaftaran yang ada
    existing = Pendaftaran.query.filter_by(user_id=current_user.id).first()
    if existing:
        # Tampilkan pesan sesuai status
        status_messages = {
            'Menunggu': 'Pendaftaran Anda sedang dalam proses verifikasi.',
            'Diverifikasi': 'Pendaftaran Anda telah diterima.',
            'Ditolak': 'Maaf, pendaftaran Anda ditolak.'
        }
        flash(status_messages.get(existing.status, 'Anda sudah melakukan pendaftaran.'), 'info')
        return redirect(url_for('ppdb.dashboard'))

    form = FormulirPPDB()
    if form.validate_on_submit():
        try:
            # Generate nomor pendaftaran
            last_pendaftaran = Pendaftaran.query.order_by(Pendaftaran.id.desc()).first()
            no_urut = 1 if not last_pendaftaran else last_pendaftaran.id + 1
            no_pendaftaran = f"PPDB{datetime.now().strftime('%Y')}{no_urut:04d}"
            
            pendaftar = Pendaftaran(
                user_id=current_user.id,
                no_pendaftaran=no_pendaftaran,
                nisn=form.nisn.data,
                nama_lengkap=form.nama_lengkap.data,
                tempat_lahir=form.tempat_lahir.data,
                tanggal_lahir=form.tanggal_lahir.data,
                jenis_kelamin=form.jenis_kelamin.data,
                agama=form.agama.data,
                alamat=form.alamat.data,
                no_hp=form.no_hp.data,
                asal_sekolah=form.asal_sekolah.data,
                jurusan_pilihan=form.jurusan_pilihan.data,
                jalur_pendaftaran=form.jalur_pendaftaran.data,
                status='Menunggu',
                status_pendaftaran='Submitted',
                created_at=datetime.utcnow()
            )
            db.session.add(pendaftar)
            db.session.commit()

            # Log aktivitas
            current_app.logger.info(f"Pendaftaran baru: {no_pendaftaran} oleh {current_user.email}")
            
            flash('Formulir berhasil dikirim! Silakan upload berkas yang diperlukan.', 'success')
            return redirect(url_for('ppdb.dashboard'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saat pendaftaran: {str(e)}")
            flash('Terjadi kesalahan. Silakan coba lagi.', 'danger')
            
    return render_template('ppdb/formulir.html', form=form)

@ppdb_bp.route('/upload-berkas', methods=['GET', 'POST'])
@login_required
def upload_berkas():
    if not current_user.pendaftaran:
        flash('Silakan isi formulir pendaftaran terlebih dahulu.', 'warning')
        return redirect(url_for('ppdb.formulir'))

    form = UploadBerkasForm()
    existing_berkas = {
        berkas.jenis_berkas: berkas 
        for berkas in Berkas.query.filter_by(pendaftar_id=current_user.pendaftaran.id).all()
    }

    if form.validate_on_submit():
        berkas_types = ['kartu_keluarga', 'akta_kelahiran', 'rapor', 'surat_keterangan']
        uploaded = False
        
        try:
            for berkas_type in berkas_types:
                file = getattr(form, berkas_type).data
                if file and allowed_file(file.filename):
                    filename = secure_filename(
                        f"{current_user.pendaftaran.nisn}_{berkas_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}"
                    )
                    
                    # Delete existing file if it exists
                    if berkas_type in existing_berkas:
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                              existing_berkas[berkas_type].nama_file)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                        db.session.delete(existing_berkas[berkas_type])
                    
                    # Save new file
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    berkas = Berkas(
                        pendaftar_id=current_user.pendaftaran.id,
                        jenis_berkas=berkas_type,
                        nama_file=filename,
                        status='Menunggu',
                        uploaded_at=datetime.utcnow()
                    )
                    db.session.add(berkas)
                    uploaded = True
            
            if uploaded:
                db.session.commit()
                flash('Berkas berhasil diupload!', 'success')
                return redirect(url_for('ppdb.dashboard'))
            else:
                flash('Tidak ada berkas yang diupload.', 'warning')
                
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat mengupload berkas.', 'danger')
            current_app.logger.error(f"Error in upload_berkas: {str(e)}")
    
    return render_template('ppdb/upload_berkas.html', 
                         form=form, 
                         existing_berkas=existing_berkas)

@ppdb_bp.route('/pembayaran', methods=['GET', 'POST'])
@login_required
def pembayaran():
    if not current_user.pendaftaran:
        flash('Silakan isi formulir pendaftaran terlebih dahulu.', 'warning')
        return redirect(url_for('ppdb.formulir'))
        
    existing_payment = Pembayaran.query.filter_by(pendaftar_id=current_user.pendaftaran.id).first()
    if existing_payment:
        flash('Anda sudah melakukan pembayaran. Silakan tunggu verifikasi.', 'info')
        return redirect(url_for('ppdb.dashboard'))
        
    form = PembayaranForm()
    if form.validate_on_submit():
        try:
            bukti = form.bukti_pembayaran.data
            if bukti and allowed_file(bukti.filename):
                filename = secure_filename(
                    f"payment_{current_user.pendaftaran.nisn}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{bukti.filename.rsplit('.', 1)[1].lower()}"
                )
                bukti.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                
                pembayaran = Pembayaran(
                    pendaftar_id=current_user.pendaftaran.id,
                    jumlah=form.jumlah.data,
                    metode_pembayaran=form.metode_pembayaran.data,
                    bukti_pembayaran=filename,
                    status='Menunggu',
                    tanggal_bayar=datetime.utcnow()
                )
                db.session.add(pembayaran)
                db.session.commit()
                
                flash('Bukti pembayaran berhasil diupload! Silakan tunggu verifikasi.', 'success')
                return redirect(url_for('ppdb.dashboard'))
                
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat mengupload bukti pembayaran.', 'danger')
            current_app.logger.error(f"Error in pembayaran: {str(e)}")
    
    return render_template('ppdb/pembayaran.html', form=form)

@ppdb_bp.route('/status')
@login_required
def status():
    if not current_user.pendaftaran:
        flash('Silakan isi formulir pendaftaran terlebih dahulu.', 'warning')
        return redirect(url_for('ppdb.formulir'))
        
    pendaftar = current_user.pendaftaran
    berkas = Berkas.query.filter_by(pendaftar_id=pendaftar.id).all()
    pembayaran = Pembayaran.query.filter_by(pendaftar_id=pendaftar.id).first()
    
    return render_template('ppdb/status.html',
                         pendaftar=pendaftar,
                         berkas=berkas,
                         pembayaran=pembayaran)