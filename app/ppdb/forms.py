from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, TextAreaField, DateField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError
from app.models import Pendaftar

class FormulirPPDB(FlaskForm):
    nama_lengkap = StringField('Nama Lengkap', 
        validators=[DataRequired(), Length(min=3, max=100)]
    )
    nisn = StringField('NISN', 
        validators=[
            DataRequired(message='NISN harus diisi'), 
            Length(min=10, max=10, message='NISN harus 10 digit'),
            Regexp('^[0-9]*$', message='NISN harus berupa angka')
        ]
    )
    tempat_lahir = StringField('Tempat Lahir', 
        validators=[DataRequired(), Length(max=50)]
    )
    tanggal_lahir = DateField('Tanggal Lahir', 
        validators=[DataRequired()]
    )
    jenis_kelamin = SelectField('Jenis Kelamin',
        choices=[('L', 'Laki-laki'), ('P', 'Perempuan')],
        validators=[DataRequired()]
    )
    agama = SelectField('Agama', 
        choices=[('Islam', 'Islam'), ('Kristen', 'Kristen'), 
                 ('Katolik', 'Katolik'), ('Hindu', 'Hindu'),
                 ('Buddha', 'Buddha'), ('Konghucu', 'Konghucu')],
        validators=[DataRequired()]
    )
    alamat = TextAreaField('Alamat Lengkap',
        validators=[DataRequired(), Length(min=10, max=200)]
    )
    no_hp = StringField('Nomor HP', 
        validators=[DataRequired()]
    )
    asal_sekolah = StringField('Asal Sekolah',
        validators=[DataRequired(), Length(max=100)]
    )
    nilai_un = DecimalField('Nilai Rata-rata UN', 
        validators=[DataRequired()]
    )
    jurusan_pilihan = SelectField('Jurusan Pilihan',
        choices=[('RPL', 'Rekayasa Perangkat Lunak'),
                 ('TKJ', 'Teknik Komputer dan Jaringan'),
                 ('MM', 'Multimedia'),
                 ('AKL', 'Akuntansi dan Keuangan Lembaga'),
                 ('BDP', 'Bisnis Daring dan Pemasaran')],
        validators=[DataRequired()]
    )
    jalur_pendaftaran = SelectField('Jalur Pendaftaran',
        choices=[('Reguler', 'Reguler'),
                 ('Prestasi', 'Prestasi'),
                 ('KIP', 'KIP')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Kirim Formulir')

    def validate_nisn(self, field):
        pendaftar = Pendaftar.query.filter_by(nisn=field.data).first()
        if pendaftar:
            raise ValidationError('NISN sudah terdaftar.')

class UploadBerkasForm(FlaskForm):
    kartu_keluarga = FileField('Kartu Keluarga',
        validators=[
            FileRequired(),
            FileAllowed(['pdf', 'jpg', 'png'], 'File harus berupa PDF atau gambar!')
        ]
    )
    akta_kelahiran = FileField('Akta Kelahiran',
        validators=[
            FileRequired(),
            FileAllowed(['pdf', 'jpg', 'png'], 'File harus berupa PDF atau gambar!')
        ]
    )
    rapor = FileField('Rapor',
        validators=[
            FileRequired(),
            FileAllowed(['pdf', 'jpg', 'png'], 'File harus berupa PDF atau gambar!')
        ]
    )
    surat_keterangan = FileField('Surat Keterangan',
        validators=[
            FileRequired(),
            FileAllowed(['pdf', 'jpg', 'png'], 'File harus berupa PDF atau gambar!')
        ]
    )
    submit = SubmitField('Upload Berkas')
