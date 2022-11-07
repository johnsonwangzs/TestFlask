# -*- encoding: utf-8 -*-
# @auther  : wangzs
# @time    : 2022-11-05
# @file    : main.py.py
# @function:

from flask import Flask, render_template, session, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, logout_user, login_user, current_user
import dbutils
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

app = Flask(__name__)
app.secret_key = b'WzsTestFlask'

login_manager = LoginManager()
login_manager.login_view = 'login'  # 默认登录页面
login_manager.login_massage = '尚未登陆，即将跳转到登陆页面。'
login_manager.login_message_category = 'info'
login_manager.refresh_view = 'reauthenticate'  # 处理fresh login
login_manager.needs_refresh_message = '为保证账号安全，请重新登陆。'
login_manager.needs_refresh_message_category = 'info'
login_manager.session_protection = 'strong'
login_manager.init_app(app)


class User(UserMixin):
    """
    自定义User类需要实现3个属性和1个方法
    可以继承UserMixin类，使用Flask-Login提供的默认方法
    """
    pass


def query_user(user_id:str):
    """
    在数据库中查询当前user_id是否存在
    :param user_id: user_id
    :return:
    """
    condition = f'user_id="{user_id}"'
    data = {
        'condition': condition
    }
    res = mysqldb.exec_sql(op='query', table='user', data=data)
    if len(res) > 0:
        return res
    return None


@login_manager.user_loader
def load_user(user_id:str):
    """
    接收唯一的userid，返回该userid对应的User对象
    :param user_id: 唯一的user ID。
    :return:
    """
    if query_user(user_id) is not None:  # 有与此user_id关联的用户记录
        cur_user = User()
        cur_user.id = user_id
        return cur_user
    return None  # user_id不存在时，不能抛出异常，必须返回None


@app.route('/')
@app.route('/start', methods=['GET'])
def start():
    return render_template('start.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('userid')
        user = query_user(user_id)
        if user is not None:
            if request.form.get('password') == user[0][1]:  # 认证通过
                login_user(load_user(user_id))
                return redirect(url_for('index'))
            else:  # 口令错误
                logging.warning('用户ID %s 尝试登陆时输入了错误的口令', user_id)
        else:  # 用户不存在
            logging.warning('不存在的用户ID %s 尝试登录', user_id)
    return render_template('login.html')


@app.route('/index', methods=['GET'])
@login_required
def index():
    if request.method == 'GET':
        return render_template('index.html')


def reauthenticate():
    """
    fresh login重认证
    :return:
    """
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('start'))


if __name__ == "__main__":
    mysqldb = dbutils.MysqlUtil()
    app.run(port=1939, host="127.0.0.1", debug=True)
