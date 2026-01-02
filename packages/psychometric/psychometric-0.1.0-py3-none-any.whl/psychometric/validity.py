"""
效度分析模块 (Validity Analysis)

提供探索性因子分析(EFA)、验证性因子分析(CFA)、AVE和CR等效度指标计算
"""

import pandas as pd
import numpy as np
from factor_analyzer import FactorAnalyzer, calculate_bartlett_sphericity, calculate_kmo
from semopy import Model, calc_stats
from .utils import validate_dataframe
from .exceptions import DataValidationError


class Validity:
    """
    效度分析类

    用于评估问卷的结构效度
    """

    def __init__(self, data, item_names=None):
        """
        初始化效度分析

        Parameters
        ----------
        data : pd.DataFrame
            问卷数据，行为样本，列为题目
        item_names : list, optional
            题目名称列表，如果为None则使用列名
        """
        validate_dataframe(data, min_samples=50, min_items=3)
        self.data = data.copy()
        self.item_names = item_names if item_names else data.columns.tolist()
        self.n_samples = len(data)
        self.n_items = len(data.columns)

    def efa(self, n_factors=None, rotation="varimax", method="minres"):
        """
        探索性因子分析 (Exploratory Factor Analysis)

        Parameters
        ----------
        n_factors : int, optional
            因子数量，如果为None则使用特征值>1的准则自动确定
        rotation : str, default='varimax'
            旋转方法：'varimax', 'promax', 'oblimin'等
        method : str, default='minres'
            提取方法：'minres'(最小残差), 'ml'(最大似然), 'principal'(主成分)

        Returns
        -------
        dict
            包含EFA结果
            - n_factors: 因子数量
            - loadings: 因子载荷矩阵
            - variance: 方差解释
            - kmo: KMO检验结果
            - bartlett: Bartlett球形检验结果
            - factor_structure: 推荐的因子结构
        """
        # KMO检验
        kmo_all, kmo_model = calculate_kmo(self.data)

        # Bartlett球形检验
        chi_square, p_value = calculate_bartlett_sphericity(self.data)

        # 检验是否适合做因子分析
        if kmo_model < 0.6:
            raise DataValidationError(
                f"KMO值({kmo_model:.3f})过低，数据可能不适合做因子分析（建议KMO>0.6）"
            )

        if p_value > 0.05:
            raise DataValidationError(
                f"Bartlett检验不显著(p={p_value:.3f})，数据可能不适合做因子分析"
            )

        # 如果未指定因子数，使用特征值>1的准则
        if n_factors is None:
            fa_initial = FactorAnalyzer(rotation=None)
            fa_initial.fit(self.data.values)
            ev, _ = fa_initial.get_eigenvalues()
            n_factors = np.sum(ev > 1)

            if n_factors == 0:
                n_factors = 1

        # 进行因子分析
        fa = FactorAnalyzer(n_factors=n_factors, rotation=rotation, method=method)
        fa.fit(self.data.values)

        # 获取因子载荷
        loadings = fa.loadings_

        # 创建载荷矩阵DataFrame
        loadings_df = pd.DataFrame(
            loadings,
            index=self.data.columns,
            columns=[f"Factor{i + 1}" for i in range(n_factors)],
        )

        # 计算方差解释
        variance = fa.get_factor_variance()
        variance_df = pd.DataFrame(
            variance,
            index=["SS Loadings", "Proportion Var", "Cumulative Var"],
            columns=[f"Factor{i + 1}" for i in range(n_factors)],
        )

        # 推荐因子结构（每个题目归入载荷最大的因子）
        factor_structure = self._extract_factor_structure(loadings_df)

        # 获取共同度
        communalities = fa.get_communalities()
        communalities_df = pd.DataFrame(
            {"item": self.data.columns, "communality": communalities}
        )

        return {
            "n_factors": n_factors,
            "loadings": loadings_df,
            "variance": variance_df,
            "communalities": communalities_df,
            "kmo": {
                "overall": kmo_model,
                "per_item": pd.DataFrame({"item": self.data.columns, "kmo": kmo_all}),
            },
            "bartlett": {
                "chi_square": chi_square,
                "p_value": p_value,
                "df": (self.n_items * (self.n_items - 1)) // 2,
            },
            "factor_structure": factor_structure,
            "rotation": rotation,
            "method": method,
        }

    def _extract_factor_structure(self, loadings_df, threshold=0.4):
        """从载荷矩阵提取因子结构"""
        factor_structure = {}

        for i, col in enumerate(loadings_df.columns):
            factor_items = []
            for item in loadings_df.index:
                # 检查该题目在该因子上的载荷是否最大且超过阈值
                item_loadings = loadings_df.loc[item]
                max_loading = item_loadings.abs().max()
                max_factor = item_loadings.abs().idxmax()

                if max_factor == col and max_loading >= threshold:
                    factor_items.append(item)

            if factor_items:
                factor_structure[col] = factor_items

        return factor_structure

    def cfa(self, model_spec):
        """
        验证性因子分析 (Confirmatory Factor Analysis)

        使用semopy进行CFA

        Parameters
        ----------
        model_spec : str or dict
            模型规格说明
            如果是字符串，应为semopy的lavaan风格语法
            如果是字典，格式为 {'factor1': ['item1', 'item2'], ...}

        Returns
        -------
        dict
            包含CFA结果
            - fit_indices: 拟合指数
            - loadings: 标准化因子载荷
            - model: 拟合后的模型对象
        """
        # 如果输入是字典，转换为lavaan语法
        if isinstance(model_spec, dict):
            model_str = self._dict_to_lavaan(model_spec)
        else:
            model_str = model_spec

        # 拟合模型
        try:
            model = Model(model_str)
            model.fit(self.data)
        except Exception as e:
            raise DataValidationError(f"CFA模型拟合失败: {str(e)}")

        # 获取拟合指数
        fit_indices = self._extract_fit_indices(model)

        # 获取标准化载荷
        estimates = model.inspect()
        loadings = estimates[estimates["op"] == "~"]

        return {
            "fit_indices": fit_indices,
            "loadings": loadings,
            "estimates": estimates,
            "model": model,
            "model_spec": model_str,
        }

    def _dict_to_lavaan(self, factor_dict):
        """将因子结构字典转换为lavaan语法"""
        lines = []
        for factor, items in factor_dict.items():
            items_str = " + ".join(items)
            lines.append(f"{factor} =~ {items_str}")
        return "\n".join(lines)

    def _extract_fit_indices(self, model):
        """提取拟合指数"""
        return calc_stats(model)

    def ave_cr(self, factor_structure):
        """
        计算平均方差提取(AVE)和组合信度(CR)

        Parameters
        ----------
        factor_structure : dict
            因子结构，格式为 {'factor1': ['item1', 'item2'], ...}

        Returns
        -------
        pd.DataFrame
            包含每个因子的AVE和CR
            - factor: 因子名称
            - ave: 平均方差提取
            - cr: 组合信度
            - ave_quality: AVE质量评级
            - cr_quality: CR质量评级
        """
        results = []

        for factor, items in factor_structure.items():
            if not all(item in self.data.columns for item in items):
                raise DataValidationError(f"因子'{factor}'包含不存在的题目")

            if len(items) < 2:
                raise DataValidationError(f"因子'{factor}'至少需要2个题目")

            # 提取该因子的数据
            factor_data = self.data[items]

            # 进行单因子分析获取载荷
            fa = FactorAnalyzer(n_factors=1, rotation=None)
            fa.fit(factor_data.values)
            loadings = fa.loadings_[:, 0]

            # 计算AVE: AVE = Σλ² / n
            ave = np.mean(loadings**2)

            # 计算CR: CR = (Σλ)² / [(Σλ)² + Σ(1-λ²)]
            sum_loadings = np.sum(loadings)
            sum_error_var = np.sum(1 - loadings**2)
            cr = (sum_loadings**2) / (sum_loadings**2 + sum_error_var)

            results.append(
                {
                    "factor": factor,
                    "n_items": len(items),
                    "ave": ave,
                    "cr": cr,
                    "ave_quality": self._classify_ave(ave),
                    "cr_quality": self._classify_cr(cr),
                }
            )

        return pd.DataFrame(results)

    def _classify_ave(self, ave):
        """AVE质量分类"""
        if ave >= 0.5:
            return "良好"
        elif ave >= 0.36:
            return "可接受"
        else:
            return "较差"

    def _classify_cr(self, cr):
        """CR质量分类"""
        if cr >= 0.7:
            return "良好"
        elif cr >= 0.6:
            return "可接受"
        else:
            return "较差"

    def discriminant_validity(self, factor_structure):
        """
        判别效度分析

        检验各因子之间是否具有良好的区分度
        使用Fornell-Larcker准则：每个因子的AVE平方根应大于其与其他因子的相关系数

        Parameters
        ----------
        factor_structure : dict
            因子结构

        Returns
        -------
        dict
            包含判别效度分析结果
            - correlation_matrix: 因子间相关矩阵
            - ave_sqrt: AVE平方根
            - fornell_larcker: Fornell-Larcker准则检验结果
        """
        # 计算各因子的得分
        factor_scores = {}
        ave_values = {}

        for factor, items in factor_structure.items():
            factor_data = self.data[items]
            factor_scores[factor] = factor_data.mean(axis=1)

            # 计算AVE
            fa = FactorAnalyzer(n_factors=1, rotation=None)
            fa.fit(factor_data.values)
            loadings = fa.loadings_[:, 0]
            ave = np.mean(loadings**2)
            ave_values[factor] = ave

        # 计算因子间相关矩阵
        scores_df = pd.DataFrame(factor_scores)
        corr_matrix = scores_df.corr()

        # 计算AVE平方根
        ave_sqrt = pd.Series({f: np.sqrt(v) for f, v in ave_values.items()})

        # Fornell-Larcker准则检验
        fornell_larcker_results = []
        for factor in factor_structure.keys():
            sqrt_ave = ave_sqrt[factor]
            correlations = corr_matrix[factor].drop(factor)

            if len(correlations) > 0:
                max_corr = correlations.abs().max()
                passed = sqrt_ave > max_corr
            else:
                max_corr = np.nan
                passed = True

            fornell_larcker_results.append(
                {
                    "factor": factor,
                    "ave_sqrt": sqrt_ave,
                    "max_correlation": max_corr,
                    "passed": passed,
                }
            )

        return {
            "correlation_matrix": corr_matrix,
            "ave_sqrt": ave_sqrt,
            "fornell_larcker": pd.DataFrame(fornell_larcker_results),
        }

    def analyze(
        self, n_factors=None, rotation="varimax", factor_structure=None, cfa_model=None
    ):
        """
        完整的效度分析报告

        Parameters
        ----------
        n_factors : int, optional
            EFA的因子数量
        rotation : str, default='varimax'
            EFA的旋转方法
        factor_structure : dict, optional
            指定的因子结构（用于AVE/CR计算）
        cfa_model : str or dict, optional
            CFA模型规格

        Returns
        -------
        dict
            包含所有效度分析结果
        """
        results = {}

        # EFA分析
        try:
            efa_results = self.efa(n_factors=n_factors, rotation=rotation)
            results["efa"] = efa_results

            # 如果未指定因子结构，使用EFA推荐的结构
            if factor_structure is None:
                factor_structure = efa_results["factor_structure"]
        except Exception as e:
            results["efa"] = {"error": str(e)}

        # AVE和CR分析
        if factor_structure:
            try:
                ave_cr_results = self.ave_cr(factor_structure)
                results["ave_cr"] = ave_cr_results

                # 判别效度
                discriminant_results = self.discriminant_validity(factor_structure)
                results["discriminant_validity"] = discriminant_results
            except Exception as e:
                results["ave_cr"] = {"error": str(e)}

        # CFA分析
        if cfa_model:
            try:
                cfa_results = self.cfa(cfa_model)
                results["cfa"] = cfa_results
            except Exception as e:
                results["cfa"] = {"error": str(e)}

        return results
