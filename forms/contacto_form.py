from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Length, Email

class ContactoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=100)])
    correo = EmailField('Correo', validators=[DataRequired(), Email(), Length(max=120)])
    mensaje = TextAreaField('Mensaje', validators=[DataRequired(), Length(min=10, max=2000)])
