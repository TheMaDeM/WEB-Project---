from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, IntegerField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class AdsForm1(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    price = IntegerField('Цена (в руб)', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    image = FileField('Изображение', validators=[DataRequired()])
    submit = SubmitField('Выложить')


class AdsForm2(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    price = IntegerField('Цена (в руб)', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    submit = SubmitField('Выложить')