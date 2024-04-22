from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_uploads import UploadSet, IMAGES

from wtforms import StringField, SubmitField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Length

post_images = UploadSet('images', IMAGES)


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField('Основной текст')
    imgs = MultipleFileField('Прикладываемые файлы', validators=[FileAllowed(post_images, 'wrong'),
                                                                 Length(max=10, message='max 10 files')])
    submit = SubmitField('Опубликовать')
