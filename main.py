import datetime

from flask_uploads import configure_uploads
from PIL import Image
from data import db_session
from data.users import User
from forms.user import user_images
from forms.user import LoginForm, RegisterForm
from data.posts import Post
from forms.post import post_images
from forms.post import PostForm
from flask import Flask, render_template, redirect, request, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import reqparse, abort, Api, Resource
import os
import shutil

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['UPLOADED_IMAGES_DEST'] = '/users_images'
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
configure_uploads(app, (user_images,))


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return render_template('base.html', title='Лента')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == "POST" and form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first()\
                or db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            nickname=form.nickname.data,
            about=form.about.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()

        os.mkdir(f'static/img/users_images/{user.id}')
        f = form.picture.data
        if not f:
            shutil.copy2('static/img/unknown_avatar_original.png', f'static/img/users_images/{user.id}')
            os.rename(f'static/img/users_images/{user.id}/unknown_avatar_original.png', f'static/img/users_images/{user.id}/avatar_original.png')
            shutil.copy2('static/img/unknown_avatar_scaled_micro.png', f'static/img/users_images/{user.id}')
            os.rename(f'static/img/users_images/{user.id}/unknown_avatar_scaled_micro.png', f'static/img/users_images/{user.id}/avatar_scaled_micro.png')
        else:
            print(f)  # на снос
            f.save(f'static/img/users_images/{user.id}/avatar_original.png')
            new_f = Image.open(f)
            resized_new_f = new_f.resize((30, 30))
            resized_new_f.save(f'static/img/users_images/{user.id}/avatar_scaled_micro.png')
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)  # тыц, там session
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/create_post', methods=['GET', 'POST'])  # создаю запись на стене
def create_post():
    form = PostForm()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            post = Post(
                title=form.title.data,
                text=form.text.data,
                owner=current_user.id,
                likes=0
            )
            db_sess.add(post)
            db_sess.commit()
            imgs = request.files.getlist(form.imgs.name)
            if imgs:
                os.mkdir(f'static/img/posts_images/{post.id}')
                for i, pic in enumerate(imgs):  # не уверен, что так будет работать, потом уточню
                    print(pic)
                    pic.save(f'static/img/posts_images/{post.id}/{i + 1}.{pic.filename.split('.')[-1]}')
            return redirect('/')  # временно, потом будет перекидывать на твой профиль
        return render_template('create_post.html', form=form)
    return render_template('login_required.html', form=form)


def main():
    db_session.global_init("db/pystagramm.db")
    app.run()


if __name__ == '__main__':
    main()
