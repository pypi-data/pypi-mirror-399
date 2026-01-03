"""子包的初始化文件

演示包的层次结构
"""

from .advanced_math import factorial, fibonacci
from .module3 import fun3

__all__ = ['factorial', 'fibonacci', 'fun3']

print("子包subpackage已加载")
