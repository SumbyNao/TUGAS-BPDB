import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash
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
    form = FormulirPPDB()
    if current_user.pendaftar:
        flash("Kamu sudah mengisi formulir PPDB.", "info")
        return redirect(url_for('ppdb.status'))

    if form.validate_on_submit():
        # ...form processing code...
        pass
        
    return render_template('ppdb/form_ppdb.html', form=form)

@ppdb_bp.route('/status')
@login_required
def status():
    pendaftar = current_user.pendaftar
    if not pendaftar:
        flash("Anda belum mengisi formulir pendaftaran.", "warning")
        return redirect(url_for('ppdb.formulir'))
    return render_template('ppdb/status.html', pendaftar=pendaftar)

@ppdb_bp.route('/upload-berkas', methods=['GET', 'POST'])
@login_required
def upload_berkas():
    if not current_user.pendaftar:
        flash("Isi formulir terlebih dahulu.", "warning")
        return redirect(url_for('ppdb.formulir'))

    form = UploadBerkasForm()
    
    if form.validate_on_submit():
        try:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            def save_file(file_obj):
                if file_obj:
                    filename = secure_filename(file_obj.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, f"{current_user.id}_{filename}")
                    file_obj.save(filepath)
                    return filepath
                return None

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
        except Exception as e:
            db.session.rollback()
            flash("Terjadi kesalahan saat upload berkas.", "danger")
    
    return render_template('ppdb/detail.html', form=form)