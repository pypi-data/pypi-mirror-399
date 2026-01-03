"""数据处理工具模块
提供数据处理和分析功能
"""

class DataProcessor:
    """数据处理器类"""
    def __init__(self):
        """初始化数据处理器"""
        self.data = []

    def add_data(self, item):
        """添加数据项
        Args:
            item: 要添加的数据项
        """
        self.data.append(item)

    def get_average(self):
        """计算数据的平均值
        Returns:
            float: 平均值
        Raises:
            ValueError: 当数据为空时抛出异常
        """
        if not self.data:
            raise ValueError("数据为空，无法计算平均值")
        return sum(self.data) / len(self.data)

    def get_max(self):
        """获取最大值
        Returns:
            数据中的最大值
        Raises:
            ValueError: 当数据为空时抛出异常
        """
        if not self.data:
            raise ValueError("数据为空，无法获取最大值")
        return max(self.data)

    def get_min(self):
        """获取最小值
        Returns:
            数据中的最小值
        Raises:
            ValueError: 当数据为空时抛出异常
        """
        if not self.data:
            raise ValueError("数据为空，无法获取最小值")
        return min(self.data)

    def clear_data(self):
        """清空所有数据"""
        self.data.clear()

    def get_data_count(self):
        """获取数据项数量
        Returns:
            int: 数据项数量
        """
        return len(self.data)
