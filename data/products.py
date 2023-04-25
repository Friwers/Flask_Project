import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Product(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # название товара
    manufacturer_id = sqlalchemy.Column(sqlalchemy.Integer,
                                        sqlalchemy.ForeignKey("users.id"))
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # цена товара
    about = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # описание товара
    image = sqlalchemy.Column(sqlalchemy.String)  # изображение товара (если есть)
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # кол-во товаров
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.strptime(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "%d/%m/%Y %H:%M:%S"))  # дата изменения

    categories = orm.relationship("Category",
                                  secondary="association",
                                  backref="products") # категория товара
    cart = orm.relationship("Cart", back_populates='product')

    manufacturer = orm.relationship('User')
