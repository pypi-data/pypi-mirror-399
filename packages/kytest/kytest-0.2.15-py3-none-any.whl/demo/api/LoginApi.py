"""
@Author: kang.yang
@Date: 2025/12/9 17:47
"""
from page.web_page import LoginPage


class LoginApi:
    def __init__(self, driver):
        self.lp = LoginPage(driver)

    def pwd_login(self):
        self.lp.goto()
        self.lp.pwd_login.click()
        self.lp.phone_input.input('13652435335')
        self.lp.pwd_input.input('wz123456@QZD')
        self.lp.accept_btn.click()
        self.lp.login_now_btn.click()
        self.lp.first_company_item.click()
