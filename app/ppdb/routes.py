from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Pendaftar, Berkas
from app.forms import FormulirPPDB, UploadBerkasForm
from . import ppdb_bp
import os
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = 'app/static/uploads/'

@ppdb_bp.route('/')
def index():
    return render_template('index.html')

@ppdb_bp.route('/formulir', methods=['GET', 'POST'])
@login_required
def formulir():
    form = FormulirPPDB()
    if current_user.pendaftar:
        flash("Kamu sudah mengisi formulir PPDB.", "info")
        return redirect(url_for('ppdb.status'))

    if form.validate_on_submit():
        pendaftar = Pendaftar(
            user_id=current_user.id,
            nama_lengkap=form.nama_lengkap.data,
            nisn=form.nisn.data,
            tempat_lahir=form.tempat_lahir.data,
            tanggal_lahir=form.tanggal_lahir.data,
            jenis_kelamin=form.jenis_kelamin.data,
            alamat=form.alamat.data,
            asal_sekolah=form.asal_sekolah.data,
            jalur_pendaftaran=form.jalur_pendaftaran.data,
        )
        db.session.add(pendaftar)
        db.session.commit()
        flash("Formulir berhasil disimpan!", "success")
        return redirect(url_for('ppdb.upload_berkas'))
    return render_template('ppdb/form_ppdb.html', form=form)

@ppdb_bp.route('/status')
@login_required
def status():
    pendaftar = current_user.pendaftar
    return render_template('ppdb/status.html', pendaftar=pendaftar)

@ppdb_bp.route('/upload-berkas', methods=['GET', 'POST'])
@login_required
def upload_berkas():
    if not current_user.pendaftar:
        flash("Isi formulir terlebih dahulu.", "warning")
        return redirect(url_for('ppdb.formulir'))

    form = UploadBerkasForm()
    if form.validate_on_submit():
        # Buat folder jika belum ada
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Simpan file
        def save_file(file_obj):
            filename = secure_filename(file_obj.filename)
            filepath = os.path.join(UPLOAD_FOLDER, f"{current_user.id}_{filename}")
            file_obj.save(filepath)
            return filepath

        berkas = Berkas(
            pendaftar_id=current_user.pendaftar.id,
            kartu_keluarga=save_file(form.kartu_keluarga.data),
            akta_kelahiran=save_file(form.akta_kelahiran.data),
            rapor=save_file(form.rapor.data),
            surat_keterangan=save_file(form.surat_keterangan.data),
            tanggal_upload=datetime.utcnow()
        )

        db.session.add(berkas)
        db.session.commit()
        flash("Berkas berhasil diupload!", "success")
        return redirect(url_for('ppdb.status'))

    return render_template('ppdb/upload_berkas.html', form=form)
