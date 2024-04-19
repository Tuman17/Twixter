from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from forms.register import RegisterForm
from forms.login import LoginForm
from data.db_session import create_session, global_init
from data.users import User
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
@app.route('/main')
def main():
    return render_template('header.html', title="Twixter - Главная")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.submit.data:
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
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
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and (user.check_password(form.password.data)):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.query(User).get(user_id)


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Профиль')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/rename', methods=['GET', 'POST'])
def rename():
    form = RegisterForm()
    if form.submit.data:
        if form.password.data != form.password_again.data:
            return render_template('rename.html', title='Настройки профиля',
                                   form=form, message='Пароли не совпадают')
        session = create_session()
        if form.email.data != current_user.email and session.query(User).filter(User.email == form.email.data).first():
            return render_template('rename.html', title='Настройки профиля',
                                   form=form, message='Пользователь с такой почтой уже существует')
        user = session.query(User).filter(User.username == current_user.username).first()
        user.username = form.name.data
        user.email = form.name.data
        user.set_password(form.password.data)
        session.commit()
        return redirect('/profile')
    return render_template('rename.html', title='Настройки профиля', form=form)


if __name__ == '__main__':
    global_init("database.db")
    app.run("127.0.0.1", 8080)
