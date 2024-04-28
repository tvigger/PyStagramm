import datetime

from flask import Flask, render_template, redirect, request, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
from flask_uploads import configure_uploads

from PIL import Image

from data import db_session
from data.users import User
from data.posts import Post
from data.comments import Comment
from data.post_resourses import PostResource, PostsListResource
from data.user_resourses import UsersResource, UsersListResource
from data.comment_resourses import CommentResource, CommentsListResource

from forms.user import user_images, LoginForm, RegisterForm
from forms.post import PostForm, post_images
from forms.login_required import LogReqForm
from forms.comment import CommentForm

import os
import shutil

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['UPLOADED_IMAGES_DEST'] = '/users_images'
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
configure_uploads(app, (user_images,))
forbidden_nicknames = ['register', 'login', 'logout', 'create_post', 'posts']


def main():
    db_session.global_init("db/pystagramm.db")
    api.add_resource(PostsListResource, '/api/posts')
    api.add_resource(PostResource, '/api/posts/<int:post_id>')
    api.add_resource(UsersListResource, '/api/users')
    api.add_resource(UsersResource, '/api/users/<int:user_id>')
    api.add_resource(CommentsListResource, '/api/comments')
    api.add_resource(CommentResource, '/api/comments/<int:comment_id>')
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).all()
    return render_template('index.html', title='Лента', posts=posts)


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
                or db_sess.query(User).filter(User.nickname == form.nickname.data).first()\
                or form.nickname.data in forbidden_nicknames:
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
            os.rename(f'static/img/users_images/{user.id}/unknown_avatar_original.png',
                      f'static/img/users_images/{user.id}/avatar_original.png')
            shutil.copy2('static/img/unknown_avatar_scaled_micro.png', f'static/img/users_images/{user.id}')
            os.rename(f'static/img/users_images/{user.id}/unknown_avatar_scaled_micro.png',
                      f'static/img/users_images/{user.id}/avatar_scaled_micro.png')
        else:
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
    if current_user.is_authenticated:
        form = PostForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            post = Post(
                title=form.title.data,
                text=form.text.data,
                owner=current_user.id
            )
            db_sess.add(post)
            db_sess.commit()
            imgs = request.files.getlist(form.imgs.name)
            c = 0
            if imgs:
                os.mkdir(f'static/img/posts_images/{post.id}')
                for i, pic in enumerate(imgs):
                    pic.save(f'static/img/posts_images/{post.id}/{i + 1}.png')
                    c += 1
            post.img_amount = c
            db_sess.commit()
            return redirect(f'/{current_user.nickname}')
        return render_template('create_post.html', form=form, title='Создание публикации')
    else:
        form = LogReqForm()
        if form.validate_on_submit():
            return redirect('/')
        return render_template('login_required.html', form=form)


@app.route('/<nickname>', methods=['GET', 'POST'])
def profile(nickname):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.nickname == nickname).first()
    if user:
        posts = db_sess.query(Post).filter(Post.user == user).all()
        return render_template('profile.html', user=user, posts=posts, title=user.nickname)
    else:
        abort(404)


@app.route('/posts/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comment = Comment(
            under=post_id,
            publisher=current_user.id,
            text=form.text.data
        )
        db_sess.add(comment)
        db_sess.commit()
        return redirect(f'/posts/{post_id}')
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == post_id).first()
    comments = db_sess.query(Comment).filter(Comment.under == post_id).order_by(-Comment.id)
    return render_template('post.html', post=post, comments=comments, form=form)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    main()
