from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class BlogForm(FlaskForm):
    title = StringField('Название', [DataRequired(), Length(min=3, max=36)])
    content = TextAreaField('Содержание')
    submit = SubmitField('Опубликовать')
