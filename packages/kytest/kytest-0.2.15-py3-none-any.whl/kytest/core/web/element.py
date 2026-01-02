"""
@Author: kang.yang
@Date: 2023/5/13 10:16
"""
from playwright.sync_api import expect, Locator
from .driver import Driver
from kytest.utils.log import logger


class BaseLocator:
    """
    各种定位方式的临时对象，用于支持链式调用
    """

    def __init__(self,
                 text=None,
                 exact=None,
                 placeholder=None,
                 role=None,
                 name=None,
                 locator=None,
                 filters=None,
                 nth=None
                 ):
        if filters is None:
            filters = {}
        self.text = text
        self.exact = exact
        self.placeholder = placeholder
        self.role = role
        self.name = name
        self.locator = locator
        self.filters = filters
        self.nth = nth


class Elem:
    """
    通过playwright定位的web元素
    https://playwright.dev/python/docs/locators
    """

    def __init__(self, tag: str = None):
        """
        @param tag: 元素名称，方便后续维护
        """
        self._driver: Driver = None
        self.tag = tag
        if not self.tag:
            raise KeyError('tag不能为空')
        self._locators = []

    def __call__(self, *args, **kwargs):
        return self

    def __get__(self, instance, owner):
        """pm模式的关键"""
        if instance is None:
            return None
        self._driver = instance.driver
        return self

    def get_by_text(self, text, exact=False):
        self._locators.append(BaseLocator(text=text, exact=exact))
        return self

    def get_by_placeholder(self, placeholder):
        self._locators.append(BaseLocator(placeholder=placeholder))
        return self

    def get_by_role(self, role, name=None):
        self._locators.append(BaseLocator(role=role, name=name))
        return self

    def locator(self, locator):
        self._locators.append(BaseLocator(locator=locator))
        return self

    def nth(self, nth):
        self._locators.append(BaseLocator(nth=nth))
        return self

    def filter(self, **kwargs):
        self._locators.append(BaseLocator(filters=kwargs))
        return self

    def get_locator(self):
        """
        根据定位方式返回对应的locator
        @return:
        """
        if not self._locators:
            raise KeyError('定位方式不能为空')
        # 第一个
        _page = self._driver.page
        first_locator: BaseLocator = self._locators[0]
        if first_locator.text:
            _element = _page.get_by_text(first_locator.text, exact=first_locator.exact)
        elif first_locator.role:
            _element = _page.get_by_role(first_locator.role, name=first_locator.name)
        elif first_locator.placeholder:
            _element = _page.get_by_placeholder(first_locator.placeholder)
        elif first_locator.locator:
            _element = _page.locator(first_locator.locator)
        else:
            raise KeyError('不支持的定位方式')
        # 第二个开始
        for locator in self._locators[1:]:
            if locator.text:
                _element = _element.get_by_text(locator.text, exact=locator.exact)
            elif locator.role:
                _element = _page.get_by_role(locator.role, name=locator.name)
            elif locator.placeholder:
                _element = _element.get_by_placeholder(locator.placeholder)
            elif locator.locator:
                _element = _element.locator(locator.locator)
            elif locator.filters:
                _element = _element.filter(**locator.filters)
            elif locator.nth:
                _element = _element.nth(locator.nth)
            else:
                raise KeyError('不支持的定位方式')
        return _element

    def find(self, timeout=5):
        """查找指定的一个元素"""
        logger.info(f"查找: {self.tag}")
        element = self.get_locator()
        try:
            element.wait_for(timeout=timeout * 1000)
            logger.info("查找成功")
            return element
        except:
            self._driver.shot("查找失败")
            raise Exception("查找失败")

    # 属性
    def is_visible(self, timeout=1):
        logger.info(f"判断{self.tag}是否可见")
        return self.find(timeout=timeout).is_visible()

    def is_hidden(self, timeout=1):
        logger.info(f"判断{self.tag}是否隐藏")
        return self.find(timeout=timeout).is_hidden()

    def text_content(self):
        logger.info(f"获取{self.tag}的文本")
        elem = self.find()
        text = elem.text_content()
        logger.info(text)
        return text

    def all_text_content(self):
        logger.info(f"获取{self.tag}的多个文本")
        elems = self.find().all()
        text_list = [elem.text_content() for elem in elems]
        logger.info(text_list)
        return text_list

    # 操作
    def click_exists(self, timeout=5, *args, **kwargs):
        """
        page.get_by_text("Item").click(button="right")
        page.get_by_text("Item").click(modifiers=["Shift"])
        page.get_by_text("Item").click(position={ "x": 0, "y": 0})
        page.get_by_role("button").click(force=True)
        @param timeout:
        @param args:
        @param kwargs:
        @return:
        """
        logger.info(f"存在才点击{self.tag}")
        try:
            self.find(timeout=timeout).click(*args, **kwargs)
            logger.info(f"点击完成")
        except:
            logger.info("不存在跳过点击")

    def click(self, timeout=5, *args, **kwargs):
        """
        page.get_by_text("Item").click(button="right")
        page.get_by_text("Item").click(modifiers=["Shift"])
        page.get_by_text("Item").click(position={ "x": 0, "y": 0})
        page.get_by_role("button").click(force=True)
        @param timeout: 
        @param args: 
        @param kwargs: 
        @return: 
        """
        logger.info(f"点击{self.tag}")
        self.find(timeout=timeout).click(*args, **kwargs)
        logger.info(f"点击完成")

    def js_click(self, timeout=5):
        """
        其它点击方式都不管用了可以试试这个
        @param timeout:
        @return:
        """
        logger.info(f"使用js事件点击{self.tag}")
        self.find(timeout=timeout).dispatch_event('click')
        logger.info(f"点击完成")

    def dbclick(self, timeout=5):
        logger.info(f"双击{self.tag}")
        self.find(timeout=timeout).dblclick()
        logger.info(f"双击完成")

    def input(self, text, timeout=5):
        logger.info(f"{self.tag}输入: {text}")
        self.find(timeout=timeout).fill(text)
        logger.info(f"输入完成")

    # def press(self, key, timeout=5):
    #     """
    #     @param key: 单个键位支持Backquote, Minus, Equal, Backslash, Backspace, Tab, Delete, Escape,
    #     ArrowDown, End, Enter, Home, Insert, PageDown, PageUp, ArrowRight, ArrowUp, F1 - F12, Digit0 - Digit9,
    #     KeyA - KeyZ, etc.
    #                 还支持组合键，如Shift+A、Control+o、Control+Shift+T
    #     @param timeout:
    #     @return:
    #     """
    #     logger.info(f"键盘输入{key}")
    #     self.find(timeout=timeout).press(key)
    #     logger.info("输入完成")

    # def press_sequentially(self, words: str, timeout=5):
    #     """
    #     没找到引用，不知道靠不靠谱
    #     @param words:
    #     @param timeout:
    #     @return:
    #     """
    #     logger.info(f"逐个输入: {words}")
    #     self.find(timeout=timeout).press_sequentially(words)
    #     logger.info("输入完成")

    def check(self, timeout=5):
        logger.info(f"{self.tag}选中")
        self.find(timeout=timeout).check()
        logger.info(f"选中完成")

    def select_option(self, value: str, timeout=5):
        logger.info(f"{self.tag}选择")
        self.find(timeout=timeout).select_option(value)
        logger.info(f"选择完成")

    # def set_input_file(self, timeout=5, *args, **kwargs):
    #     """
    #     @param timeout:
    #     @param args:
    #     支持单个文件：'file.pdf'
    #     支持多个文件：['file1.txt', 'file2.txt']
    #     清空：[]
    #     @param kwargs: Upload buffer from memory
    #     files=[
    #         {"name": "test.txt", "mimeType": "text/plain", "buffer": b"this is a test"}
    #     ]
    #     @return:
    #     """
    #     logger.info(f"{self.tag}进行上传")
    #     self.find(timeout=timeout).set_input_files(*args, **kwargs)
    #     logger.info(f"{self.tag}上传完成")
    #
    # def set_files(self, file_path: str, timeout=5):
    #     logger.info(f"{self.tag}进行上传")
    #     locator = self.find(timeout=timeout)
    #     with self._driver.page.expect_file_chooser() as fc_info:
    #         locator.click()
    #     file_chooser = fc_info.value
    #     file_chooser.set_files(file_path)
    #     logger.info("上传完成")

    def focus(self, timeout=5):
        logger.info(f"聚焦到{self.tag}")
        self.find(timeout=timeout).focus()
        logger.info(f"聚焦完成")

    def drag_to(self, locator: Locator, timeout=5):
        logger.info(f"从{self.tag}拖动到{locator}")
        self.find(timeout=timeout).drag_to(locator)
        logger.info(f"拖动完成")

    def drag_to_manually(self, locator: Locator, timeout=5):
        logger.info(f"从{self.tag}拖动到{locator}")
        self.find(timeout=timeout).hover()
        self._driver.page.mouse.down()
        locator.hover()
        self._driver.page.mouse.up()
        logger.info(f"拖动完成")

    # def scroll_into_view_if_needed(self, timeout=5):
    #     """
    #     正常做其他操作会自动滚动到可视区，自动不生效再用这个方法
    #     @param timeout:
    #     @return:
    #     """
    #     logger.info(f"把{self.tag}滚动到可视区")
    #     self.find(timeout=timeout).scroll_into_view_if_needed()
    #     logger.info("滚动完成")

    def download(self, save_path: str, timeout=5):
        """
        下载
        @param save_path: 只要目录，文件名会自己生成
        @param timeout:
        @return:
        """
        logger.info(f"点击{self.tag}进行下载")
        with self._driver.page.expect_download() as download_info:
            self.find(timeout=timeout).click()
        download = download_info.value
        download.save_as(save_path + download.suggested_filename)
        logger.info(f"下载完成")

    def popup(self, timeout=5):
        """
        点击打开新页签，并返回新页签的page
        @param timeout:
        @return:
        """
        logger.info(f"点击{self.tag}打开新页签")
        with self._driver.page.expect_popup() as popup:
            self.find(timeout=timeout).click()
        new_page = popup.value
        logger.info("返回新页签对象")
        return new_page

    # 断言
    def assert_checked(self, timeout=5):
        logger.info(f"断言：{self.tag}是否选中")
        expect(self.find(timeout=timeout)).to_be_checked()
        logger.info("断言完成")

    def assert_visible(self, timeout=5):
        logger.info(f"断言：{self.tag}是否可见")
        expect(self.find(timeout=timeout)).to_be_visible()
        logger.info("断言完成")

    def assert_hidden(self, timeout=5):
        logger.info(f"断言：{self.tag}是否隐藏")
        expect(self.find(timeout=timeout)).to_be_hidden()
        logger.info("断言完成")

    def assert_text_ct(self, text: str, timeout=5):
        logger.info(f"断言：{self.tag}是否包含文本-{text}")
        expect(self.find(timeout=timeout)).to_contain_text(text, timeout=timeout)
        logger.info("断言完成")

    def assert_text_eq(self, text: str, timeout=5):
        logger.info(f"断言：{self.tag}是否等于文本-{text}")
        expect(self.find(timeout=timeout)).to_have_text(text)
        logger.info("断言完成")

    def assert_count_eq(self, count, timeout=5):
        logger.info(f"断言：{self.tag}定位到几个元素")
        expect(self.find(timeout=timeout)).to_have_count(count)
        logger.info("断言完成")

    # def screenshot(self, file_path, timeout=5, full_screen=True):
    #     logger.info("截屏")
    #     if full_screen is True:
    #         self._driver.shot(file_path)
    #     else:
    #         self.find(timeout=timeout).screenshot(path=file_path)
    #     logger.info("截屏完成")


if __name__ == '__main__':
    pass
