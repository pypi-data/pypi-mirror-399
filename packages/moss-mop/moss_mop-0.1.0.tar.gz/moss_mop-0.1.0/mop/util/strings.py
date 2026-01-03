import re


def to_underline(camel: str) -> str:
    """
    将驼峰转为下划线
    :param camel: 驼峰字符串
    :return:
    """
    return re.sub('(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])', '_\g<0>', camel).lower()