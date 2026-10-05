from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TelField
from wtforms.validators import DataRequired, Email, Length

class ClienteForm(FlaskForm):
    nombre = StringField('Nombre completo', validators=[DataRequired(), Length(min=4, max=100)])
    correo = EmailField('Correo', validators=[DataRequired(), Email(), Length(max=120)])
    telefono = TelField('Teléfono', validators=[DataRequired(), Length(min=7, max=20)])
    direccion = StringField('Dirección', validators=[DataRequired(), Length(min=5, max=200)])
