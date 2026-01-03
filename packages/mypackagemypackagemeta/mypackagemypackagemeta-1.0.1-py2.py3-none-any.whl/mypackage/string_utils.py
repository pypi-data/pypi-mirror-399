"""字符串工具模块
提供字符串处理功能
"""

def capitalize_words(text):
    """将字符串中每个单词的首字母大写
    Args:
        text (str): 输入字符串
    Returns:
        str: 处理后的字符串
    """
    return ' '.join(word.capitalize() for word in text.split())

def reverse_string(text):
    """反转字符串
    Args:
        text (str): 输入字符串
    Returns:
        str: 反转后的字符串
    """
    return text[::-1]

def count_words(text):
    """统计字符串中的单词数量
    Args:
        text (str): 输入字符串
    Returns:
        int: 单词数量
    """
    return len(text.split())

def remove_spaces(text):
    """移除字符串中的所有空格
    Args:
        text (str): 输入字符串
    Returns:
        str: 移除空格后的字符串
    """
    return text.replace(' ', '')
