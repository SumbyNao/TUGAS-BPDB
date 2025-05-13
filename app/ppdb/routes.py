import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Pendaftar, Berkas
from app.ppdb.forms import FormulirPPDB, UploadBerkasForm
from config import UPLOAD_FOLDER

ppdb_bp = Blueprint('ppdb', __name__)

@ppdb_bp.route('/formulir', methods=['GET', 'POST'])
@login_required
def formulir():
    if current_user.pendaftar:
        flash('Anda sudah mengisi formulir pendaftaran.', 'info')
        return redirect(url_for('ppdb.status'))

    form = FormulirPPDB()
    if form.validate_on_submit():
        pendaftar = Pendaftar(
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
            jalur_pendaftaran=form.jalur_pendaftaran.data
        )
        db.session.add(pendaftar)
        db.session.commit()
        flash('Formulir berhasil dikirim!', 'success')
        return redirect(url_for('ppdb.upload_berkas'))
    return render_template('ppdb/formulir.html', form=form)

@ppdb_bp.route('/status')
@login_required
def status():
    pendaftar = current_user.pendaftar
    return render_template('ppdb/status.html', pendaftar=pendaftar)

@ppdb_bp.route('/upload-berkas', methods=['GET', 'POST'])
@login_required
def upload_berkas():
    if not current_user.pendaftar:
        flash('Silakan isi formulir pendaftaran terlebih dahulu.', 'warning')
        return redirect(url_for('ppdb.formulir'))

    form = UploadBerkasForm()
    if form.validate_on_submit():
        berkas_types = ['kartu_keluarga', 'akta_kelahiran', 'rapor', 'surat_keterangan']
        
        for berkas_type in berkas_types:
            file = getattr(form, berkas_type).data
            if file:
                filename = f"{current_user.pendaftar.nisn}_{berkas_type}.{file.filename.split('.')[-1]}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                
                berkas = Berkas(
                    pendaftar_id=current_user.pendaftar.id,
                    jenis_berkas=berkas_type,
                    nama_file=filename
                )
                db.session.add(berkas)
        
        db.session.commit()
        flash('Berkas berhasil diupload!', 'success')
        return redirect(url_for('ppdb.status'))
    
    return render_template('ppdb/upload_berkas.html', form=form)