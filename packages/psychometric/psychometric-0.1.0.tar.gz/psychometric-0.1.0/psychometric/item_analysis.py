"""
项目分析模块 (Item Analysis)

提供难易度分析和区分度分析功能
"""

import pandas as pd
from scipy import stats
from .utils import validate_dataframe, is_binary
from .exceptions import DataValidationError


class ItemAnalysis:
    """
    项目分析类

    用于分析问卷中单个题目的质量，包括难易度和区分度
    """

    def __init__(self, data, item_names=None):
        """
        初始化项目分析

        Parameters
        ----------
        data : pd.DataFrame
            问卷数据，行为样本，列为题目
        item_names : list, optional
            题目名称列表，如果为None则使用列名
        """
        validate_dataframe(data, min_samples=30, min_items=1)
        self.data = data.copy()
        self.item_names = item_names if item_names else data.columns.tolist()
        self.n_samples = len(data)
        self.n_items = len(data.columns)

    def difficulty(self):
        """
        计算难易度

        对于连续数据，使用均值作为难易度指标
        对于二分数据（0/1），使用通过率（P值）

        Returns
        -------
        pd.DataFrame
            包含每个题目的难易度信息
            - mean: 均值
            - std: 标准差
            - min: 最小值
            - max: 最大值
            - difficulty: 难易度（连续数据为均值，二分数据为通过率）
            - level: 难易度等级（易/中/难）
        """
        results = []

        for col in self.data.columns:
            item_data = self.data[col].dropna()
            mean_val = item_data.mean()
            std_val = item_data.std()
            min_val = item_data.min()
            max_val = item_data.max()

            # 判断是否为二分数据
            if is_binary(pd.DataFrame(item_data)):
                # 二分数据使用通过率
                difficulty = mean_val  # 0/1数据的均值即为通过率
                level = self._classify_difficulty_binary(difficulty)
            else:
                # 连续数据使用均值，标准化到0-1
                score_range = max_val - min_val
                if score_range > 0:
                    difficulty = (mean_val - min_val) / score_range
                else:
                    difficulty = 0.5
                level = self._classify_difficulty_continuous(difficulty)

            results.append(
                {
                    "item": col,
                    "mean": mean_val,
                    "std": std_val,
                    "min": min_val,
                    "max": max_val,
                    "difficulty": difficulty,
                    "level": level,
                }
            )

        return pd.DataFrame(results)

    def _classify_difficulty_binary(self, p):
        """二分数据难易度分类"""
        if p >= 0.7:
            return "易"
        elif p >= 0.3:
            return "中"
        else:
            return "难"

    def _classify_difficulty_continuous(self, d):
        """连续数据难易度分类"""
        if d >= 0.7:
            return "易"
        elif d >= 0.3:
            return "中"
        else:
            return "难"

    def citc(self, corrected=True):
        """
        计算校正题总相关 (Corrected Item-Total Correlation)

        衡量每个题目与总分的相关程度，用于评估题目的区分度

        Parameters
        ----------
        corrected : bool, default=True
            是否使用校正方法（从总分中移除该题目）

        Returns
        -------
        pd.DataFrame
            包含每个题目的CITC值
            - item: 题目名称
            - citc: 校正题总相关系数
            - quality: 质量评级（优秀/良好/可接受/较差）
        """
        results = []

        # 计算总分
        total_score = self.data.sum(axis=1)

        for col in self.data.columns:
            item_data = self.data[col]

            if corrected:
                # 校正：从总分中移除该题目
                corrected_total = total_score - item_data
                correlation = item_data.corr(corrected_total)
            else:
                # 未校正
                correlation = item_data.corr(total_score)

            quality = self._classify_citc(correlation)

            results.append({"item": col, "citc": correlation, "quality": quality})

        return pd.DataFrame(results)

    def _classify_citc(self, r):
        """CITC质量分类"""
        if pd.isna(r):
            return "无法计算"
        elif r >= 0.4:
            return "优秀"
        elif r >= 0.3:
            return "良好"
        elif r >= 0.2:
            return "可接受"
        else:
            return "较差"

    def extreme_group_test(self, p=0.27, method="independent"):
        """
        极端组检验 (Extreme Group Method)

        比较高分组和低分组在每个题目上的差异，评估题目的区分度

        Parameters
        ----------
        p : float, default=0.27
            极端组的比例（取总分最高和最低的p比例）
        method : str, default='independent'
            检验方法：'independent' (独立样本t检验) 或 'mann-whitney' (Mann-Whitney U检验)

        Returns
        -------
        pd.DataFrame
            包含每个题目的极端组检验结果
            - item: 题目名称
            - high_mean: 高分组均值
            - low_mean: 低分组均值
            - difference: 均值差
            - statistic: 检验统计量
            - p_value: p值
            - significant: 是否显著（p<0.05）
            - discrimination: 区分度评级
        """
        if not 0 < p < 0.5:
            raise DataValidationError("极端组比例p必须在0到0.5之间")

        # 计算总分
        total_score = self.data.sum(axis=1)

        # 确定分组阈值
        n_extreme = int(len(total_score) * p)
        if n_extreme < 10:
            raise DataValidationError(
                f"极端组样本量过小（{n_extreme}），建议增加样本或调整p值"
            )

        # 排序并分组
        sorted_indices = total_score.argsort()
        low_group_idx = sorted_indices[:n_extreme]
        high_group_idx = sorted_indices[-n_extreme:]

        results = []

        for col in self.data.columns:
            high_group = self.data.loc[high_group_idx, col]
            low_group = self.data.loc[low_group_idx, col]

            high_mean = high_group.mean()
            low_mean = low_group.mean()
            difference = high_mean - low_mean

            # 执行检验
            if method == "independent":
                statistic, p_value = stats.ttest_ind(high_group, low_group)
            elif method == "mann-whitney":
                statistic, p_value = stats.mannwhitneyu(
                    high_group, low_group, alternative="two-sided"
                )
            else:
                raise ValueError(f"不支持的检验方法: {method}")

            significant = p_value < 0.05
            discrimination = self._classify_discrimination(difference, significant)

            results.append(
                {
                    "item": col,
                    "high_mean": high_mean,
                    "low_mean": low_mean,
                    "difference": difference,
                    "statistic": statistic,
                    "p_value": p_value,
                    "significant": significant,
                    "discrimination": discrimination,
                }
            )

        return pd.DataFrame(results)

    def _classify_discrimination(self, diff, significant):
        """区分度分类"""
        if not significant:
            return "不显著"
        elif diff >= 0.3:
            return "优秀"
        elif diff >= 0.2:
            return "良好"
        else:
            return "一般"

    def analyze(self, extreme_p=0.27):
        """
        完整的项目分析报告

        Parameters
        ----------
        extreme_p : float, default=0.27
            极端组比例

        Returns
        -------
        dict
            包含所有项目分析结果的字典
            - difficulty: 难易度分析结果
            - citc: 校正题总相关结果
            - extreme_group: 极端组检验结果
            - summary: 综合评估结果
        """
        difficulty_df = self.difficulty()
        citc_df = self.citc()
        extreme_df = self.extreme_group_test(p=extreme_p)

        # 合并结果
        summary = (
            difficulty_df[["item", "difficulty", "level"]]
            .merge(citc_df[["item", "citc", "quality"]], on="item")
            .merge(
                extreme_df[["item", "difference", "significant", "discrimination"]],
                on="item",
            )
        )

        # 添加综合建议
        summary["recommendation"] = summary.apply(self._get_recommendation, axis=1)

        return {
            "difficulty": difficulty_df,
            "citc": citc_df,
            "extreme_group": extreme_df,
            "summary": summary,
        }

    def _get_recommendation(self, row):
        """根据分析结果给出建议"""
        issues = []

        # 检查难易度
        if row["level"] in ["易", "难"]:
            issues.append(f"难易度偏{row['level']}")

        # 检查CITC
        if row["quality"] in ["较差", "可接受"]:
            issues.append(f"CITC{row['quality']}")

        # 检查区分度
        if row["discrimination"] in ["不显著", "一般"]:
            issues.append(f"区分度{row['discrimination']}")

        if not issues:
            return "保留"
        elif len(issues) >= 2:
            return "建议删除"
        else:
            return "考虑修改"
