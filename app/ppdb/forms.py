from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

class FormulirPPDB(FlaskForm):
    nama_lengkap = StringField('Nama Lengkap', 
        validators=[DataRequired(), Length(min=3, max=100)]
    )
    nisn = StringField('NISN', 
        validators=[
            DataRequired(), 
            Length(min=10, max=10),
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
    alamat = TextAreaField('Alamat Lengkap',
        validators=[DataRequired(), Length(min=10, max=200)]
    )
    asal_sekolah = StringField('Asal Sekolah',
        validators=[DataRequired(), Length(max=100)]
    )
    jalur_pendaftaran = SelectField('Jalur Pendaftaran',
        choices=[
            ('prestasi', 'Jalur Prestasi'),
            ('zonasi', 'Jalur Zonasi'),
            ('afirmasi', 'Jalur Afirmasi')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Kirim Formulir')

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
