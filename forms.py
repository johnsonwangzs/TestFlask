# -*- encoding: utf-8 -*-
# @auther  : wangzs
# @time    : 2022-11-07
# @file    : forms.py
# @function: WTForms


from flask_wtf import Form
from wtforms import TextAreaField


class UserForm(Form):
    name = TextAreaField('用户名')
