"""
- HDpip: A pip GUI based on maliang
- Copyright © 2025 寒冬利刃.
- License: MIT
"""

import pathlib
import sys
import platform
import pip

class HDpipError(Exception):
    """
    抛出一个HDpip错误，初始化函数可以接受一个`message`参数。

    例如：
    ```
    raise HDpip("炸了！")
    ```

    ***您不应该使用它**，如果您不是HDpip的开发者。*
    """
    def __init__(self, message = None) -> None:
        self.message = message
        super().__init__(self.message)

def unfinshed() -> None:
    """
    用于未完成功能的占位，使用`HDpipError`抛出一个错误。
    """
    raise HDpipError("\033[1m\033[91m不是，哥们，你写了这个功能吗？！\033[0m")

def getBaseDir() -> pathlib.Path:
    """
    获取HDpip的根目录，即`main.py`所在目录。
    
    :return: 路径
    :rtype: Path
    """
    return pathlib.Path(__file__).parents[1]

def getPython() -> pathlib.Path:
    """
    获取运行HDpip的Python的路径。
    
    :return: 路径
    :rtype: Path
    """
    return pathlib.Path(sys.executable)

def switchVersion(ver: str | tuple[str, int] | list[str, int]) -> list[int]:
    """
    输入一个类型为`str（分隔符为.）`、`tutple`或`list`的版本，且对每个元素`int`化，返回其列表形式。
    
    :param ver: 输入的版本，如`0.1.0`
    :type ver: str | tuple[str, int] | list [str]
    :return: 输出的版本，如`[0, 1, 0]`
    :rtype: list[int]
    """
    result = []
    if type(ver) == str:
        result = ver.split(".")
    elif type(ver) == tuple:
        result = list(ver)
    elif type(ver) == list:
        result = ver
    else:
        raise TypeError(f"版本转换支持str、tuple或list类型，但您输入的是{type(ver)}！")
    for i in range(0, len(result)):
        result[i] = int(result[i])
    return result

def compareUpdate(ver1: list[int], ver2: list[int]) -> bool:
    """
    输入两个版本列表，返回是否需要更新。
    
    :param ver1: 当前版本
    :type ver1: list[int]
    :param ver2: 对比版本
    :type ver2: list[int]
    :return: 是否需要更新
    :rtype: bool
    """
    for i1, i2 in zip(ver1, ver2):
        if i1 < i2:
            return True
    return False

def getPythonVersion() -> list[int]:
    """
    获取运行HDpip的Python的版本。
    
    :return: 版本列表
    :rtype: list[int]
    """
    return switchVersion(platform.python_version_tuple())

def getPipVersion() -> list[int]:
    """
    获取运行HDpip的Python所对应的pip的版本。
    
    :return: 版本列表
    :rtype: list[int]
    """
    return switchVersion(pip.__version__)
