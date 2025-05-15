from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional, ValidationError
from app.models import Pendaftaran  

class FormulirPPDB(FlaskForm):
    nisn = StringField('NISN', 
        validators=[
            DataRequired(message='NISN harus diisi'), 
            Length(min=10, max=10, message='NISN harus 10 digit')
        ]
    )
    nik = StringField('NIK', 
        validators=[
            DataRequired(message='NIK harus diisi'), 
            Length(min=16, max=16, message='NIK harus 16 digit')
        ]
    )
    nama_lengkap = StringField('Nama Lengkap', 
        validators=[
            DataRequired(message='Nama lengkap harus diisi'),
            Length(min=3, max=100, message='Nama harus antara 3-100 karakter')
        ]
    )
    jenis_kelamin = SelectField('Jenis Kelamin', 
                              choices=[('L', 'Laki-laki'), ('P', 'Perempuan')],
                              validators=[DataRequired(message='Jenis kelamin harus dipilih')]
    )
    tempat_lahir = StringField('Tempat Lahir', 
        validators=[
            DataRequired(message='Tempat lahir harus diisi'),
            Length(max=50, message='Tempat lahir maksimal 50 karakter')
        ]
    )
    tanggal_lahir = DateField('Tanggal Lahir', 
        validators=[DataRequired(message='Tanggal lahir harus diisi')]
    )
    agama = SelectField('Agama', 
                       choices=[
                           ('Islam', 'Islam'),
                           ('Kristen', 'Kristen'),
                           ('Katolik', 'Katolik'),
                           ('Hindu', 'Hindu'),
                           ('Buddha', 'Buddha'),
                           ('Konghucu', 'Konghucu')
                       ],
                       validators=[DataRequired(message='Agama harus dipilih')]
    )
    alamat = TextAreaField('Alamat', 
        validators=[
            DataRequired(message='Alamat harus diisi'),
            Length(min=10, max=200, message='Alamat harus antara 10-200 karakter')
        ]
    )
    rt = StringField('RT', 
        validators=[
            DataRequired(message='RT harus diisi'),
            Length(max=3, message='RT maksimal 3 karakter')
        ]
    )
    rw = StringField('RW', 
        validators=[
            DataRequired(message='RW harus diisi'),
            Length(max=3, message='RW maksimal 3 karakter')
        ]
    )
    kelurahan = StringField('Kelurahan/Desa', 
        validators=[
            DataRequired(message='Kelurahan/Desa harus diisi')
        ]
    )
    kecamatan = StringField('Kecamatan', 
        validators=[
            DataRequired(message='Kecamatan harus diisi')
        ]
    )
    kota = StringField('Kota/Kabupaten', 
        validators=[
            DataRequired(message='Kota/Kabupaten harus diisi')
        ]
    )
    kode_pos = StringField('Kode Pos', 
        validators=[
            DataRequired(message='Kode Pos harus diisi'),
            Length(max=5, message='Kode Pos maksimal 5 karakter')
        ]
    )
    no_hp = StringField('No. HP', 
        validators=[
            DataRequired(message='Nomor HP harus diisi'),
            Length(max=15, message='Nomor HP maksimal 15 karakter')
        ]
    )
    
    nama_ayah = StringField('Nama Ayah', 
        validators=[
            DataRequired(message='Nama Ayah harus diisi')
        ]
    )
    pekerjaan_ayah = StringField('Pekerjaan Ayah', 
        validators=[
            DataRequired(message='Pekerjaan Ayah harus diisi')
        ]
    )
    nama_ibu = StringField('Nama Ibu', 
        validators=[
            DataRequired(message='Nama Ibu harus diisi')
        ]
    )
    pekerjaan_ibu = StringField('Pekerjaan Ibu', 
        validators=[
            DataRequired(message='Pekerjaan Ibu harus diisi')
        ]
    )
    no_hp_ortu = StringField('No. HP Orang Tua', 
        validators=[
            DataRequired(message='Nomor HP Orang Tua harus diisi'),
            Length(max=15, message='Nomor HP Orang Tua maksimal 15 karakter')
        ]
    )
    
    asal_sekolah = StringField('Asal Sekolah', 
        validators=[
            DataRequired(message='Asal sekolah harus diisi')
        ]
    )
    npsn_sekolah = StringField('NPSN Sekolah', 
        validators=[
            DataRequired(message='NPSN sekolah harus diisi'),
            Length(max=8, message='NPSN sekolah maksimal 8 karakter')
        ]
    )
    jurusan = SelectField('Pilihan Jurusan', 
        validators=[DataRequired(message='Jurusan harus dipilih')]
    )
    jalur_pendaftaran = SelectField('Jalur Pendaftaran',
                                  choices=[
                                      ('Reguler', 'Reguler'),
                                      ('Prestasi', 'Prestasi'),
                                      ('KIP', 'KIP')
                                  ],
                                  validators=[DataRequired(message='Jalur pendaftaran harus dipilih')]
    )
    submit = SubmitField('Simpan')

class UploadBerkasForm(FlaskForm):
    berkas = FileField('Pilih Berkas', 
                      validators=[
                          FileRequired(message='File harus dipilih'),
                          FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'File harus berupa PDF atau gambar!')
                      ]
    )
    submit = SubmitField('Upload')

class PembayaranForm(FlaskForm):
    bukti_pembayaran = FileField('Upload Bukti Pembayaran',
                                validators=[
                                    FileRequired(message='File harus dipilih'),
                                    FileAllowed(['jpg', 'jpeg', 'png'], 'File harus berupa gambar!')
                                ]
    )
    submit = SubmitField('Upload Bukti Pembayaran')
