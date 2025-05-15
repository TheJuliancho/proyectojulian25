from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length

class ComentarioForm(FlaskForm):
    contenido = TextAreaField(
        'Tu comentario',
        validators=[DataRequired(), Length(max=500)]
    )
    
    calificacion = RadioField(
        'Calificación',
        choices=[('1', '1 estrella'), ('2', '2 estrellas'), ('3', '3 estrellas'), ('4', '4 estrellas'), ('5', '5 estrellas')],
        validators=[DataRequired()]
    )
    
    submit = SubmitField('Publicar')
