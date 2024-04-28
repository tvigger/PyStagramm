from requests import delete

from flask import Flask, render_template, redirect, request, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
from flask_uploads import configure_uploads

from PIL import Image

from data import db_session
from data.users import User
from data.posts import Post
from data.comments import Comment
from data.subscribes import Subscribe
from data.post_resourses import PostResource, PostsListResource
from data.user_resourses import UsersResource, UsersListResource
from data.comment_resourses import CommentResource, CommentsListResource

from forms.user import user_images, LoginForm, RegisterForm
from forms.post import PostForm
from forms.login_required import LogReqForm
from forms.comment import CommentForm

import os
import shutil

from config import *

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['UPLOADED_IMAGES_DEST'] = '/users_images'
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
configure_uploads(app, (user_images,))


def main():
    db_session.global_init("db/pystagramm.db")
    api.add_resource(PostsListResource, '/api/posts')
    api.add_resource(PostResource, '/api/posts/<int:post_id>')
    api.add_resource(UsersListResource, '/api/users')
    api.add_resource(UsersResource, '/api/users/<int:user_id>')
    api.add_resource(CommentsListResource, '/api/comments')
    api.add_resource(CommentResource, '/api/comments/<int:comment_id>')
    app.run(port=PORT, host=HOST)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    db_sess = db_session.create_session()
    posts = db_sess.query(Post).order_by(-Post.id)
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
            pos = Post(
                title=form.title.data,
                text=form.text.data,
                owner=current_user.id
            )
            db_sess.add(pos)
            db_sess.commit()
            imgs = form.imgs.data
            c = 0
            os.mkdir(f'static/img/posts_images/{pos.id}')
            for i, pic in enumerate(imgs):
                _ = pic.filename
                if _:
                    pic.save(f'static/img/posts_images/{pos.id}/{i + 1}.png')
                    c += 1
            pos.img_amount = c
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
    if request.method == 'GET':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nickname == nickname).first()
        if user:
            posts = db_sess.query(Post).filter(Post.user == user).order_by(-Post.id).all()
            followers = [x.follower for x in (db_sess.query(Subscribe).filter(Subscribe.following == user.id).all())]
            return render_template('profile.html', user=user, posts=posts,
                                   title=user.nickname, followers=followers)
        else:
            abort(404)
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nickname == nickname).first()
        followers = [x.follower for x in (db_sess.query(Subscribe).filter(Subscribe.following == user.id).all())]
        if current_user.id in followers:
            sub = db_sess.query(Subscribe).filter(Subscribe.following == user.id,
                                                  Subscribe.follower == current_user.id).first()
            db_sess.delete(sub)
            db_sess.commit()
        elif current_user.nickname != nickname:
            sub = Subscribe(
                follower=current_user.id,
                following=user.id
            )
            db_sess.add(sub)
            db_sess.commit()
        else:
            return redirect(f'/delete_user/{user.id}')
        return redirect(f'/{nickname}')


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
    pos = db_sess.query(Post).filter(Post.id == post_id).first()
    comments = db_sess.query(Comment).filter(Comment.under == post_id).order_by(-Comment.id)
    return render_template('post.html', post=pos, comments=comments, form=form)


@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    if current_user.is_authenticated:
        if request.method == 'GET':
            return render_template('submit_delete.html')
        else:
            logout_user()
            delete(f'http://{HOST}:{PORT}/api/users/{user_id}')
            return redirect('/')
    else:
        form = LogReqForm()
        return render_template('login_required.html', form=form)


@app.route('/delete_post/<int:post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    if current_user.is_authenticated:
        if request.method == 'GET':
            return render_template('submit_delete.html')
        else:
            delete(f'http://{HOST}:{PORT}/api/posts/{post_id}')
            return redirect(f'/{current_user.nickname}')
    else:
        form = LogReqForm()
        return render_template('login_required.html', form=form)


@app.route('/delete_comment/<int:comment_id>')
def delete_comment(comment_id):
    sess = db_session.create_session()
    cur_post = sess.query(Comment).get(comment_id).under
    delete(f'http://{HOST}:{PORT}/api/comments/{comment_id}')
    return redirect(f'/posts/{cur_post}')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    main()
