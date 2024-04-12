from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from flask_uploads import UploadSet, IMAGES
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash

user_images = UploadSet('images', IMAGES)


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия')
    nickname = StringField('Псевдоним', validators=[DataRequired(), Length(min=4, max=100)])
    picture = FileField('Фотография профиля', validators=[FileAllowed(user_images, 'wrong')])
    about = TextAreaField('О себе')
    email = EmailField('Адрес электронной почты', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повтор пароля', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
