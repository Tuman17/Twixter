from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, InputRequired, Email, Length


class RegisterForm(FlaskForm):
    name = StringField('Имя пользователя', [DataRequired(), Length(min=3, max=18)])
    email = EmailField('Почта', [Email(), Length(min=6, max=28)])
    password = PasswordField('Пароль', [InputRequired(), Length(min=6, max=28)])
    password_again = PasswordField('Повторите пароль', [InputRequired(), Length(min=6, max=28)])
    submit = SubmitField('Зарегистрироваться')
