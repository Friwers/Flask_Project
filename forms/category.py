from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import DataRequired

class CategoryForms(FlaskForm):
    title = StringField('Название', validators=[DataRequired()], render_kw={"placeholder": "Title"})
    submit = SubmitField('Сохранить')