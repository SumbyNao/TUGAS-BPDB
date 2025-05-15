from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email harus diisi'),
        Email(message='Format email tidak valid')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password harus diisi')
    ])
    remember_me = BooleanField('Ingat Saya')  # Added remember me option
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    nama_lengkap = StringField('Nama Lengkap', validators=[
        DataRequired(message='Nama lengkap harus diisi'),
        Length(min=3, max=100, message='Nama harus antara 3-100 karakter'),
        Regexp(r'^[\w\s-]+$', message='Nama hanya boleh mengandung huruf, angka, dan spasi')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email harus diisi'),
        Email(message='Masukkan email yang valid'),
        Length(max=120, message='Email terlalu panjang')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password harus diisi'),
        Length(min=6, message='Password minimal 6 karakter'),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', 
               message='Password harus mengandung minimal 1 huruf dan 1 angka')
    ])
    confirm_password = PasswordField('Konfirmasi Password', validators=[
        DataRequired(message='Konfirmasi password harus diisi'),
        EqualTo('password', message='Password harus sama')
    ])
    submit = SubmitField('Daftar')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email sudah terdaftar. Silakan gunakan email lain.')
    
    def validate_nama_lengkap(self, nama_lengkap):
        if len(nama_lengkap.data.split()) < 2:
            raise ValidationError('Nama lengkap harus terdiri dari minimal 2 kata')