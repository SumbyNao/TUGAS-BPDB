from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class ContactForm(FlaskForm):
    """Form untuk halaman kontak"""
    nama = StringField('Nama Lengkap', 
        validators=[DataRequired(), Length(min=3, max=100)])
    
    email = StringField('Email',
        validators=[DataRequired(), Email()])
    
    no_hp = StringField('Nomor HP',
        validators=[DataRequired(), Length(min=10, max=15)])
    
    pesan = TextAreaField('Pesan',
        validators=[DataRequired(), Length(min=10, max=1000)])
    
    submit = SubmitField('Kirim Pesan')