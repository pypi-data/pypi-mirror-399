"""
通用工具函数
"""

import pandas as pd
import numpy as np
from .exceptions import DataValidationError, InsufficientDataError


def validate_dataframe(data, min_samples=30, min_items=1):
    """
    验证数据框的有效性

    Parameters
    ----------
    data : pd.DataFrame
        输入数据，行为样本，列为题目
    min_samples : int, default=30
        最小样本量要求
    min_items : int, default=1
        最小题目数要求

    Raises
    ------
    DataValidationError
        数据类型或格式不正确
    InsufficientDataError
        数据量不足
    """
    if not isinstance(data, pd.DataFrame):
        raise DataValidationError("输入数据必须是pandas.DataFrame类型")

    if data.empty:
        raise DataValidationError("数据框不能为空")

    n_samples, n_items = data.shape

    if n_samples < min_samples:
        raise InsufficientDataError(
            f"样本量不足：当前{n_samples}个样本，至少需要{min_samples}个"
        )

    if n_items < min_items:
        raise InsufficientDataError(
            f"题目数不足：当前{n_items}个题目，至少需要{min_items}个"
        )

    # 检查数据类型
    if not all(pd.api.types.is_numeric_dtype(data[col]) for col in data.columns):
        raise DataValidationError("所有列必须是数值型数据")

    return True


def handle_missing_values(data, method="drop"):
    """
    处理缺失值

    Parameters
    ----------
    data : pd.DataFrame
        输入数据
    method : str, default='drop'
        处理方法：'drop'（删除）或 'mean'（均值填充）

    Returns
    -------
    pd.DataFrame
        处理后的数据
    """
    if method == "drop":
        return data.dropna()
    elif method == "mean":
        return data.fillna(data.mean())
    else:
        raise ValueError(f"不支持的缺失值处理方法: {method}")


def get_score_range(data):
    """
    获取数据的分数范围

    Parameters
    ----------
    data : pd.DataFrame
        输入数据

    Returns
    -------
    tuple
        (最小值, 最大值)
    """
    return data.min().min(), data.max().max()


def is_binary(data):
    """
    判断数据是否为二分数据（0/1）

    Parameters
    ----------
    data : pd.DataFrame
        输入数据

    Returns
    -------
    bool
        是否为二分数据
    """
    unique_vals = pd.unique(data.values.ravel())
    unique_vals = unique_vals[~np.isnan(unique_vals)]
    return len(unique_vals) == 2 and set(unique_vals).issubset({0, 1})


def generate_data(
    n_samples=200, n_items=10, n_factors=2, random_seed=42
) -> pd.DataFrame:
    """
    生成模拟问卷数据

    Parameters
    ----------
    n_samples : int
        样本数量
    n_items : int
        题目数量
    n_factors : int
        因子数量
    random_seed : int
        随机种子

    Returns
    -------
    pd.DataFrame
        模拟数据
    """
    np.random.seed(random_seed)

    # 生成潜在因子得分
    factor_scores = np.random.randn(n_samples, n_factors)

    # 为每个题目分配到不同因子
    items_per_factor = n_items // n_factors
    data = np.zeros((n_samples, n_items))

    for i in range(n_items):
        factor_idx = i // items_per_factor
        if factor_idx >= n_factors:
            factor_idx = n_factors - 1

        # 题目 = 因子得分 * 载荷 + 误差
        loading = np.random.uniform(0.6, 0.9)
        error = np.random.randn(n_samples) * 0.3

        data[:, i] = factor_scores[:, factor_idx] * loading + error

    # 标准化到1-5分（李克特量表）
    data = (data - data.min()) / (data.max() - data.min()) * 4 + 1
    data = np.round(data)
    data = np.clip(data, 1, 5)

    # 创建DataFrame
    columns = [f"Q{i + 1}" for i in range(n_items)]
    df = pd.DataFrame(data, columns=columns)

    return df
