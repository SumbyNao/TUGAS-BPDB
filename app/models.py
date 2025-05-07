from app import db
from flask_login import UserMixin
from datetime import datetime

# --------------------------
# USER (untuk login)
# --------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user') 

    # Relasi ke pendaftar (1 user hanya bisa mendaftar sekali)
    pendaftar = db.relationship('Pendaftar', backref='user', uselist=False)


# --------------------------
# PENDAFTAR (formulir siswa)
# --------------------------
class Pendaftar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    nama_lengkap = db.Column(db.String(100), nullable=False)
    nisn = db.Column(db.String(10), nullable=False, unique=True)
    tempat_lahir = db.Column(db.String(50), nullable=False)
    tanggal_lahir = db.Column(db.Date, nullable=False)
    jenis_kelamin = db.Column(db.String(1), nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    asal_sekolah = db.Column(db.String(100), nullable=False)
    jalur_pendaftaran = db.Column(db.String(20), nullable=False)
    tanggal_daftar = db.Column(db.DateTime, default=datetime.utcnow)

    # Status verifikasi
    status = db.Column(db.String(20), default='Menunggu')  # Menunggu, Diverifikasi, Ditolak

    # Relasi ke berkas
    berkas = db.relationship('Berkas', backref='pendaftar', uselist=False)

# --------------------------
# BERKAS PENDAFTAR
# --------------------------
class Berkas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pendaftar_id = db.Column(db.Integer, db.ForeignKey('pendaftar.id'), nullable=False)

    kartu_keluarga = db.Column(db.String(200))
    akta_kelahiran = db.Column(db.String(200))
    rapor = db.Column(db.String(200))
    surat_keterangan = db.Column(db.String(200))
    tanggal_upload = db.Column(db.DateTime, default=datetime.utcnow)
