from .login_form import LoginForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp

class UsuarioForm(LoginForm):
    usuario = StringField("Usuario", validators=[DataRequired(), Length(min=3, max=50), Regexp(r"^[A-Za-z0-9_.-]+$", message="Usa letras, números, puntos, guiones o guion bajo, sin espacios.")])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8, max=128)])
    confirmacion = PasswordField('Repetir contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas no coinciden.')])
