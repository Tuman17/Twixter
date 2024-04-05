from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from datetime import datetime
import sqlalchemy


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    register_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now())
    news = sqlalchemy.orm.relationship("Posts", back_populates='user',)
