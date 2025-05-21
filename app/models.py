from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
from sqlalchemy.ext.hybrid import hybrid_property
from flask.json.provider import DefaultJSONProvider  # Changed from JsonProvider
from decimal import Decimal

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(obj, Decimal):
                return float(obj)
            elif hasattr(obj, '__dict__'):
                return str(obj)
            return str(obj)
        except Exception as e:
            return str(obj)

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

    @property
    def is_verified(self):
        return bool(self.pendaftaran and self.pendaftaran.status == 'Diverifikasi')

    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.commit()

    def log_activity(self, action, description, ip_address=None, user_agent=None):
        log = ActivityLog(
            user_id=self.id,
            action=action,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log)
        db.session.commit()
        
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
    status = db.Column(db.String(20), default='Menunggu')  # Menunggu/Diverifikasi/Ditolak
    status_pendaftaran = db.Column(db.String(20), default='Draft')  # Draft/Submitted/Verified/Rejected
    
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
    jalur_pendaftaran = db.Column(db.String(20)) 
    jurusan_pilihan = db.Column(db.String(100))# Reguler/Prestasi/KIP
    
    # Status
    status_seleksi = db.Column(db.String(20))  # Proses/Diterima/Tidak Diterima
    no_urut = db.Column(db.Integer)  # Nomor urut seleksi
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    berkas = db.relationship('Berkas', backref='pendaftaran', lazy=True)
    pembayaran = db.relationship('Pembayaran', backref='pendaftaran', lazy=True)
    daftar_ulang = db.relationship('DaftarUlang', backref='pendaftaran', uselist=False)

    @hybrid_property
    def status_display(self):
        status_map = {
            'Menunggu': 'Menunggu Verifikasi',
            'Diverifikasi': 'Diterima',
            'Ditolak': 'Ditolak'
        }
        return status_map.get(self.status, self.status)

    @hybrid_property
    def is_complete(self):
        """Check if all required fields are filled"""
        required_fields = [
            self.nisn, self.nama_lengkap, self.jenis_kelamin,
            self.tempat_lahir, self.tanggal_lahir, self.alamat,
            self.asal_sekolah, self.jurusan_pilihan
        ]
        return all(required_fields)

    @hybrid_property
    def berkas_status(self):
        """Get overall berkas verification status"""
        if not self.berkas:
            return 'Belum Upload'
        if all(b.status == 'Valid' for b in self.berkas):
            return 'Lengkap'
        return 'Belum Lengkap'

    def verify(self, admin_user, is_accepted=True):
        """Verify pendaftaran by admin"""
        self.status = 'Diverifikasi' if is_accepted else 'Ditolak'
        self.status_pendaftaran = 'Verified' if is_accepted else 'Rejected'
        self.updated_at = datetime.utcnow()
        
        admin_user.log_activity(
            'verify_pendaftaran',
            f'{"Menerima" if is_accepted else "Menolak"} pendaftaran {self.no_pendaftaran}'
        )
        db.session.commit()

class Jurusan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(10), unique=True)
    nama = db.Column(db.String(100))
    deskripsi = db.Column(db.Text)
    kuota = db.Column(db.Integer)
    pendaftar = db.relationship('Pendaftaran', backref='jurusan', lazy=True)

class Berkas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pendaftaran_id = db.Column(db.Integer, db.ForeignKey('pendaftaran.id'), nullable=False)
    jenis = db.Column(db.String(50))  # Changed from jenis_berkas
    nama_file = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Menunggu')
    keterangan = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Pembayaran(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pendaftaran_id = db.Column(db.Integer, db.ForeignKey('pendaftaran.id'), nullable=False)  # Changed from pendaftar_id
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
