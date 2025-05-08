from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email harus diisi'),
        Email(message='Format email tidak valid')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password harus diisi')
    ])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    nama_lengkap = StringField('Nama Lengkap', validators=[
        DataRequired(message='Nama lengkap harus diisi'),
        Length(min=3, max=100, message='Nama harus antara 3-100 karakter')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email harus diisi'),
        Email(message='Format email tidak valid')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password harus diisi'),
        Length(min=6, message='Password minimal 6 karakter')
    ])
    password2 = PasswordField('Konfirmasi Password', validators=[
        DataRequired(message='Konfirmasi password harus diisi'),
        EqualTo('password', message='Password tidak cocok')
    ])
    submit = SubmitField('Daftar')