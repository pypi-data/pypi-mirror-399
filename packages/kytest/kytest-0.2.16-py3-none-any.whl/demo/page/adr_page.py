"""
@Author: kang.yang
@Date: 2024/9/14 09:44
"""
import kytest
from kytest.core.adr import Elem


class HomePage(kytest.Page):
    ad_btn = Elem('广告关闭按钮').locator(description="关闭")
    my_tab = Elem('我的tab入口').locator(text='我的')
    space_tab = Elem('科创空间入口').locator(text='科创空间')


class MyPage(kytest.Page):
    page_title = Elem('页面标题').locator(resourceId='com.qizhidao.clientapp:id/tv_actionbar_title')
    agree_btn = Elem('同意按钮').locator(resourceId='com.qizhidao.clientapp:id/agreement_tv_2')


