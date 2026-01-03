"""
@Author: kang.yang
@Date: 2024/10/8 15:04
"""
import kytest
from kytest.core.hm import Elem


class HmPage(kytest.Page):
    my_entry = Elem('我的入口').locator(text='我的')
    login_entry = Elem('登录/注册按钮').locator(text='登录/注册')
    pwd_login = Elem('账号登录入口').locator(text='账号登录')
    forget_pwd = Elem('忘记密码入口').locator(text='忘记密码')


