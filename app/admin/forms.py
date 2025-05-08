from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Optional

class FilterPendaftarForm(FlaskForm):
    jalur = SelectField('Filter Jalur Pendaftaran', choices=[
        ('', 'Semua'), ('zonasi', 'Zonasi'), ('prestasi', 'Prestasi'),
        ('afirmasi', 'Afirmasi'), ('pindahan', 'Pindahan')
    ], validators=[Optional()])
    asal_sekolah = StringField('Filter Asal Sekolah', validators=[Optional()])
    submit = SubmitField('Filter')
