"""相对导入演示模块

演示包内部的相对导入
"""

# 相对导入同级模块
from . import math_utils, string_utils

# 相对导入子包
from .subpackage import advanced_math

def demo_relative_imports():
    """演示相对导入的函数"""
    print("=== 相对导入演示 ===")
    
    # 使用同级模块的函数
    print(f"使用math_utils: 8 + 2 = {math_utils.add(8, 2)}")
    print(f"使用string_utils: {string_utils.capitalize_words('relative import demo')}")
    
    # 使用子包的函数
    print(f"使用advanced_math: 4的阶乘 = {advanced_math.factorial(4)}")
    print(f"使用advanced_math: 斐波那契数列第7项 = {advanced_math.fibonacci(7)}")

if __name__ == "__main__":
    print("这个模块不能直接运行，必须作为包的一部分导入")