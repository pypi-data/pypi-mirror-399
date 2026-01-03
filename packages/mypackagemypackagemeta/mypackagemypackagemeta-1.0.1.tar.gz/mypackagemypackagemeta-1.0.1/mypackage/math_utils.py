"""数学工具模块
提供基本的数学运算功能
"""

def add(a, b):
    """加法运算
    Args:
        a (float): 第一个数
        b (float): 第二个数
    Returns:
        float: 两数之和
    """
    return a + b

def multiply(a, b):
    """乘法运算
    Args:
        a (float): 第一个数
        b (float): 第二个数
    Returns:
        float: 两数之积
    """
    return a * b

def divide(a, b):
    """除法运算
    Args:
        a (float): 被除数
        b (float): 除数
    Returns:
        float: 除法结果
    Raises:
        ValueError: 当除数为0时抛出异常
    """
    if b == 0:
        raise ValueError("除数不能为0")
    return a / b

def power(base, exponent):
    """幂运算
    Args:
        base (float): 底数
        exponent (float): 指数
    Returns:
        float: 幂运算结果
    """
    return base ** exponent
