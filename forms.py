# -*- encoding: utf-8 -*-
# @auther  : wangzs
# @time    : 2022-11-07
# @file    : forms.py
# @function: WTForms


from wtforms import Form, TextAreaField, StringField
from wtforms.validators import Email, Length, InputRequired, Regexp, ValidationError
import dbutils

mysqldb = dbutils.MysqlUtil()


class UserForm(Form):
    name = TextAreaField('用户名')


class RegisterForm(Form):
    """
    注册表单
    """
    username = StringField(validators=[InputRequired(message="用户名为必填项！")])  # 需检查不可重复！
    password = StringField(validators=[InputRequired(message="密码为必填项！"),
                                       Length(min=8, max=32, message="密码长度需为8~32位！")])
    phone = StringField(validators=[InputRequired(message="手机号为必填项！"),  # 需检查不可重复！
                                    Regexp(r'1(3[0-9]|4[579]|5[0-3,5-9]|6[6]|7[0135678]|8[0-9]|9[89])\d{8}',
                                           message="手机号格式不正确"),
                                    Length(min=11, max=11, message="手机号格式不正确")])
    email = StringField(validators=[InputRequired(message="邮箱为必填项！"),  # 需检查不可重复！
                                    Email(message="邮箱格式不正确！")])

    def validate_username(self, filed):
        """
        保证数据库中username唯一
        :param filed:
        :return:
        """
        cur_username = filed.data
        data = {
            'condition': f'username="{cur_username}"',
            'columns': '*'
        }
        res = mysqldb.exec_sql(op='query', table='user_info', data=data)
        if len(res) > 0:
            raise ValidationError('用户名已存在！')

    def validate_phone(self, filed):
        """
        保证数据库中用户手机号唯一
        :param filed:
        :return:
        """
        cur_phone = filed.data
        data = {
            'condition': f'phone="{cur_phone}"',
            'columns': '*'
        }
        res = mysqldb.exec_sql(op='query', table='user_info', data=data)
        if len(res) > 0:
            raise ValidationError('手机号已被其他用户使用！')

    def validate_email(self, filed):
        """
        保证数据库中用户邮箱唯一
        :param filed:
        :return:
        """
        cur_email = filed.data
        data = {
            'condition': f'email="{cur_email}"',
            'columns': '*'
        }
        res = mysqldb.exec_sql(op='query', table='user_info', data=data)
        if len(res) > 0:
            raise ValidationError('邮箱已被其他用户使用！')
