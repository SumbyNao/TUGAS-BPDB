from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional

class FilterPendaftarForm(FlaskForm):
    search = StringField('Cari (NISN/Nama)', validators=[Optional()])
    jalur = SelectField('Jalur Pendaftaran', 
                       choices=[
                           ('', 'Semua'),
                           ('Reguler', 'Reguler'),
                           ('Prestasi', 'Prestasi'),
                           ('KIP', 'KIP')
                       ], 
                       validators=[Optional()])
    
    jurusan = SelectField('Jurusan',
                         choices=[
                             ('', 'Semua'),
                             ('RPL', 'Rekayasa Perangkat Lunak'),
                             ('TKJ', 'Teknik Komputer dan Jaringan'),
                             ('MM', 'Multimedia'),
                             ('AKL', 'Akuntansi'),
                             ('BDP', 'Bisnis Daring dan Pemasaran')
                         ],
                         validators=[Optional()])
    
    status = SelectField('Status',
                        choices=[
                            ('', 'Semua'),
                            ('Menunggu', 'Menunggu'),
                            ('Diverifikasi', 'Diverifikasi'),
                            ('Ditolak', 'Ditolak')
                        ],
                        validators=[Optional()])
    
    asal_sekolah = StringField('Asal Sekolah', validators=[Optional()])
    tanggal_awal = DateField('Tanggal Awal', validators=[Optional()])
    tanggal_akhir = DateField('Tanggal Akhir', validators=[Optional()])
    submit = SubmitField('Filter')

class PengumumanForm(FlaskForm):
    """Form untuk manajemen pengumuman"""
    judul = StringField('Judul', 
        validators=[DataRequired(), Length(max=200)])
    
    konten = TextAreaField('Konten', 
        validators=[DataRequired()])
    
    kategori = SelectField('Kategori',
        choices=[
            ('umum', 'Pengumuman Umum'),
            ('pendaftaran', 'Info Pendaftaran'),
            ('hasil', 'Hasil Seleksi'),
            ('daftar_ulang', 'Daftar Ulang')
        ],
        validators=[DataRequired()])
    
    is_published = BooleanField('Publikasikan')
    
    lampiran = FileField('Lampiran (PDF)',
        validators=[FileAllowed(['pdf'], 'File harus dalam format PDF!')])
    
    submit = SubmitField('Simpan Pengumuman')

class VerifikasiBerkasForm(FlaskForm):
    """Form untuk verifikasi berkas pendaftar"""
    status = SelectField('Status Verifikasi',
        choices=[
            ('pending', 'Belum Diverifikasi'),
            ('valid', 'Valid'),
            ('invalid', 'Tidak Valid')
        ],
        validators=[DataRequired()])
    
    catatan = TextAreaField('Catatan',
        validators=[Optional(), Length(max=500)])
    
    submit = SubmitField('Simpan Status')

class VerifikasiPembayaranForm(FlaskForm):
    """Form untuk verifikasi pembayaran pendaftar"""
    status = SelectField('Status Pembayaran',
        choices=[
            ('pending', 'Menunggu Verifikasi'),
            ('valid', 'Pembayaran Valid'),
            ('invalid', 'Pembayaran Tidak Valid')
        ],
        validators=[DataRequired()])
    
    tanggal_verifikasi = DateField('Tanggal Verifikasi',
        validators=[Optional()])
    
    catatan = TextAreaField('Catatan',
        validators=[Optional(), Length(max=500)])
    
    submit = SubmitField('Verifikasi Pembayaran')

class JurusanForm(FlaskForm):
    """Form untuk manajemen jurusan"""
    nama = StringField('Nama Jurusan',
        validators=[DataRequired(), Length(max=100)])
    
    kode = StringField('Kode Jurusan',
        validators=[DataRequired(), Length(max=10)])
    
    deskripsi = TextAreaField('Deskripsi',
        validators=[DataRequired()])
    
    kuota = StringField('Kuota Siswa',
        validators=[DataRequired()])
    
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
        validators=[DataRequired()])
    
    nilai_akhir = StringField('Nilai Akhir',
        validators=[Optional()])
    
    jurusan_diterima = SelectField('Jurusan Diterima',
        coerce=int,
        validators=[Optional()])
    
    catatan = TextAreaField('Catatan',
        validators=[Optional(), Length(max=500)])
    
    submit = SubmitField('Simpan Hasil')

class EmailBlastForm(FlaskForm):
    """Form untuk kirim email massal"""
    subjek = StringField('Subjek Email',
        validators=[DataRequired(), Length(max=200)])
    
    konten = TextAreaField('Isi Email',
        validators=[DataRequired()])
    
    tipe_penerima = SelectField('Kirim Ke',
        choices=[
            ('all', 'Semua Pendaftar'),
            ('verified', 'Pendaftar Terverifikasi'),
            ('unverified', 'Pendaftar Belum Terverifikasi'),
            ('lulus', 'Pendaftar Lulus'),
            ('tidak_lulus', 'Pendaftar Tidak Lulus')
        ],
        validators=[DataRequired()])
    
    lampiran = FileField('Lampiran',
        validators=[Optional(), FileAllowed(['pdf', 'doc', 'docx'], 'Format file tidak didukung!')])
    
    submit = SubmitField('Kirim Email')
