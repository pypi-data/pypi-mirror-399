"""
@Author: kang.yang
@Date: 2024/9/14 09:44
"""
import kytest
from kytest.core.adr import Elem


class AdrPage(kytest.Page):
    ad_btn = Elem(
        tag='首页广告关闭按钮',
        rid='id/bottom_btn'
    )
    my_tab = Elem(
        tag='首页底部我的tab入口',
        xpath='//android.widget.FrameLayout[4]'
    )
    space_tab = Elem(
        tag='首页底部科创空间入口',
        text='科创空间'
    )
    set_btn = Elem(
        tag='我的页右上角设置入口',
        rid='id/me_top_bar_setting_iv'
    )
    # title = Elem(
    #     tag='当前页标题',
    #     rid='id/tv_actionbar_title'
    # )
    agree_text = Elem(
        tag='同意按钮',
        rid='id/agreement_tv_2'
    )
    page_title = Elem(
        tag='当前页标题',
        rid='id/tv_actionbar_title'
    )

