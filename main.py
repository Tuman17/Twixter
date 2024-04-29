from flask import Flask, render_template, redirect, request, flash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.blog import BlogForm
from data.db_session import create_session, global_init
from data.users import User
from data.posts import Posts
from glob import glob
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def main():
    session = create_session()
    posts = session.query(Posts).all()
    return render_template('main.html', title="Twixter - Главная", posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.submit.data:
        if form.password.data != form.password_again.data:
            flash("Пароли не совпадают", "error")
            return render_template('register.html', title='Регистрация', form=form)
        session = create_session()
        if ((session.query(User).filter(User.email == form.email.data).first()) or
                (session.query(User).filter(User.email == form.email.data).first())):
            flash("Такой пользователь уже есть", "error")
            return render_template('register.html', title='Регистрация', form=form)
        user = User()
        user.username = form.name.data
        user.email = form.email.data
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.submit.data:
        session = create_session()
        user = session.query(User).filter(User.username == form.login.data).first()
        if user and (user.check_password(form.password.data)):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        flash('Неправильный логин или пароль', 'error')
        return render_template('login.html', title='Авторизация', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.query(User).get(user_id)


@app.route('/profile')
@login_required
def profile():
    if current_user.is_authenticated:
        return render_template('profile.html', title='Профиль')
    else:
        return redirect('/register')


@app.route("/save_avatar", methods=["POST"])
def save_avatar():
    session = create_session()
    avatar = request.files['avatar']
    if avatar:
        for file in glob(f'static/icons/avatars/{str(current_user.id)}.*'):
            os.remove(file)
        avatar.save(os.path.join("static/icons/avatars", str(current_user.id) + avatar.filename[-4:]))
        user = session.query(User).filter(User.id == current_user.id).first()
        user.avatar = avatar.filename[-4:]
        session.commit()
        current_user.avatar = avatar.filename[-4:]
    return redirect('/rename')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/rename', methods=['GET', 'POST'])
@login_required
def rename():
    form = RegisterForm()

    if request.method == 'GET':
        form.name.data = current_user.username
        form.email.data = current_user.email

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            flash('Пароли не совпадают', 'error')
            return render_template('rename.html', title='Настройки профиля', form=form)
        session = create_session()
        if form.email.data != current_user.email and session.query(User).filter(User.email == form.email.data).first():
            flash('Пользователь с такой почтой уже существует', 'error')
            return render_template('rename.html', title='Настройки профиля', form=form)
        user = session.query(User).filter(User.username == current_user.username).first()
        user.username = form.name.data
        user.email = form.email.data
        user.set_password(form.password.data)
        session.commit()
        login_user(user)
        redirect('/profile')
    return render_template('rename.html', title='Настройки профиля', form=form)


@app.route('/create_blog', methods=['GET', 'POST'])
@login_required
def create_blog():
    form = BlogForm()
    if form.validate_on_submit():
        session = create_session()
        post = Posts()
        post.title = form.title.data
        post.content = form.content.data
        post.user_id = current_user.id
        image = request.files['image']
        if image and image.filename != '':
            for file in glob(f'static/icons/posts/{str(current_user.id)}.*'):
                os.remove(file)
            post.image = image.filename[-4:]
        session.add(post)
        session.commit()
        if post.image:
            image.save(os.path.join("static/icons/posts/", str(post.id) + image.filename[-4:]))
        return redirect('/')
    return render_template('blog.html', title='Создать запись', form=form)


@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    session = create_session()
    post = session.query(Posts).filter(Posts.id == post_id).first()
    session.delete(post)
    session.commit()
    return redirect('/')


if __name__ == '__main__':
    global_init("database.db")
    app.run("127.0.0.1", 8080)
