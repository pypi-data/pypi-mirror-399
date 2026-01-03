import time

from .driver import HmDriver

from kytest.utils.log import logger


class Elem(object):
    """
    鸿蒙元素定义
    https://github.com/codematrixer/hmdriver2
    """

    def __init__(self,
                 tag=None
                 ):
        """
        @param tag: 元素名称，方便后续维护
        """
        self._driver: HmDriver = None
        self.tag = tag
        self._first_locator = None

    def __get__(self, instance, owner):
        """po模式中element初始化不需要带driver的关键"""
        if instance is None:
            return None

        self._driver = instance.driver
        return self

    # # 公共方法
    # def _match(self, text):
    #     """
    #     判断元素是否存在当前页面
    #     @return:
    #     """
    #     _element = self._driver.d(text=text)
    #     result = text if _element.exists(timeout=0.1) else None
    #     return result
    #
    # def pop_check(self, timeout=3):
    #     logger.info(f"开始弹窗检测: {self._watch}")
    #     # 多线程match，如果match到，获取第一个非None内容，进行点击
    #     # match完休息1s，如果休息3s也没有match到，就停止（定义一个flag，match到就清零）
    #     # 如果3s内仍然能match到就继续（如果flag大于3就停止）
    #     _build_info = ["允许", "使用App时允许", "始终允许", "同意"]
    #     if self._watch is True:
    #         loc_list = _build_info
    #     else:
    #         loc_list = list(set(_build_info + self._watch))
    #     flag = timeout
    #     while flag > 0:
    #         import concurrent.futures
    #
    #         logger.info(f"匹配: {loc_list}")
    #         with concurrent.futures.ThreadPoolExecutor() as executor:
    #             results = executor.map(self._match, loc_list)
    #             results = [item for item in results if item is not None]
    #
    #         if results:
    #             logger.info(f"匹配到: {results}")
    #             self._driver.d(text=results[0]).click()
    #             logger.info("点击成功")
    #             flag = timeout
    #         else:
    #             logger.info("匹配失败")
    #
    #         flag -= 1
    #         time.sleep(1)
    #     logger.info("结束检测")

    def locator(self, **kwargs):
        if not kwargs:
            raise KeyError('定位方式不能为空')
        return kwargs

    def find(self, timeout=5):
        """
        增加截图的方法
        @param timeout: 每次查找时间
        @param n：失败后重试的次数
        @return:
        """
        logger.info(f"查找: {self.tag}")
        # 第一个定位
        _element = self._driver.d(**self._first_locator)

        # # 后面的定位
        # if self._locators:
        #     for loc_obj in self._locators:
        #         if loc_obj.type == "child":
        #             _element = _element.child(*loc_obj.args, **loc_obj.kwargs)
        #         elif loc_obj.type == 'sibling':
        #             _element = _element.sibling(*loc_obj.args, **loc_obj.kwargs)
        #         elif loc_obj.type == 'left':
        #             _element = _element.left(*loc_obj.args, **loc_obj.kwargs)
        #         elif loc_obj.type == 'right':
        #             _element = _element.right(*loc_obj.args, **loc_obj.kwargs)
        #         elif loc_obj.type == 'up':
        #             _element = _element.up(*loc_obj.args, **loc_obj.kwargs)
        #         elif loc_obj.type == 'down':
        #             _element = _element.down(*loc_obj.args, **loc_obj.kwargs)

        if _element.find_component(wait_time=timeout):
            logger.info(f"查找成功")
            return _element
        else:
            logger.info("查找失败")
            self._driver.shot(f"{self.tag}_查找失败")
            raise Exception(f"{self.tag}, 查找失败")

    def exists(self, timeout=5):
        logger.info(f"判断{self.tag}是否存在")
        try:
            self.find(timeout=timeout)
            return True
        except:
            return False

    def get_text(self, timeout=5):
        logger.info(f"获取{self.tag}的文本")
        return self.find(timeout=timeout).text

    def click_exists(self, timeout=5):
        logger.info(f"{self.tag}存在才点击")
        try:
            self.find(timeout=timeout).click()
            logger.info("点击完成")
        except:
            logger.info("不存在，不进行操作")

    def click(self, timeout=5):
        logger.info(f"{self.tag}点击")
        self.find(timeout=timeout).click()
        logger.info("点击完成")

    def input(self, text, timeout=5, clear=False):
        logger.info(f"{self.tag}输入文本: {text}")
        element = self.find(timeout=timeout)
        if clear is True:
            element.clear_text()
        element.input_text(text)
        logger.info("输入完成")









