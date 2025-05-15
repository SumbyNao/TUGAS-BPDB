from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField
from wtforms.validators import Optional

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
