"""mypackage包的初始化文件
这个包演示了Python包的基本概念和使用方法
"""

# 包的版本信息
__version__ = "1.0.0"
__author__ = "Python学习者"

# 从子模块导入常用的类和函数
from .math_utils import add, multiply, divide
from .string_utils import capitalize_words, reverse_string
from .data_utils import DataProcessor
from . import module1, module2

# 定义包的公共API
__all__ = [
    'add', 'multiply', 'divide',
    'capitalize_words', 'reverse_string',
    'DataProcessor',
    'module1', 'module2'
]

print(f"mypackage包已加载，版本: {__version__}")
