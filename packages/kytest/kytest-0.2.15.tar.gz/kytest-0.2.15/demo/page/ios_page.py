"""
@Author: kang.yang
@Date: 2025/4/11 14:59
"""
import kytest
from kytest.core.ios import Elem


class IosPage(kytest.Page):
    music_tab = Elem(
        tag='儿童tab',
        label='儿童'
    )
    gold_tab = Elem(
        tag='金币tab',
        name='金币'
    )
