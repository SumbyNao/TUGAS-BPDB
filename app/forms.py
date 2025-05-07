from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length

# ----------------------------
# FORM LOGIN
# ----------------------------
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Masuk')

# ----------------------------
# FORM REGISTRASI AKUN (USER)
# ----------------------------
class RegisterForm(FlaskForm):
    nama_lengkap = StringField('Nama Lengkap', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6),
        EqualTo('confirm_password', message='Password harus cocok')
    ])
    confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired()])
    submit = SubmitField('Daftar')

# ----------------------------
# FORMULIR PENDAFTARAN PPDB
# ----------------------------
class FormulirPPDB(FlaskForm):
    nama_lengkap = StringField('Nama Lengkap', validators=[DataRequired()])
    nisn = StringField('NISN', validators=[DataRequired(), Length(min=10, max=10)])
    tempat_lahir = StringField('Tempat Lahir', validators=[DataRequired()])
    tanggal_lahir = DateField('Tanggal Lahir', format='%Y-%m-%d', validators=[DataRequired()])
    jenis_kelamin = SelectField('Jenis Kelamin', choices=[('L', 'Laki-laki'), ('P', 'Perempuan')], validators=[DataRequired()])
    alamat = TextAreaField('Alamat Lengkap', validators=[DataRequired()])
    asal_sekolah = StringField('Asal Sekolah', validators=[DataRequired()])
    jalur_pendaftaran = SelectField('Jalur Pendaftaran', choices=[
        ('zonasi', 'Zonasi'), ('prestasi', 'Prestasi'), ('afirmasi', 'Afirmasi'), ('pindahan', 'Pindahan')
    ], validators=[DataRequired()])
    submit = SubmitField('Kirim Formulir')

# ----------------------------
# FORM UPLOAD BERKAS
# ----------------------------
class UploadBerkasForm(FlaskForm):
    kartu_keluarga = FileField('Scan Kartu Keluarga', validators=[DataRequired()])
    akta_kelahiran = FileField('Scan Akta Kelahiran', validators=[DataRequired()])
    rapor = FileField('Scan Nilai Rapor', validators=[DataRequired()])
    surat_keterangan = FileField('Surat Keterangan dari Sekolah', validators=[DataRequired()])
    submit = SubmitField('Upload Berkas')
