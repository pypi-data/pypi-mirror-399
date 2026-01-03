"""
@Author: kang.yang
@Date: 2023/11/16 17:50
"""
import kytest
from kytest.core.web import TC
from api.LoginApi import LoginApi


@kytest.story('登录')
class TestNormalSearch(TC):
    def start(self):
        self.la = LoginApi(self.dr)

    @kytest.title("账号密码登录")
    def test_normal_search(self):
        self.la.pwd_login()
        self.sleep(10)






