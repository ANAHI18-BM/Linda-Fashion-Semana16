from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange

class ProductoForm(FlaskForm):
    nombre = StringField(
        "Nombre de la prenda",
        validators=[DataRequired(message="El nombre de la prenda es obligatorio."),
                    Length(min=4, max=150, message="El nombre debe tener al menos 4 caracteres.")]
    )
    categoria = SelectField(
        "Categoría",
        choices=[
            ("", "Seleccione una categoría"),
            ("Vestidos", "Vestidos"),
            ("Blusas", "Blusas"),
            ("Jeans", "Jeans"),
            ("Conjuntos", "Conjuntos"),
            ("Accesorios", "Accesorios"),
            ("Camisas", "Camisas"), ("Shorts", "Shorts"), ("Faldas", "Faldas"),
        ],
        validators=[DataRequired(message="Debe seleccionar una categoría.")]
    )
    descripcion = TextAreaField(
        "Descripción",
        validators=[DataRequired(message="La descripción es obligatoria."),
                    Length(min=10, max=2000, message="La descripción debe tener al menos 10 caracteres.")]
    )
    talla = SelectField(
        "Talla",
        choices=[
            ("", "Seleccione una talla"),
            ("XS", "XS"), ("S", "S"), ("M", "M"), ("L", "L"), ("XL", "XL"), ("P", "P"), ("G", "G")
        ],
        validators=[DataRequired(message="Debe seleccionar una talla.")]
    )
    precio = DecimalField(
        "Precio ($)",
        places=2,
        validators=[DataRequired(message="El precio es obligatorio."),
                    NumberRange(min=0.01, max=9999999999.99, message="El precio debe ser mayor a 0.")]
    )
    estado = SelectField(
        "Estado",
        choices=[
            ("", "Seleccione el estado"),
            ("Disponible", "Disponible"),
            ("Agotado", "Agotado"),
            ("Próximamente", "Próximamente"),
        ],
        validators=[DataRequired(message="Debe seleccionar el estado de la prenda.")]
    )

    proveedor_id = SelectField("Proveedor", coerce=int, validators=[DataRequired()])

    imagen = SelectField("Fotografía de la prenda", choices=[], default="")

    foto = FileField("Subir fotografía nueva (opcional)", validators=[FileAllowed(["jpg","jpeg","png","webp"], "Usa JPG, PNG o WebP.")])
