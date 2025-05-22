from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, TextAreaField, SelectField, DateField, SubmitField, BooleanField, IntegerField, DateTimeField, EmailField, PasswordField)
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange

class FilterPendaftarForm(FlaskForm):
    """Form untuk filter data pendaftar"""
    search = StringField('Cari (NISN/Nama)', 
        validators=[Optional(), Length(min=3, message="Minimal 3 karakter")])
    
    jalur = SelectField('Jalur Pendaftaran', 
        choices=[
            ('', 'Semua'),
            ('Reguler', 'Reguler'),
            ('Prestasi', 'Prestasi'),
            ('KIP', 'KIP')
        ])
    
    jurusan = SelectField('Jurusan',
        choices=[
            ('', 'Semua'),
            ('RPL', 'Rekayasa Perangkat Lunak'),
            ('TKJ', 'Teknik Komputer dan Jaringan'),
            ('MM', 'Multimedia'),
            ('AKL', 'Akuntansi'),
            ('BDP', 'Bisnis Daring dan Pemasaran')
        ])
    
    status = SelectField('Status',
        choices=[
            ('', 'Semua'),
            ('Menunggu', 'Menunggu'),
            ('Diverifikasi', 'Diverifikasi'),
            ('Ditolak', 'Ditolak')
        ])
    
    asal_sekolah = StringField('Asal Sekolah')
    tanggal_awal = DateField('Tanggal Awal', format='%Y-%m-%d')
    tanggal_akhir = DateField('Tanggal Akhir', format='%Y-%m-%d')
    submit = SubmitField('Filter')

class PengumumanForm(FlaskForm):
    """Form untuk manajemen pengumuman"""
    judul = StringField('Judul', validators=[
        DataRequired(message="Judul harus diisi"),
        Length(max=255, message="Judul maksimal 255 karakter")
    ])
    kategori = SelectField('Kategori', 
                          choices=[],  # Akan diisi saat form diinisialisasi
                          coerce=int,
                          validators=[DataRequired(message="Kategori harus dipilih")])
    publish_date = DateTimeField('Tanggal Publikasi', 
                               format='%Y-%m-%dT%H:%M',
                               validators=[DataRequired(message="Tanggal publikasi harus diisi")])
    konten = TextAreaField('Konten', validators=[
        DataRequired(message="Konten harus diisi")
    ])
    submit = SubmitField('Simpan')

class VerifikasiBerkasForm(FlaskForm):
    """Form untuk verifikasi berkas pendaftar"""
    status = SelectField('Status Verifikasi',
        choices=[
            ('pending', 'Belum Diverifikasi'),
            ('valid', 'Valid'),
            ('invalid', 'Tidak Valid')
        ],
        validators=[DataRequired(message="Pilih status verifikasi")])
    
    catatan = TextAreaField('Catatan',
        validators=[
            Optional(),
            Length(max=500, message="Catatan maksimal 500 karakter")
        ])
    
    submit = SubmitField('Simpan Status')

class JurusanForm(FlaskForm):
    """Form untuk manajemen jurusan"""
    nama = StringField('Nama Jurusan',
        validators=[
            DataRequired(message="Nama jurusan harus diisi"),
            Length(max=100, message="Nama jurusan maksimal 100 karakter")
        ])
    
    kode = StringField('Kode Jurusan',
        validators=[
            DataRequired(message="Kode jurusan harus diisi"),
            Length(max=10, message="Kode jurusan maksimal 10 karakter")
        ])
    
    deskripsi = TextAreaField('Deskripsi',
        validators=[DataRequired(message="Deskripsi harus diisi")])
    
    kuota = IntegerField('Kuota Siswa',
        validators=[
            DataRequired(message="Kuota harus diisi"),
            NumberRange(min=1, message="Kuota minimal 1 siswa")
        ])
    
    submit = SubmitField('Simpan Jurusan')

class HasilSeleksiForm(FlaskForm):
    """Form untuk input hasil seleksi"""
    status = SelectField('Status Kelulusan',
        choices=[
            ('pending', 'Belum Diproses'),
            ('lulus', 'Lulus'),
            ('tidak_lulus', 'Tidak Lulus'),
            ('cadangan', 'Cadangan')
        ],
        validators=[DataRequired(message="Pilih status kelulusan")])
    
    nilai_akhir = IntegerField('Nilai Akhir',
        validators=[
            Optional(),
            NumberRange(min=0, max=100, message="Nilai harus antara 0-100")
        ])
    
    jurusan_diterima = SelectField('Jurusan Diterima',
        coerce=int,
        validators=[Optional()])
    
    catatan = TextAreaField('Catatan',
        validators=[
            Optional(),
            Length(max=500, message="Catatan maksimal 500 karakter")
        ])
    
    submit = SubmitField('Simpan Hasil')

class EmailBlastForm(FlaskForm):
    """Form untuk kirim email massal"""
    subjek = StringField('Subjek Email',
        validators=[
            DataRequired(message="Subjek email harus diisi"),
            Length(max=200, message="Subjek maksimal 200 karakter")
        ])
    
    konten = TextAreaField('Isi Email',
        validators=[DataRequired(message="Isi email harus diisi")])
    
    tipe_penerima = SelectField('Kirim Ke',
        choices=[
            ('all', 'Semua Pendaftar'),
            ('verified', 'Pendaftar Terverifikasi'),
            ('unverified', 'Pendaftar Belum Terverifikasi'),
            ('lulus', 'Pendaftar Lulus'),
            ('tidak_lulus', 'Pendaftar Tidak Lulus')
        ],
        validators=[DataRequired(message="Pilih tipe penerima")])
    
    lampiran = FileField('Lampiran',
        validators=[
            Optional(),
            FileAllowed(
                ['pdf', 'doc', 'docx'], 
                message='Format file tidak didukung!'
            )
        ])
    
    submit = SubmitField('Kirim Email')

class AdminProfileForm(FlaskForm):
    nama = StringField('Nama Lengkap', validators=[
        DataRequired(message="Nama harus diisi"),
        Length(max=100, message="Nama maksimal 100 karakter")
    ])
    email = EmailField('Email', validators=[
        DataRequired(message="Email harus diisi"),
        Email(message="Format email tidak valid")
    ])
    password = PasswordField('Password Baru', validators=[
        Optional(),
        Length(min=6, message="Password minimal 6 karakter")
    ])
    password_confirm = PasswordField('Konfirmasi Password', validators=[
        Optional(),
        Length(min=6, message="Password minimal 6 karakter")
    ])
    submit = SubmitField('Simpan Perubahan')
