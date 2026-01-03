"""
- HDpip: A pip GUI based on maliang
- Copyright © 2025 寒冬利刃.
- License: MIT
"""

import json

class Data():
    """
    接受一个`.json`文件（使用`open`函数打开文件，并使用`load`函数加载。），生成一个数据类。
    
    但是，您应该如此获得数据：
    ```
    d = Data()
    d.open("data.json")
    d.load() #这是必须的，因为在open后不会自动运行load函数。
    print(d.data[0][0])
    ```
    """

    def open(self, file: str, encoding: str = "utf-8") -> dict[str: str]:
        """
        绑定一个`.json`文件，且返回绑定的文件字典。
        
        :param self: `Data`类
        :param file: 一个指向`.json`文件的路径，如`data.json`
        :type file: str
        :param encoding: 编码字符串，如`utf-8`
        :type encoding: str
        :param mode: 文件打开模式，如`w+`
        :type mode: str
        :return: 文件字典
        :rtype: dict[str: str]
        """

        self.file = {"file": file, "encoding": encoding}
        return self.file
    def load(self) -> list | dict:
        """
        加载`.json`文件的数据至数据类并返回。
        
        :param self: `Data`类
        :return: 数据
        :rtype: list | dict
        """

        with open(**self.file, mode = "r") as f:
            self.data = json.load(f)
        return self.data
    def save(self) -> list | dict:
        """
        保存`.json`文件的数据至文件并返回。
        
        :param self: `Data`类
        :return: 数据
        :rtype: list | dict
        """

        with open(**self.file, mode = "w") as f:
            json.dump(self.data, f)
        return self.data
