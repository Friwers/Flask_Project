import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Cart(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'cart'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # название товара
    manufacturer_id = sqlalchemy.Column(sqlalchemy.String,
                                        sqlalchemy.ForeignKey("users.id"))
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.String,nullable=False)
    customer = sqlalchemy.Column(sqlalchemy.String, nullable=False)