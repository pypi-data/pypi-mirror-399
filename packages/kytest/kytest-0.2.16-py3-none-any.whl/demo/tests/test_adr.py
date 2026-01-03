import kytest
from kytest.core.adr import TC
from page.adr_page import HomePage


@kytest.story('测试demo')
class TestAdrDemo(TC):
    def start(self):
        self.start_app()
        self.hp = HomePage(self.dr)

    def end(self):
        self.stop_app()

    @kytest.title('进入我的页')
    def test_switch_to_my(self):
        self.hp.ad_btn.click_exists()
        self.hp.my_tab.click()
        self.sleep(5)







