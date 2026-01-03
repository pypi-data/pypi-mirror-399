from sympy import sympify, lambdify
from sympy.logic.boolalg import Boolean
from pandas import DataFrame
from typing import Union
import numpy as np
from .object import BaseException

class MathsException(BaseException):
    pass

class ExpressionCache:
    """用于缓存表达式和对应矢量化函数的类"""
    _cache = {}

    @classmethod
    def get_calculator(cls, expression):
        """获取或创建表达式的矢量化计算器"""
        if expression not in cls._cache:
            cls._cache[expression] = VectorizedExpressionCalculator(expression)
        return cls._cache[expression]


class VectorizedExpressionCalculator:
    """矢量化表达式计算类"""
    def __init__(self, expression):
        # 将表达式字符串转换为 SymPy 表达式
        self.expression = sympify(expression)
        # 将 SymPy 表达式转换为矢量化函数（支持 NumPy/Pandas 运算）
        self.variables = sorted(self.expression.free_symbols, key=lambda x: str(x)) # 这里要用sorted很关键，因为set是没有顺序的，会导致值计算错误
        self.vectorized_func = lambdify(
            self.variables,
            self.expression,
            modules=[{
                'max': np.maximum,
                'min': np.minimum,
                '&': np.logical_and,
                '|': np.logical_or,
                '==': np.equal,
                '>': np.greater,
                '<': np.less,
                '>=': np.greater_equal,
                '<=': np.less_equal
            }, 'numpy']
        )

    def calculate_dataframe(self, df):
        # 确保 DataFrame 中包含表达式需要的所有变量
        required_columns = [str(x) for x in self.variables]
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # 使用矢量化函数计算
        return self.vectorized_func(*(df[col] for col in required_columns))


def calculate_expression(expression, df):
    """接口函数，直接传入表达式和 DataFrame 进行计算"""
    calculator = ExpressionCache.get_calculator(expression)
    return calculator.calculate_dataframe(df)

def cal_exp(exp: str, values: Union[dict, DataFrame]):
    try:
        if isinstance(values, dict):
            # 将表达式字符串转换为 SymPy 表达式
            expression = sympify(exp)
            expression = expression.subs(values)
            # 如果结果是布尔值（BooleanTrue 或 BooleanFalse）
            if isinstance(expression, Boolean):
                return bool(expression)  # 返回Python的布尔类型
            # 如果结果是浮动类型，计算并返回浮动值
            else:
                return float(expression.evalf()) if expression.is_number else expression
        else:
            calculator = ExpressionCache.get_calculator(exp)
            return calculator.calculate_dataframe(values)
    except Exception as e:
        raise MathsException(f"表达式{exp}计算错误：{str(e)}", data={'values': values})

# t = cal_exp('a+b+c', {'a': 1, 'b': 2, 'c': 3})
# print(t)