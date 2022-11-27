from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,
                     RadioField, SubmitField)
from wtforms.validators import InputRequired, Length


class AddressForm(FlaskForm):
    post_code = StringField('Post Code', validators=[InputRequired()])

    submit = SubmitField('Submit')