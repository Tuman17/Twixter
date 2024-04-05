from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user
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
        user = User(
            username=form.name.data,
            email=form.email.data,
            hashed_password=form.password.data
        )
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
        if user and (user.hashed_password == form.password.data):
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


if __name__ == '__main__':
    global_init("database.db")
    app.run("127.0.0.1", 8080)
