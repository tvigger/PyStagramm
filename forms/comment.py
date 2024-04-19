from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    text = TextAreaField('Ваше мнение', validators=[DataRequired()])
    submit = SubmitField('Прокомментировать')
