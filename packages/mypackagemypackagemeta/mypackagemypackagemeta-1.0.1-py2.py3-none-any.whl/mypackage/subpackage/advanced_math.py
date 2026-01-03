"""高级数学运算模块
提供更复杂的数学运算功能
"""

def factorial(n):
    """计算阶乘
    Args:
        n (int): 非负整数
    Returns:
        int: n的阶乘
    Raises:
        ValueError: 当n为负数时抛出异常
    """
    if n < 0:
        raise ValueError("阶乘的参数必须是非负整数")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def fibonacci(n):
    """计算斐波那契数列的第n项
    Args:
        n (int): 项数（从0开始）
    Returns:
        int: 斐波那契数列的第n项
    Raises:
        ValueError: 当n为负数时抛出异常
    """
    if n < 0:
        raise ValueError("斐波那契数列的参数必须是非负整数")
    if n == 0:
        return 0
    if n == 1:
        return 1

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def is_prime(n):
    """判断一个数是否为质数
    Args:
        n (int): 要判断的数
    Returns:
        bool: 如果是质数返回True，否则返回False
    """
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True
