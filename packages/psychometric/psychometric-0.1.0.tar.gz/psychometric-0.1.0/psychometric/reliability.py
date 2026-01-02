"""
信度分析模块 (Reliability Analysis)

提供Cronbach's α和McDonald's Omega等信度指标计算
"""

import pandas as pd
import numpy as np
import pingouin as pg
from .utils import validate_dataframe
from .exceptions import DataValidationError


class Reliability:
    """
    信度分析类

    用于评估问卷的内部一致性信度
    """

    def __init__(self, data, item_names=None):
        """
        初始化信度分析

        Parameters
        ----------
        data : pd.DataFrame
            问卷数据，行为样本，列为题目
        item_names : list, optional
            题目名称列表，如果为None则使用列名
        """
        validate_dataframe(data, min_samples=30, min_items=2)
        self.data = data.copy()
        self.item_names = item_names if item_names else data.columns.tolist()
        self.n_samples = len(data)
        self.n_items = len(data.columns)

    def cronbach_alpha(self, standardized=False):
        """
        计算Cronbach's α系数

        Parameters
        ----------
        standardized : bool, default=False
            是否计算标准化α系数

        Returns
        -------
        dict
            包含α系数及相关信息
            - alpha: Cronbach's α系数
            - standardized_alpha: 标准化α系数（如果standardized=True）
            - n_items: 题目数量
            - n_samples: 样本数量
            - quality: 信度质量评级
        """
        # 使用pingouin计算
        alpha_result = pg.cronbach_alpha(data=self.data)
        alpha_value = alpha_result[0]

        result = {
            "alpha": alpha_value,
            "n_items": self.n_items,
            "n_samples": self.n_samples,
            "quality": self._classify_reliability(alpha_value),
        }

        if standardized:
            # 计算标准化α
            # 标准化数据
            standardized_data = (self.data - self.data.mean()) / self.data.std()
            std_alpha = pg.cronbach_alpha(data=standardized_data)[0]
            result["standardized_alpha"] = std_alpha

        return result

    def alpha_if_deleted(self):
        """
        计算删除每个题目后的Cronbach's α系数

        用于识别降低信度的题目

        Returns
        -------
        pd.DataFrame
            包含删除每个题目后的α值
            - item: 题目名称
            - alpha_if_deleted: 删除该题目后的α值
            - alpha_change: α值变化（正值表示删除后α增加）
            - recommendation: 建议
        """
        # 计算原始α值
        original_alpha = pg.cronbach_alpha(data=self.data)[0]

        results = []

        for col in self.data.columns:
            # 删除该列后的数据
            data_without_item = self.data.drop(columns=[col])

            # 计算新的α值
            if len(data_without_item.columns) >= 2:
                alpha_new = pg.cronbach_alpha(data=data_without_item)[0]
            else:
                alpha_new = np.nan

            alpha_change = alpha_new - original_alpha

            # 给出建议
            if alpha_change > 0.05:
                recommendation = "建议删除（删除后α显著提升）"
            elif alpha_change > 0:
                recommendation = "考虑删除（删除后α略有提升）"
            else:
                recommendation = "保留"

            results.append(
                {
                    "item": col,
                    "alpha_if_deleted": alpha_new,
                    "alpha_change": alpha_change,
                    "recommendation": recommendation,
                }
            )

        df_result = pd.DataFrame(results)
        df_result["original_alpha"] = original_alpha

        return df_result

    def omega(self, factor_structure=None):
        """
        计算McDonald's Omega系数

        需要指定因子结构或自动从单因子模型计算

        Parameters
        ----------
        factor_structure : dict, optional
            因子结构字典，格式为 {'factor1': ['item1', 'item2'], 'factor2': ['item3']}
            如果为None，则假设所有题目属于单一因子

        Returns
        -------
        dict
            包含Omega系数及相关信息
            - omega_total: 总体Omega系数
            - omega_hierarchical: 层次Omega系数（如果适用）
            - quality: 信度质量评级
        """
        if factor_structure is None:
            # 单因子模型
            return self._omega_single_factor()
        else:
            # 多因子模型
            return self._omega_multiple_factors(factor_structure)

    def _omega_single_factor(self):
        """计算单因子模型的Omega系数"""
        try:
            # 进行因子分析提取单因子
            from factor_analyzer import FactorAnalyzer

            # 转换为numpy数组以避免兼容性问题
            data_array = self.data.values

            fa = FactorAnalyzer(n_factors=1, rotation=None)
            fa.fit(data_array)

            # 获取因子载荷
            loadings = fa.loadings_[:, 0]

            # 计算Omega
            # ω = (Σλ)² / [(Σλ)² + Σ(1-λ²)]
            sum_loadings = np.sum(loadings)
            sum_error_var = np.sum(1 - loadings**2)

            omega = (sum_loadings**2) / (sum_loadings**2 + sum_error_var)

            return {
                "omega_total": omega,
                "n_factors": 1,
                "quality": self._classify_reliability(omega),
            }
        except Exception as e:
            raise DataValidationError(f"Omega计算失败: {str(e)}")

    def _omega_multiple_factors(self, factor_structure):
        """计算多因子模型的Omega系数"""
        results = {}

        # 为每个因子计算Omega
        for factor_name, items in factor_structure.items():
            if not all(item in self.data.columns for item in items):
                raise DataValidationError(f"因子'{factor_name}'包含不存在的题目")

            factor_data = self.data[items]

            if len(items) < 2:
                raise DataValidationError(f"因子'{factor_name}'至少需要2个题目")

            try:
                # 对该因子进行单因子分析
                from factor_analyzer import FactorAnalyzer

                # 转换为numpy数组
                factor_array = factor_data.values

                fa = FactorAnalyzer(n_factors=1, rotation=None)
                fa.fit(factor_array)

                loadings = fa.loadings_[:, 0]

                sum_loadings = np.sum(loadings)
                sum_error_var = np.sum(1 - loadings**2)

                omega = (sum_loadings**2) / (sum_loadings**2 + sum_error_var)

                results[factor_name] = {
                    "omega": omega,
                    "n_items": len(items),
                    "quality": self._classify_reliability(omega),
                }
            except Exception as e:
                results[factor_name] = {"error": str(e)}

        return results

    def _classify_reliability(self, value):
        """信度质量分类"""
        if pd.isna(value):
            return "无法计算"
        elif value >= 0.9:
            return "优秀"
        elif value >= 0.8:
            return "良好"
        elif value >= 0.7:
            return "可接受"
        elif value >= 0.6:
            return "较差"
        else:
            return "不可接受"

    def split_half_reliability(self, method="even-odd"):
        """
        分半信度

        Parameters
        ----------
        method : str, default='even-odd'
            分半方法：'even-odd'（奇偶分半）或 'first-second'（前后分半）

        Returns
        -------
        dict
            包含分半信度结果
            - half1_alpha: 第一半的α系数
            - half2_alpha: 第二半的α系数
            - correlation: 两半相关系数
            - spearman_brown: Spearman-Brown校正后的信度系数
        """
        n_items = self.n_items

        if method == "even-odd":
            # 奇偶分半
            half1_cols = self.data.columns[::2]
            half2_cols = self.data.columns[1::2]
        elif method == "first-second":
            # 前后分半
            mid = n_items // 2
            half1_cols = self.data.columns[:mid]
            half2_cols = self.data.columns[mid:]
        else:
            raise ValueError(f"不支持的分半方法: {method}")

        half1_data = self.data[half1_cols]
        half2_data = self.data[half2_cols]

        # 计算两半的α系数
        half1_alpha = (
            pg.cronbach_alpha(data=half1_data)[0] if len(half1_cols) >= 2 else np.nan
        )
        half2_alpha = (
            pg.cronbach_alpha(data=half2_data)[0] if len(half2_cols) >= 2 else np.nan
        )

        # 计算两半总分的相关
        half1_score = half1_data.sum(axis=1)
        half2_score = half2_data.sum(axis=1)
        correlation = half1_score.corr(half2_score)

        # Spearman-Brown校正
        spearman_brown = (2 * correlation) / (1 + correlation)

        return {
            "method": method,
            "half1_alpha": half1_alpha,
            "half2_alpha": half2_alpha,
            "correlation": correlation,
            "spearman_brown": spearman_brown,
            "quality": self._classify_reliability(spearman_brown),
        }

    def analyze(self, factor_structure=None):
        """
        完整的信度分析报告

        Parameters
        ----------
        factor_structure : dict, optional
            因子结构（用于Omega计算）

        Returns
        -------
        dict
            包含所有信度分析结果
            - cronbach_alpha: Cronbach's α结果
            - alpha_if_deleted: 删除题目后的α值
            - omega: McDonald's Omega结果
            - split_half: 分半信度结果
        """
        results = {
            "cronbach_alpha": self.cronbach_alpha(standardized=True),
            "alpha_if_deleted": self.alpha_if_deleted(),
            "split_half": self.split_half_reliability(),
        }

        # 计算Omega
        try:
            results["omega"] = self.omega(factor_structure)
        except Exception as e:
            results["omega"] = {"error": str(e)}

        return results
