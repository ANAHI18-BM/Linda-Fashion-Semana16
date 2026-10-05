from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TelField
from wtforms.validators import DataRequired, Email, Length

class ProveedorForm(FlaskForm):
    nombre = StringField('Nombre del proveedor', validators=[DataRequired(), Length(min=3, max=100)])
    correo = EmailField('Correo', validators=[DataRequired(), Email(), Length(max=120)])
    telefono = TelField('Teléfono', validators=[DataRequired(), Length(min=7, max=20)])
    producto = StringField('Producto o servicio que provee', validators=[DataRequired(), Length(min=3, max=150)])
