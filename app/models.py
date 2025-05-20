from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    nama_lengkap = db.Column(db.String(100), nullable=False)
    no_hp = db.Column(db.String(15))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    profile_picture = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_ip = db.Column(db.String(45))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    pendaftaran = db.relationship('Pendaftaran', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

class Pendaftaran(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    no_pendaftaran = db.Column(db.String(20), unique=True)
    nisn = db.Column(db.String(10), unique=True)
    nik = db.Column(db.String(16))
    nama_lengkap = db.Column(db.String(100))
    jenis_kelamin = db.Column(db.String(1))  # L/P
    tempat_lahir = db.Column(db.String(50))
    tanggal_lahir = db.Column(db.Date)
    agama = db.Column(db.String(20))
    alamat = db.Column(db.Text)
    rt = db.Column(db.String(3))
    rw = db.Column(db.String(3))
    kelurahan = db.Column(db.String(50))
    kecamatan = db.Column(db.String(50))
    kota = db.Column(db.String(50))
    kode_pos = db.Column(db.String(5))
    no_hp = db.Column(db.String(15))
    
    # Data Orangtua
    nama_ayah = db.Column(db.String(100))
    pekerjaan_ayah = db.Column(db.String(50))
    nama_ibu = db.Column(db.String(100))
    pekerjaan_ibu = db.Column(db.String(50))
    no_hp_ortu = db.Column(db.String(15))
    
    # Data Akademik
    asal_sekolah = db.Column(db.String(100))
    npsn_sekolah = db.Column(db.String(8))
    nilai_rata_rata = db.Column(db.Float)
    jurusan_id = db.Column(db.Integer, db.ForeignKey('jurusan.id'))
    jalur_pendaftaran = db.Column(db.String(20))  # Reguler/Prestasi/KIP
    
    # Status
    status_pendaftaran = db.Column(db.String(20), default='Draft')  # Draft/Submitted/Verified/Rejected
    status_seleksi = db.Column(db.String(20))  # Proses/Diterima/Tidak Diterima
    no_urut = db.Column(db.Integer)  # Nomor urut seleksi
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    berkas = db.relationship('Berkas', backref='pendaftaran', lazy=True)
    pembayaran = db.relationship('Pembayaran', backref='pendaftaran', lazy=True)
    daftar_ulang = db.relationship('DaftarUlang', backref='pendaftaran', uselist=False)

class Jurusan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(10), unique=True)
    nama = db.Column(db.String(100))
    deskripsi = db.Column(db.Text)
    kuota = db.Column(db.Integer)
    pendaftar = db.relationship('Pendaftaran', backref='jurusan', lazy=True)

class Berkas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pendaftaran_id = db.Column(db.Integer, db.ForeignKey('pendaftaran.id'))
    jenis = db.Column(db.String(50))  # KK/Akta/Rapor/SKHUN
    nama_file = db.Column(db.String(255))
    ukuran = db.Column(db.Integer)  # Ukuran dalam bytes
    status = db.Column(db.String(20), default='Pending')  # Pending/Valid/Invalid
    keterangan = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Pembayaran(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pendaftaran_id = db.Column(db.Integer, db.ForeignKey('pendaftaran.id'))
    no_invoice = db.Column(db.String(20), unique=True)
    jumlah = db.Column(db.Integer)
    metode = db.Column(db.String(50))
    bukti = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Pending')  # Pending/Valid/Invalid
    tanggal_bayar = db.Column(db.DateTime)
    verified_at = db.Column(db.DateTime)
    verified_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class DaftarUlang(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pendaftaran_id = db.Column(db.Integer, db.ForeignKey('pendaftaran.id'))
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Pending/Selesai
    verifikasi_admin = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime)
    verified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    berkas = db.relationship('BerkasDaftarUlang', backref='daftar_ulang', lazy=True)

class BerkasDaftarUlang(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    daftar_ulang_id = db.Column(db.Integer, db.ForeignKey('daftar_ulang.id'))
    jenis = db.Column(db.String(50))
    nama_file = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Pengumuman(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200))
    konten = db.Column(db.Text)
    kategori_id = db.Column(db.Integer, db.ForeignKey('kategori_pengumuman.id'))
    is_published = db.Column(db.Boolean, default=False)
    publish_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class KategoriPengumuman(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(50))
    slug = db.Column(db.String(50), unique=True)
    pengumuman = db.relationship('Pengumuman', backref='kategori', lazy=True)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100))
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
