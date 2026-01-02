__doc__ = """
基础客户端类
"""


class BaseClient:
    """
    基础客户端类
    """

    def check_properties(self, *args):
        """
        检查属性是否存在
        :param args:
        :return:
        """
        for arg in args:
            if not hasattr(self, arg):
                raise AttributeError(f"Missing required property: {arg}")

    def check_required_properties(self, *args):
        """
        检查属性是否存在且不为None
        :param args:
        :return:
        """
        for arg in args:
            if not hasattr(self, arg):
                raise AttributeError(f"Missing required property: {arg}")
            if getattr(self, arg) is None:
                raise AttributeError(f"Required property cannot be None: {arg}")
