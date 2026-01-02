"""
@Author: kang.yang
@Date: 2024/10/8 15:04
"""
import kytest
from kytest.core.hm import Elem


class HmPage(kytest.Page):
    my_entry = Elem(
        tag='首页底部我的入口',
        text='我的'
    )
    login_entry = Elem(
        tag='登录页登录/注册按钮',
        text='登录/注册'
    )
    pwd_login = Elem(
        tag='账号登录入口',
        text='账号登录'
    )
    forget_pwd = Elem(
        tag='忘记密码入口',
        text='忘记密码'
    )

