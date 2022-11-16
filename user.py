# -*- encoding: utf-8 -*-
# @auther  : wangzs
# @time    : 2022-11-07
# @file    : user.py.py
# @function: user蓝图

from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import login_required, login_user, logout_user, UserMixin, LoginManager
import logging
import dbutils
from forms import RegisterForm
from datetime import datetime

user = Blueprint('user', __name__)

login_manager = LoginManager()
login_manager.login_view = 'user.login'  # 默认登录页面
login_manager.login_massage = '尚未登陆，即将跳转到登陆页面。'
login_manager.login_message_category = 'info'
login_manager.refresh_view = 'user.reauthenticate'  # 处理fresh login
login_manager.needs_refresh_message = '为保证账号安全，请重新登陆。'
login_manager.needs_refresh_message_category = 'info'
login_manager.session_protection = 'strong'

mysqldb = dbutils.MysqlUtil()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')


class User(UserMixin):
    """
    自定义User类需要实现3个属性和1个方法
    可以继承UserMixin类，使用Flask-Login提供的默认方法
    """
    pass


def query_user(attr_key: str, attr_value: str):
    """
    在数据库中根据某个user属性，查询当前user是否存在
    :param attr_key: 查询所使用的属性
    :param attr_value: 属性值
    :return:
    """
    condition, table = '', ''
    if attr_key == 'user_id':
        condition = f'user_id="{attr_value}"'
        table = 'user_account'
    elif attr_key == 'username':
        condition = f'username="{attr_value}"'
        table = 'user_info'
    if condition != '' and table != '':
        data = {
            'columns': '*',
            'condition': condition
        }
        res = mysqldb.exec_sql(op='query', table=table, data=data)
        if len(res) > 0:
            return res
        return None
    return None


@login_manager.user_loader
def load_user(user_id: str):
    """
    接收唯一的user_id，返回该user_id对应的User对象
    :param user_id: 唯一的user ID。
    :return:
    """
    if query_user('user_id', user_id) is not None:  # 有与此user_id关联的用户记录
        cur_user = User()
        cur_user.id = user_id
        return cur_user
    return None  # user_id不存在时，不能抛出异常，必须返回None


@user.route('/user/login/', methods=['GET', 'POST'])
def login():
    """
    用户登录
    :return:
    """
    if request.method == 'POST':
        username = request.form.get('username')
        query_res = query_user('username', username)
        if query_res is None:  # 用户不存在
            logging.warning('不存在的用户名 %s 尝试登录', username)
            flash('用户不存在！')
            return redirect(url_for('user.login'))
        user_id = query_res[0][0]
        cur_user = query_user('user_id', user_id)
        if request.form.get('password') == cur_user[0][1]:  # 认证通过
            login_user(load_user(user_id))
            logging.info('用户ID %s 成功登录', user_id)
            flash('登陆成功！')
            return redirect(url_for('index'))
        else:  # 口令错误
            logging.warning('用户ID %s 尝试登陆时输入了错误的口令', user_id)
            flash('口令错误！')
        return redirect(url_for('user.login'))
    elif request.method == 'GET':
        return render_template('login.html')


@user.route('/user/logout/')
@login_required
def logout():
    logout_user()
    flash('您已登出。')
    return redirect(url_for('start'))


def reauthenticate():
    """
    fresh login重认证
    :return:
    """
    flash('需要重新登陆！')
    return redirect(url_for('user.login'))


def return_err_message(template, form):
    logging.warning(form.errors)
    err_message = list(form.errors.values())[0][0]
    logging.warning(err_message)
    content = {
        'err_message': err_message
    }
    return render_template(template, **content)


def gen_user_id():
    """
    为新注册用户生成ID
    格式：'yymmddxx'
    :return: 唯一的user_id
    """
    dt = datetime.now()
    cur_date = dt.strftime('%Y%m%d')[2:]
    # 从数据库中获取最大的user_id
    data = {
        'columns': 'max(user_id)',
        'condition': 'user_id is not null'
    }
    res = mysqldb.exec_sql(op='query', table='user_account', data=data)
    max_user_id = res[0][0]
    if max_user_id[6:8] == '99':
        return None
    # 如果user_id是当天产生的，则新的user_id在此之上+1
    if max_user_id[4:6] == cur_date[4:6]:
        # new_user_id = cur_date + str(int(max_user_id[6:8]) + 1)
        new_user_id = cur_date + '%02d' % (int(max_user_id[6:8]) + 1)
        return new_user_id
    # 如果user_id不是当天产生的，则生成当天的第一个user_id
    new_user_id = cur_date + '00'
    return new_user_id


@user.route('/user/register/', methods=['GET', 'POST'])
def register():
    """
    新用户注册
    :return:
    """
    if request.method == 'GET':
        return render_template('register.html')
    else:
        form = RegisterForm(request.form)
        if form.validate():
            logging.info('收到用户提交的注册信息：%s', form.data)
            user_id = gen_user_id()
            if user_id is None:
                flash('抱歉，今日新注册用户已达上限！请明日再来。')
                return redirect(url_for('start'))
            logging.info('为用户生成ID：%s', user_id)
            # 新用户写入数据库
            data_account = {
                'user_id': user_id,
                'password': form.data.get('password'),
            }
            res1 = mysqldb.exec_sql(op='insert', table='user_account', data=data_account)
            data_info = {
                'user_id': user_id,
                'username': form.data.get('username'),
                'phone': form.data.get('phone'),
                'email': form.data.get('email')
            }
            res2 = mysqldb.exec_sql(op='insert', table='user_info', data=data_info)
            if res1 is True and res2 is True:
                flash('注册成功，请登录。')
                logging.info('新用户注册成功，已写入数据库。')
                return redirect(url_for('user.login'))
            else:
                flash('注册失败，请重试！')
                logging.error('新用户注册失败！')
            return redirect(url_for('start'))
        else:
            return return_err_message('register.html', form)
