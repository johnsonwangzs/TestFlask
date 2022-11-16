# -*- encoding: utf-8 -*-
# @auther  : wangzs
# @time    : 2022-11-06
# @file    : test.py
# @function:

from datetime import datetime

string = 'INSERT INTO user_account(user_id, password) VALUES (%s, %s)'
print(string%('a', 'b'))
