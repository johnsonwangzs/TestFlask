# -*- encoding: utf-8 -*-
# @auther  : wangzs
# @time    : 2022-11-05
# @file    : main.py.py
# @function: main app

from flask import Flask, render_template, request
from flask_login import login_required, current_user
import logging
from user import user, login_manager  # 导入user蓝图

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s')

app = Flask(__name__)
app.secret_key = b'WzsTestFlask'

urls = [user, ]
for url in urls:
    app.register_blueprint(url)  # 注册蓝图到主app

login_manager.init_app(app)


@app.route('/')
@app.route('/start/', methods=['GET'])
def start():
    if current_user.is_anonymous:
        return render_template('start.html', user_id='访客')
    return render_template('start.html', user_id=current_user.id)


@app.route('/index/', methods=['GET'])
@login_required
def index():
    if request.method == 'GET':
        return render_template('index.html')


if __name__ == "__main__":
    app.run(port=1939, host="127.0.0.1", debug=True)
