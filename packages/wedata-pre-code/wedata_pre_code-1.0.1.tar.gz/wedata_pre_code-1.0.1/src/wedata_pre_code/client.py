__doc__ = """
Wedata 预执行代码客户端
如果要初始化Wedata2的预执行代码客户端，请使用init_wedata2_pre_code方法
如果要初始化Wedata3的预执行代码客户端，请使用init_wedata3_pre_code方法
"""


class PreCodeClient:
    """
    Wedata 预执行代码客户端
    """

    def init_wedata2_pre_code(self, **kwargs):
        """
        初始化Wedata2的预执行代码客户端
        :param kwargs: Wedata2的预执行代码客户端的参数
        :return: Wedata2PreCodeClient实例
        """
        from wedata_pre_code.wedata2.client import Wedata2PreCodeClient
        return Wedata2PreCodeClient(**kwargs)

    def init_wedata3_pre_code(self, **kwargs):
        """
        初始化Wedata3的预执行代码客户端
        :param kwargs: Wedata3的预执行代码客户端的参数
        :return: Wedata3PreCodeClient实例
        """
        from wedata_pre_code.wedata3.client import Wedata3PreCodeClient
        return Wedata3PreCodeClient(**kwargs)
