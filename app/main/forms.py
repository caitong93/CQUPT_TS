# -*- coding:utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddNameForm(Form):
    name = StringField(u'name', validators=[DataRequired()])
    submit = SubmitField('Add')