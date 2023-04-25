import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Cart(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'cart'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("products.id"))
    customer = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    product = orm.relationship('Product')