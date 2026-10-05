from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(max=128)])
