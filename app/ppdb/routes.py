import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Pendaftaran, Berkas, Pembayaran  # Changed from Pendaftar to Pendaftaran
from app.ppdb.forms import FormulirPPDB, UploadBerkasForm, PembayaranForm
from config import UPLOAD_FOLDER

ppdb_bp = Blueprint('ppdb', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ppdb_bp.route('/dashboard')
@login_required
def dashboard():
    pendaftaran = Pendaftaran.query.filter_by(user_id=current_user.id).first()
    
    if not pendaftaran:
        flash('Silakan lengkapi formulir pendaftaran terlebih dahulu.', 'warning')
        return redirect(url_for('ppdb.formulir'))
    
    berkas = Berkas.query.filter_by(pendaftaran_id=pendaftaran.id).all()
    pembayaran = Pembayaran.query.filter_by(pendaftaran_id=pendaftaran.id).first()
    
    # Calculate completion percentage
    total_steps = 3  # formulir, berkas, pembayaran
    completed_steps = 1  # formulir already completed
    
    if berkas and len(berkas) >= 4:  # All required documents
        completed_steps += 1
    if pembayaran and pembayaran.status == 'Diverifikasi':
        completed_steps += 1
        
    progress = (completed_steps / total_steps) * 100
    
    return render_template('ppdb/dashboard.html',
                         pendaftaran=pendaftaran,
                         berkas=berkas,
                         pembayaran=pembayaran,
                         progress=progress)

@ppdb_bp.route('/formulir', methods=['GET', 'POST'])
@login_required
def formulir():
    if current_user.pendaftaran:
        flash('Anda sudah mengisi formulir pendaftaran.', 'info')
        return redirect(url_for('ppdb.dashboard'))

    form = FormulirPPDB()
    if form.validate_on_submit():
        try:
            pendaftar = Pendaftaran(
                user_id=current_user.id,
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
                created_at=datetime.utcnow()
            )
            db.session.add(pendaftar)
            db.session.commit()
            flash('Formulir berhasil dikirim! Silakan upload berkas yang diperlukan.', 'success')
            return redirect(url_for('ppdb.upload_berkas'))
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan. Silakan coba lagi.', 'danger')
            current_app.logger.error(f"Error in formulir: {str(e)}")
            
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