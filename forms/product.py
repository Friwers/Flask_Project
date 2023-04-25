from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectMultipleField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()], render_kw={"placeholder": "Title"})
    price = IntegerField('Цена', validators=[DataRequired()])
    about = TextAreaField("О товаре", validators=[DataRequired()])
    count = IntegerField('Кол-во', validators=[DataRequired()])
    category = SelectMultipleField("Категория", coerce=int, validators=[DataRequired()])
    submit = SubmitField('Сохранить')