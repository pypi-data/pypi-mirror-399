"""
@Author: kang.yang
@Date: 2024/9/14 09:48
"""
import kytest
from kytest.core.web import Elem


class LoginPage(kytest.Page):
    url = "/login?redirect=https%3A%2F%2Fwww.qizhidao.com%2F&businessSource" \
          "=PC%E7%BB%BC%E5%90%88-%E9%A1%B6%E9%83%A8%E6%A8%A1%E5%9D%97-%E7%AB%8B%E5%8D%B3%E7%99%BB%E5%BD%95&" \
          "registerPage=https%3A%2F%2Fwww.qizhidao.com%2F&fromPage=home"
    login_register = Elem('登录注册按钮').get_by_text('登录/注册', exact=True)
    pwd_login = Elem('密码登录按钮').get_by_text('密码登录')
    phone_input = Elem('手机号输入框').get_by_placeholder('请输入手机号码')
    pwd_input = Elem('密码输入框').get_by_placeholder('请输入密码')
    # accept_btn = Elem('接受选择框').locator("(//span[@class='el-checkbox__inner'])[2]")
    accept_btn = Elem('接受选择框').locator("form div").filter(has_text="我已阅读并同意《企知道平台服务协议》、 《企知道隐私权政策》、 《企知道商城/商贸空间使用须知》").locator("span").nth(3)
    login_now_btn = Elem('立即登录按钮').get_by_role("button", name="立即登录")
    first_company_item = Elem('第一个公司').locator("(//div[@class='company-msg__name'])[1]")

