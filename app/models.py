from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.nama_lengkap}>'

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

    def __repr__(self):
        return f'<Pendaftar {self.nama_lengkap} - NISN: {self.nisn}>'

    @property
    def status_pendaftaran(self):
        return self.status.title()

    def update_status(self, new_status):
        allowed_status = ['Menunggu', 'Diverifikasi', 'Ditolak']
        if new_status in allowed_status:
            self.status = new_status
            return True
        return False

    @property
    def has_paid(self):
        return any(payment.status == 'success' for payment in self.payments)

    @property
    def latest_payment(self):
        return Payment.query.filter_by(
            pendaftar_id=self.id
        ).order_by(Payment.created_at.desc()).first()

    @property
    def payment_status(self):
        if not self.payments:
            return "Belum Bayar"
        latest = self.latest_payment
        return latest.status_display if latest else "Belum Bayar"

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

    def __repr__(self):
        return f'<Berkas Pendaftar ID: {self.pendaftar_id}>'

    def is_complete(self):
        return all([
            self.kartu_keluarga,
            self.akta_kelahiran,
            self.rapor,
            self.surat_keterangan
        ])

# --------------------------
# PEMBAYARAN
# --------------------------
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pendaftar_id = db.Column(db.Integer, db.ForeignKey('pendaftar.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')  # pending, success, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)

    # Relasi ke pendaftar
    pendaftar = db.relationship('Pendaftar', backref='payments')

    def __repr__(self):
        return f'<Payment {self.transaction_id}>'

    @property
    def status_display(self):
        status_map = {
            'pending': 'Menunggu Pembayaran',
            'success': 'Pembayaran Berhasil',
            'failed': 'Pembayaran Gagal'
        }
        return status_map.get(self.status, self.status)

    def update_status(self, new_status, transaction_id=None):
        allowed_status = ['pending', 'success', 'failed']
        if new_status in allowed_status:
            self.status = new_status
            if new_status == 'success':
                self.paid_at = datetime.utcnow()
                if transaction_id:
                    self.transaction_id = transaction_id
            return True
        return False
