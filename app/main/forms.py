from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class ContactForm(FlaskForm):
    nama = StringField(
        'Nama Lengkap', 
        validators=[
            DataRequired(message="Nama harus diisi"), 
            Length(max=100, message="Nama maksimal 100 karakter")
        ]
    )
    
    email = EmailField(
        'Email',
        validators=[
            DataRequired(message="Email harus diisi"), 
            Email(message="Format email tidak valid")
        ]
    )
    
    no_hp = StringField(
        'No. HP',
        validators=[
            DataRequired(message="No. HP harus diisi"), 
            Length(max=20, message="No. HP maksimal 20 karakter")
        ]
    )
    
    subject = StringField(
        'Subjek', 
        validators=[
            DataRequired(message="Subjek harus diisi"), 
            Length(max=200, message="Subjek maksimal 200 karakter")
        ]
    )
    
    pesan = TextAreaField(
        'Pesan',
        validators=[
            DataRequired(message="Pesan harus diisi"), 
            Length(max=1000, message="Pesan maksimal 1000 karakter")
        ]
    )
    
    submit = SubmitField('Kirim Pesan')
