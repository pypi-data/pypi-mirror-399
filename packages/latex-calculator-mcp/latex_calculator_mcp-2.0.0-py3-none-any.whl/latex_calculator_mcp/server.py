#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LaTeX公式计算MCP服务
提供LaTeX数学公式的计算功能
使用latex2sympy2和sympy库实现计算功能
"""

import os
import tempfile
import logging
import traceback
import re
import math
import threading
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, Optional, List, Union
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError

from mcp.server.fastmcp import FastMCP, Context
from latex2sympy2 import latex2sympy
import sympy as sp

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(tempfile.gettempdir(), "latex_calculator_mcp_server.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LaTeX_Calculator_MCPServer")

class CalculationError(Exception):
    """计算错误基类"""
    pass

class TimeoutError(CalculationError):
    """计算超时错误"""
    pass

class MathDomainError(CalculationError):
    """数学域错误（如参数超出定义域）"""
    pass

class ParseError(CalculationError):
    """LaTeX解析错误"""
    pass

class ValidationError(CalculationError):
    """输入验证错误"""
    pass

class LaTeXCalculator:
    """LaTeX公式计算器类，提供计算LaTeX数学公式的功能"""

    # 常量定义
    RAD_TO_DEG = 180 / sp.pi
    DEG_TO_RAD = sp.pi / 180

    # 超时配置（秒）
    DEFAULT_TIMEOUT = 10
    MAX_EXPRESSION_LENGTH = 10000

    def __init__(self):
        self.last_expression = None
        self.last_result = None
        self._history_lock = threading.Lock()  # 保护历史记录的线程锁

        # 预编译常用正则表达式
        self.inverse_trig_pattern = re.compile(r'\\(?:arc|a)(sin|cos|tan|cot|sec|csc)')
        self.degree_symbol_patterns = [
            re.compile(r'{\^\\circ}'),
            re.compile(r'\^{\\circ}'),
            re.compile(r'\^\\circ'),
            re.compile(r'\\circ'),
            re.compile(r'°')
        ]
        # DMS正则模式（按优先级顺序）
        # 1. 完整DMS: 162°2'3'' 或 162d2m3s
        self.dms_full_pattern = re.compile(
            r"(-?\d+(?:\.\d+)?)[°d]\s*"
            r"(\d+(?:\.\d+)?)['\u2032m]\s*"
            r"(\d+(?:\.\d+)?)(''|\"|"
            r"\u2033|s)"
        )
        # 2. 度+秒（缺分）: 162°3''
        self.dms_degree_second_pattern = re.compile(
            r"(-?\d+(?:\.\d+)?)[°d]\s*"
            r"(\d+(?:\.\d+)?)(''|\"|"
            r"\u2033|s)"
        )
        # 3. 度+分（缺秒）: 162°2'
        self.dms_degree_minute_pattern = re.compile(
            r"(-?\d+(?:\.\d+)?)[°d]\s*"
            r"(\d+(?:\.\d+)?)['\u2032m]"
        )
        # 4. 只有度: 162°
        self.dms_degree_only_pattern = re.compile(
            r"(-?\d+(?:\.\d+)?)[°d]"
        )
        # 5. 分+秒（缺度）: 44'30''
        # 改进：允许前面有括号、正号或表达式开头
        self.dms_minute_second_pattern = re.compile(
            r"(?<![°d])([+-]?\d+(?:\.\d+)?)['\u2032m]\s*"
            r"(\d+(?:\.\d+)?)(''|\"|"
            r"\u2033|s)"
        )
        # 6. 只有分: 44' 或 44m (但不能匹配 44'' 的第一个')
        # 改进：允许前面有括号、正号、运算符或表达式开头
        self.dms_minute_only_pattern = re.compile(
            r"(?<![°d\d.])([+-]?\d+(?:\.\d+)?)'(?![''\"\u2033s])"
        )
        # 6b. 只有分(字母格式): 44m (必须是单独的m，后面不能跟数字或s)
        self.dms_minute_only_letter_pattern = re.compile(
            r"(?<![°d\d.])([+-]?\d+(?:\.\d+)?)m(?![0-9s])"
        )
        # 7. 只有秒: 44'' (必须是两个连续的引号)
        # 改进：允许前面有括号、正号、运算符或表达式开头
        self.dms_second_only_pattern = re.compile(
            r"(?<![°d'\u2032m\d.])([+-]?\d+(?:\.\d+)?)''(?!')"
        )
        # 7b. 只有秒(字母格式): 44s (必须是单独的s)
        self.dms_second_only_letter_pattern = re.compile(
            r"(?<![°d'\u2032m\d.])([+-]?\d+(?:\.\d+)?)s(?![a-z])"
        )

        # DMS 模式列表（按优先级排序，从复杂到简单）
        # 每个元素: (模式名称, 编译后的正则表达式)
        self.dms_patterns_ordered = [
            ("完整DMS", self.dms_full_pattern),
            ("度+秒", self.dms_degree_second_pattern),
            ("度+分", self.dms_degree_minute_pattern),
            ("只有度", self.dms_degree_only_pattern),
            ("分+秒", self.dms_minute_second_pattern),
            ("只有分", self.dms_minute_only_pattern),
            ("只有分(字母)", self.dms_minute_only_letter_pattern),
            ("只有秒", self.dms_second_only_pattern),
            ("只有秒(字母)", self.dms_second_only_letter_pattern),
        ]

    def _execute_with_timeout(self, func, timeout: float = None, *args, **kwargs):
        """
        在指定超时时间内执行函数

        Args:
            func: 要执行的函数
            timeout: 超时时间（秒），None 使用默认值
            *args, **kwargs: 传递给函数的参数

        Returns:
            函数执行结果

        Raises:
            TimeoutError: 执行超时
        """
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            try:
                return future.result(timeout=timeout)
            except FuturesTimeoutError:
                raise TimeoutError(f"计算超时（超过 {timeout} 秒）")

    def _make_dms_replacer(self, pattern_name: str):
        """
        创建 DMS 替换器函数

        Args:
            pattern_name: 模式名称，用于日志记录

        Returns:
            替换器函数，可用于 re.sub()
        """
        def replacer(match):
            try:
                decimal = self.parse_dms_to_decimal(match.group(0))
                return self._format_decimal_for_latex(decimal)
            except Exception as e:
                logger.warning(f"{pattern_name}转换失败: {match.group(0)}, 错误: {e}")
                return match.group(0)
        return replacer

    def parse_dms_to_decimal(self, dms_str: str, degrees: float = 0, minutes: float = 0, seconds: float = 0) -> float:
        """
        将度分秒格式转换为十进制度数

        支持多种格式:
        - 完整: 162°2'3'', 162d2m3s
        - 度+分: 162°2', 162d2m
        - 度+秒: 162°3'', 162d3s
        - 只有度: 162°, 162d
        - 分+秒: 44'30'', 44m30s
        - 只有分: 44', 44m
        - 只有秒: 44'', 44s
        - 负数: 所有格式支持负号

        Args:
            dms_str: 度分秒格式字符串（可选，如果提供则解析）
            degrees: 度数（如已解析则直接传入）
            minutes: 分数（如已解析则直接传入）
            seconds: 秒数（如已解析则直接传入）

        Returns:
            十进制度数

        Examples:
            parse_dms_to_decimal("162°2'3''") -> 162.03416666...
            parse_dms_to_decimal("162°3''") -> 162.00083333...
            parse_dms_to_decimal("44'30''") -> 0.74166666...
            parse_dms_to_decimal("44'") -> 0.73333333...
            parse_dms_to_decimal("44''") -> 0.01222222...
        """
        # 检测原始字符串是否以负号开头（用于处理 -0° 的情况）
        is_negative_from_string = dms_str.strip().startswith('-') if dms_str else False

        # 如果提供了字符串，尝试解析
        if dms_str:
            # 尝试各种格式（按优先级）
            # 1. 完整DMS: 162°2'3''
            match = self.dms_full_pattern.match(dms_str.strip())
            if match:
                degrees = float(match.group(1))
                minutes = float(match.group(2))
                seconds = float(match.group(3))
            else:
                # 2. 度+秒: 162°3''
                match = self.dms_degree_second_pattern.match(dms_str.strip())
                if match:
                    degrees = float(match.group(1))
                    minutes = 0.0
                    seconds = float(match.group(2))
                else:
                    # 3. 度+分: 162°2'
                    match = self.dms_degree_minute_pattern.match(dms_str.strip())
                    if match:
                        degrees = float(match.group(1))
                        minutes = float(match.group(2))
                        seconds = 0.0
                    else:
                        # 4. 只有度: 162°
                        match = self.dms_degree_only_pattern.match(dms_str.strip())
                        if match:
                            degrees = float(match.group(1))
                            minutes = 0.0
                            seconds = 0.0
                        else:
                            # 5. 分+秒: 44'30''
                            match = self.dms_minute_second_pattern.match(dms_str.strip())
                            if match:
                                degrees = 0.0
                                minutes = float(match.group(1))
                                seconds = float(match.group(2))
                            else:
                                # 6. 只有分: 44'
                                match = self.dms_minute_only_pattern.match(dms_str.strip())
                                if match:
                                    degrees = 0.0
                                    minutes = float(match.group(1))
                                    seconds = 0.0
                                else:
                                    # 6b. 只有分(字母格式): 44m
                                    match = self.dms_minute_only_letter_pattern.match(dms_str.strip())
                                    if match:
                                        degrees = 0.0
                                        minutes = float(match.group(1))
                                        seconds = 0.0
                                    else:
                                        # 7. 只有秒: 44''
                                        match = self.dms_second_only_pattern.match(dms_str.strip())
                                        if match:
                                            degrees = 0.0
                                            minutes = 0.0
                                            seconds = float(match.group(1))
                                        else:
                                            # 7b. 只有秒(字母格式): 44s
                                            match = self.dms_second_only_letter_pattern.match(dms_str.strip())
                                            if match:
                                                degrees = 0.0
                                                minutes = 0.0
                                                seconds = float(match.group(1))
                                            else:
                                                raise ParseError(f"无法解析度分秒格式: {dms_str}")

        # 验证分秒范围
        if not (0 <= abs(minutes) < 60):
            raise ValidationError(f"分的值必须在0-59之间: {minutes}")
        if not (0 <= abs(seconds) < 60):
            raise ValidationError(f"秒的值必须在0-59之间: {seconds}")

        # 验证小数逻辑：如果度有小数，分和秒应该为0；如果分有小数，秒应该为0
        degrees_has_decimal = degrees != int(degrees)
        minutes_has_decimal = minutes != int(minutes)

        if degrees_has_decimal and (minutes != 0 or seconds != 0):
            logger.warning(f"度有小数({degrees})但分({minutes})或秒({seconds})不为0，可能导致精度问题")

        if minutes_has_decimal and seconds != 0:
            logger.warning(f"分有小数({minutes})但秒({seconds})不为0，可能导致精度问题")

        # 转换为十进制度数
        decimal = abs(degrees) + abs(minutes) / 60.0 + abs(seconds) / 3600.0

        # 处理负数（检查度数符号或原始字符串的负号）
        # 注意：Python 中 -0.0 < 0 为 False，所以需要检查原始字符串
        is_negative = (
            degrees < 0 or
            is_negative_from_string or
            (degrees == 0 and minutes < 0) or
            (degrees == 0 and minutes == 0 and seconds < 0)
        )
        if is_negative:
            decimal = -decimal

        # 记录日志
        if dms_str:
            logger.info(f"DMS转换: {dms_str} -> {decimal}°")
        else:
            logger.info(f"DMS转换: {degrees}°{minutes}'{seconds}'' -> {decimal}°")

        return decimal

    def decimal_to_dms(self, decimal: float, precision: int = 2) -> str:
        """
        将十进制度数转换为度分秒格式

        Args:
            decimal: 十进制度数
            precision: 秒的小数位数

        Returns:
            度分秒格式字符串

        Examples:
            162.03416666... -> 162°2'3.00''
            -45.50416666... -> -45°30'15.00''
        """
        is_negative = decimal < 0
        decimal = abs(decimal)

        degrees = int(decimal)
        minutes_decimal = (decimal - degrees) * 60
        minutes = int(minutes_decimal)
        seconds = (minutes_decimal - minutes) * 60

        # 处理舍入导致的进位
        if round(seconds, precision) >= 60:
            seconds = 0
            minutes += 1
        if minutes >= 60:
            minutes = 0
            degrees += 1

        sign = '-' if is_negative else ''
        return f"{sign}{degrees}°{minutes}'{seconds:.{precision}f}''"

    def _format_decimal_for_latex(self, value: float) -> str:
        """
        将十进制数格式化为LaTeX友好的字符串（避免科学计数法）

        Args:
            value: 十进制数值

        Returns:
            格式化后的字符串，不使用科学计数法
        """
        # 使用定点数格式，避免科学计数法被latex2sympy误解析
        # 保留足够的精度（15位有效数字）
        if value == 0:
            return "0"
        elif abs(value) < 1e-10:
            # 对于极小值，使用高精度定点格式
            return f"{value:.15f}".rstrip('0').rstrip('.')
        else:
            # 普通数值
            formatted = f"{value:.15g}"
            # 如果包含科学计数法，转换为定点格式
            if 'e' in formatted.lower():
                formatted = f"{value:.15f}".rstrip('0').rstrip('.')
            return formatted

    def preprocess_dms_in_expression(self, latex_expr: str) -> str:
        """
        预处理表达式中的度分秒格式，转换为十进制度数

        支持所有DMS格式组合:
        - 完整: 162°2'3''
        - 度+分: 162°2'
        - 度+秒: 162°3''
        - 只有度: 162°
        - 分+秒: 44'30''
        - 只有分: 44'
        - 只有秒: 44''
        - 负数: 所有格式

        Args:
            latex_expr: 包含DMS格式的LaTeX表达式

        Returns:
            转换后的表达式（DMS转为十进制）
        """
        original_expr = latex_expr

        # 预处理：统一度数符号格式
        # 将各种度数符号格式统一为 ° 符号，便于后续正则匹配
        # 注意：这里只替换数字后面的度数符号，避免影响其他地方
        latex_expr = re.sub(r'(\d+)\s*\^\{\\circ\}', r'\1°', latex_expr)  # 处理 ^{\circ}（带花括号）
        latex_expr = re.sub(r'(\d+)\s*\^\\circ', r'\1°', latex_expr)  # 处理 ^\circ（不带花括号）
        latex_expr = re.sub(r'(\d+)\s*\\circ', r'\1°', latex_expr)  # 处理 \circ

        # 按优先级处理所有 DMS 模式（从复杂到简单，避免误匹配）
        for pattern_name, pattern in self.dms_patterns_ordered:
            latex_expr = pattern.sub(self._make_dms_replacer(pattern_name), latex_expr)

        # 清理残留的度数符号
        latex_expr = re.sub(r'(\d+)\^\{\\circ\}', r'\1', latex_expr)  # 移除 ^{\circ}
        latex_expr = re.sub(r'(\d+)\^\\circ', r'\1', latex_expr)  # 移除 ^\circ
        latex_expr = re.sub(r'(\d+)\\circ', r'\1', latex_expr)  # 移除 \circ
        latex_expr = re.sub(r'(\d+)°', r'\1', latex_expr)  # 移除 ° 符号

        # 记录转换
        if latex_expr != original_expr:
            logger.info(f"DMS预处理: {original_expr} -> {latex_expr}")

        return latex_expr

    def extract_latex_argument(self, latex_expr, start_pos):
        """提取LaTeX命令的参数，支持任何形式的参数"""
        i = start_pos
        # 跳过空白字符
        while i < len(latex_expr) and latex_expr[i].isspace():
            i += 1

        if i >= len(latex_expr):
            return None, i

        if latex_expr[i] == '{':
            # 处理花括号参数
            open_braces = 1
            j = i + 1
            while j < len(latex_expr) and open_braces > 0:
                if latex_expr[j] == '{':
                    open_braces += 1
                elif latex_expr[j] == '}':
                    open_braces -= 1
                j += 1
            return latex_expr[i+1:j-1], j
        elif latex_expr[i] == '(':
            # 处理圆括号参数
            open_parens = 1
            j = i + 1
            while j < len(latex_expr) and open_parens > 0:
                if latex_expr[j] == '(':
                    open_parens += 1
                elif latex_expr[j] == ')':
                    open_parens -= 1
                j += 1
            return latex_expr[i+1:j-1], j
        elif latex_expr[i] == '\\':
            # 这是另一个LaTeX命令
            command_match = re.match(r'\\[a-zA-Z]+', latex_expr[i:])
            if not command_match:
                return None, i

            command_name = command_match.group(0)
            j = i + len(command_name)

            # 收集该命令的所有参数
            args = []
            while j < len(latex_expr):
                # 检查是否还有下一个参数
                next_char = latex_expr[j] if j < len(latex_expr) else None
                if next_char in ['{', '(', '\\']:
                    arg, j = self.extract_latex_argument(latex_expr, j)
                    if arg is not None:
                        args.append(arg)
                else:
                    break

            # 根据命令名和参数构建完整的LaTeX表达式
            full_command = command_name
            for arg in args:
                full_command += '{' + arg + '}'

            return full_command, j
        else:
            # 处理单个字符或数字
            return latex_expr[i], i + 1

    def process_latex_expression(self, latex_expr):
        """处理完整的LaTeX表达式，评估其值"""
        try:
            # 尝试直接计算表达式值
            sympy_expr = latex2sympy(latex_expr)
            return str(float(sympy_expr.evalf()))
        except Exception as e:
            logger.warning(f"直接计算LaTeX表达式失败: {str(e)}")
            return latex_expr

    def process_inverse_trig(self, latex_expr, degree=True):
        """处理LaTeX表达式中的反三角函数，支持任何形式的参数"""
        logger.debug(f"处理可能存在反三角函数的表达式: {latex_expr}")

        # 查找反三角函数（使用预编译的正则）
        match = self.inverse_trig_pattern.search(latex_expr)
        if not match:
            return latex_expr

        # 获取反三角函数名称
        func_name = match.group(1)
        start_pos = match.end()

        # 提取参数
        arg_expr, end_pos = self.extract_latex_argument(latex_expr, start_pos)
        if arg_expr is None:
            logger.warning(f"找不到反三角函数 {func_name} 的参数")
            return latex_expr

        # 递归处理参数中可能存在的其他反三角函数
        processed_arg = self.process_inverse_trig(arg_expr, degree)

        # 尝试计算参数值
        try:
            # 评估参数的值
            arg_value_expr = self.process_latex_expression(processed_arg)
            arg_value = float(arg_value_expr)

            # 根据函数名称计算反三角函数值
            if func_name == 'sin':
                if not (-1 <= arg_value <= 1):
                    raise MathDomainError(f"asin参数 {arg_value} 超出定义域 [-1, 1]")
                result = math.asin(arg_value)
            elif func_name == 'cos':
                if not (-1 <= arg_value <= 1):
                    raise MathDomainError(f"acos参数 {arg_value} 超出定义域 [-1, 1]")
                result = math.acos(arg_value)
            elif func_name == 'tan':
                result = math.atan(arg_value)
            elif func_name == 'cot':
                # acot(x) 主值范围是 (0, π)
                # acot(0) = π/2
                # acot(x) = atan(1/x) 当 x > 0
                # acot(x) = atan(1/x) + π 当 x < 0（调整到正确范围）
                if arg_value == 0:
                    result = math.pi / 2
                elif arg_value > 0:
                    result = math.atan(1/arg_value)
                else:
                    result = math.atan(1/arg_value) + math.pi
            elif func_name == 'sec':
                if arg_value == 0:
                    raise MathDomainError("asec参数不能为0")
                if not (abs(arg_value) >= 1):
                    raise MathDomainError(f"asec参数 {arg_value} 超出定义域 |x| >= 1")
                result = math.acos(1/arg_value)
            elif func_name == 'csc':
                if arg_value == 0:
                    raise MathDomainError("acsc参数不能为0")
                if not (abs(arg_value) >= 1):
                    raise MathDomainError(f"acsc参数 {arg_value} 超出定义域 |x| >= 1")
                result = math.asin(1/arg_value)

            if degree:
                result = result * 180 / math.pi
            logger.debug(f"成功计算反三角函数 a{func_name}({processed_arg}) = {result}")

            # 替换原表达式
            result_str = str(result)
            modified_expr = latex_expr[:match.start()] + result_str + latex_expr[end_pos:]

            # 继续处理可能存在的其他反三角函数
            return self.process_inverse_trig(modified_expr, degree)
        except Exception as e:
            logger.warning(f"计算反三角函数失败: {str(e)}")
            # 如果计算失败，保留原始表达式
            return latex_expr

    def _clean_degree_symbols(self, latex_expr):
        """清理表达式中的度数符号（使用预编译的正则）"""
        # 移除度数符号 \circ、° 等
        for pattern in self.degree_symbol_patterns:
            latex_expr = pattern.sub('', latex_expr)
        return latex_expr

    def _preprocess_trig_functions(self, latex_expr):
        """预处理三角函数，确保参数被正确括起（支持嵌套）"""
        trig_funcs = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc']

        # 使用递归方式处理嵌套的花括号
        def find_matching_brace(s, start):
            """找到与start位置的{匹配的}的位置"""
            if start >= len(s) or s[start] != '{':
                return -1
            count = 1
            i = start + 1
            while i < len(s) and count > 0:
                if s[i] == '{':
                    count += 1
                elif s[i] == '}':
                    count -= 1
                i += 1
            return i - 1 if count == 0 else -1

        def process_expr(expr):
            """递归处理表达式中的三角函数"""
            changed = True
            while changed:
                changed = False
                for func in trig_funcs:
                    pattern = '\\' + func + '{'
                    result = []
                    i = 0
                    while i < len(expr):
                        # 查找三角函数
                        pos = expr.find(pattern, i)
                        if pos == -1:
                            result.append(expr[i:])
                            break

                        # 添加前面的部分
                        result.append(expr[i:pos])

                        # 找到匹配的}
                        brace_start = pos + len(pattern) - 1  # {的位置
                        brace_end = find_matching_brace(expr, brace_start)

                        if brace_end == -1:
                            # 没找到匹配的}，保留原样
                            result.append(expr[pos:pos + len(pattern)])
                            i = pos + len(pattern)
                        else:
                            # 提取参数内容
                            arg_content = expr[brace_start + 1:brace_end]
                            # 递归处理参数内容中可能的嵌套三角函数
                            processed_arg = process_expr(arg_content)
                            # 转换为圆括号形式
                            result.append('\\' + func + '(' + processed_arg + ')')
                            i = brace_end + 1
                            changed = True

                    expr = ''.join(result)
            return expr

        latex_expr = process_expr(latex_expr)

        # 处理sqrt函数，将圆括号形式转换为花括号形式
        sqrt_pattern = r'\\sqrt\(([^()]+)\)'
        latex_expr = re.sub(sqrt_pattern, r'\\sqrt{\1}', latex_expr)

        return latex_expr

    def _convert_degrees_to_radians(self, sympy_expr):
        """将sympy表达式中的角度转换为弧度（支持嵌套）"""
        trig_funcs = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc']

        # 使用递归方式从内到外处理
        def convert_recursive(expr):
            # 获取函数名（如果有）
            func_name = expr.func.__name__ if hasattr(expr, 'func') else None

            # 检查是否是三角函数
            if func_name in trig_funcs:
                # 先递归处理参数
                if len(expr.args) > 0:
                    converted_arg = convert_recursive(expr.args[0])
                    # 将参数转换为弧度
                    rad_arg = converted_arg * sp.pi / 180
                    # 返回新的三角函数调用
                    func_sympy = getattr(sp, func_name)
                    result = func_sympy(rad_arg)
                    logger.debug(f"转换: {func_name}({expr.args[0]}) -> {func_name}({rad_arg})")
                    return result
                return expr

            # 如果是纯数字或符号（没有子表达式），直接返回
            if not hasattr(expr, 'args') or not expr.args:
                return expr

            # 对于其他函数，递归处理所有参数
            new_args = [convert_recursive(arg) for arg in expr.args]
            return expr.func(*new_args)

        result = convert_recursive(sympy_expr)
        logger.info(f"度转弧度后的表达式: {result}")
        return result

    def _format_result(self, result, decimal_places, scientific_notation):
        """格式化计算结果"""
        if scientific_notation:
            return f"{result:.{decimal_places}e}"
        else:
            return round(result, decimal_places)

    def _format_output(self, original_expr, result, show_formula, display_mode):
        """格式化最终输出"""
        if show_formula:
            if display_mode == 1:
                return f"${original_expr} = {result}$"
            elif display_mode == 2:
                return f"$$\n{original_expr} = {result}\n$$"
            else:
                return f"{original_expr} = {result}"
        else:
            return result

    def calculate_value(self, latex_expr: str, n: int = 2, sci: bool = False,
                       all_formula: bool = False, degree: bool = True,
                       display_mode: int = 0, result_transfer_to_degree: bool = False,
                       output_dms: bool = False) -> Union[str, float]:
        """
        传入latex表达式(不是等式，传入的表达式中不要有变量)，保留小数位数，科学计数法是否为True,是否返回所有公式。支持角度制和弧度制。

        Args:
            latex_expr: str, latex表达式;正确示例: 0.5 \\times 0.1084 \\times 23 \\times (6.71+1.28+0.4+7+7) \\times \\sin{30^\\circ};错误示例e = 0.5 \\times 0.1084 \\times 23 \\times (6.71+1.28+0.4+7+7)
            n: int,默认2，保留小数位数
            sci: bool,默认False，计算结果是否为科学计数法
            all_formula: bool，默认False，是否把答案和原有公式组合后返回
            degree: bool，默认True，传入的表达式和最终的计算结果中的角度是否为度数
            display_mode: int,默认0，公式前后各加上display_mode个$符号
            result_transfer_to_degree: bool,默认False，最终的计算结果是否需要转换为度数
            output_dms: bool,默认False，是否将结果输出为度分秒格式

        Returns:
            计算结果（字符串或浮点数）

        Raises:
            ValidationError: 参数验证失败
            ParseError: LaTeX解析失败
            MathDomainError: 数学域错误
            CalculationError: 其他计算错误
        """
        # 参数验证
        if not isinstance(n, int) or n < 0:
            raise ValidationError(f"小数位数必须是非负整数: {n}")
        if not isinstance(display_mode, int) or display_mode not in [0, 1, 2]:
            raise ValidationError(f"display_mode必须是0, 1或2: {display_mode}")
        if not latex_expr or not latex_expr.strip():
            raise ValidationError("表达式不能为空")
        if len(latex_expr) > self.MAX_EXPRESSION_LENGTH:
            raise ValidationError(f"表达式过长（{len(latex_expr)} > {self.MAX_EXPRESSION_LENGTH}）")

        # 清理多余的反斜杠
        latex_expr = re.sub(r'\\{2,}', r'\\', latex_expr)
        original_expr = latex_expr

        # 保存最后计算的表达式（线程安全）
        with self._history_lock:
            self.last_expression = latex_expr

        logger.info(f"开始计算表达式: {latex_expr}")

        try:
            # 智能处理空格：将多个连续空格替换为单个空格，但保留LaTeX命令后的必要空格
            # 例如 "\sin 30" 需要保留空格，但 "2  +  3" 可以压缩
            latex_expr = re.sub(r'\s+', ' ', latex_expr)  # 多个空格合并为一个
            # 去除运算符周围的空格（保留LaTeX命令后的空格）
            latex_expr = re.sub(r'\s*([+\-*/^=()])\s*', r'\1', latex_expr)
            # 去除花括号周围的空格
            latex_expr = re.sub(r'\s*([{}])\s*', r'\1', latex_expr)

            # 预处理度分秒格式
            latex_expr = self.preprocess_dms_in_expression(latex_expr)
            logger.debug(f"预处理DMS后的表达式: {latex_expr}")

            # 预处理度数符号
            if degree:
                latex_expr = self._clean_degree_symbols(latex_expr)
                logger.debug(f"处理度数符号后的表达式: {latex_expr}")

            # 使用递归方式处理嵌套的反三角函数
            processed_expr = self.process_inverse_trig(latex_expr, degree)
            logger.info(f"处理反三角函数后的表达式: {processed_expr}")

            # 预处理三角函数和其他函数
            processed_expr = self._preprocess_trig_functions(processed_expr)
            logger.info(f"预处理运算符和括号后的表达式: {processed_expr}")

            # 将处理后的LaTeX表达式转换为sympy表达式
            logger.info(f"最终处理后的表达式: {processed_expr}")

            # 定义核心计算函数（用于超时控制）
            # 使用更高精度（50位有效数字）以减少浮点误差
            def _core_calculation(expr_str, convert_degrees):
                sympy_expr = latex2sympy(expr_str)
                logger.info(f"转换为sympy表达式: {sympy_expr}")

                # 如果是角度制，将角度转换为弧度（对于剩余的三角函数）
                if convert_degrees:
                    sympy_expr = self._convert_degrees_to_radians(sympy_expr)

                # 使用高精度计算（50位有效数字），最终转换为float
                high_precision_result = sympy_expr.evalf(50)
                return float(high_precision_result)

            # 使用超时控制执行核心计算
            result = self._execute_with_timeout(_core_calculation, None, processed_expr, degree)
            logger.info(f"计算结果: {result}")

            # 保存最后计算的结果（线程安全）
            with self._history_lock:
                self.last_result = result

            # 转换结果为度数
            if result_transfer_to_degree:
                result = result * 180 / math.pi
                logger.info(f"转换结果为度数: {result}")

            # 格式化结果
            if output_dms:
                # 输出为度分秒格式
                formatted_result = self.decimal_to_dms(result, n)
                logger.info(f"格式化为DMS: {formatted_result}")
            else:
                formatted_result = self._format_result(result, n, sci)
                logger.info(f"格式化后的结果: {formatted_result}")

            # 格式化输出
            return self._format_output(original_expr, formatted_result, all_formula, display_mode)

        except ValidationError as e:
            error_msg = f"参数验证错误: {str(e)}"
            logger.error(error_msg)
            raise
        except ParseError as e:
            error_msg = f"LaTeX解析错误: {str(e)}"
            logger.error(error_msg)
            raise
        except MathDomainError as e:
            error_msg = f"数学域错误: {str(e)}"
            logger.error(error_msg)
            raise
        except TimeoutError as e:
            error_msg = f"计算超时: {str(e)}"
            logger.error(error_msg)
            raise
        except Exception as e:
            error_msg = f"计算错误: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise CalculationError(error_msg) from e

    def calculate_batch(self, latex_exprs: List[str], n: int = 2, sci: bool = False,
                       all_formula: bool = False, degree: bool = True,
                       display_mode: int = 0, result_transfer_to_degree: bool = False,
                       output_dms: bool = False, stop_on_error: bool = False) -> List[Dict[str, Any]]:
        """
        批量计算多个LaTeX表达式（顺序执行）

        Args:
            latex_exprs: LaTeX表达式列表
            n: 保留小数位数，默认2
            sci: 是否使用科学计数法，默认False
            all_formula: 是否返回公式，默认False
            degree: 是否使用角度制，默认True
            display_mode: 公式显示模式 (0/1/2)，默认0
            result_transfer_to_degree: 结果是否转换为度数，默认False
            output_dms: 是否输出度分秒格式，默认False
            stop_on_error: 遇到错误时是否停止计算，默认False

        Returns:
            计算结果列表，每个元素包含:
            - index: 表达式在输入列表中的索引
            - expression: 原始表达式
            - result: 计算结果 (成功时)
            - error: 错误信息 (失败时)
            - success: 是否成功

        Examples:
            >>> calc = LaTeXCalculator()
            >>> results = calc.calculate_batch(["2+3", "\\sin{30}", "4^2"])
            >>> for r in results:
            ...     print(f"{r['expression']} = {r['result']}")
        """
        results = []
        for idx, expr in enumerate(latex_exprs):
            result = {
                "index": idx,
                "expression": expr,
                "success": False,
                "result": None,
                "error": None
            }

            try:
                calculated = self.calculate_value(
                    latex_expr=expr,
                    n=n,
                    sci=sci,
                    all_formula=all_formula,
                    degree=degree,
                    display_mode=display_mode,
                    result_transfer_to_degree=result_transfer_to_degree,
                    output_dms=output_dms
                )
                result["result"] = calculated
                result["success"] = True
                logger.info(f"批量计算[{idx}]: {expr} -> {calculated}")

            except Exception as e:
                result["error"] = str(e)
                logger.error(f"批量计算[{idx}]失败: {expr}, 错误: {e}")

                if stop_on_error:
                    # 停止后续计算
                    result["stop_flag"] = True
                    results.append(result)
                    break

            results.append(result)

        return results

    def calculate_batch_parallel(self, latex_exprs: List[str], n: int = 2, sci: bool = False,
                                 all_formula: bool = False, degree: bool = True,
                                 display_mode: int = 0, result_transfer_to_degree: bool = False,
                                 output_dms: bool = False, max_workers: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        并行计算多个LaTeX表达式

        Args:
            latex_exprs: LaTeX表达式列表
            n: 保留小数位数，默认2
            sci: 是否使用科学计数法，默认False
            all_formula: 是否返回公式，默认False
            degree: 是否使用角度制，默认True
            display_mode: 公式显示模式 (0/1/2)，默认0
            result_transfer_to_degree: 结果是否转换为度数，默认False
            output_dms: 是否输出度分秒格式，默认False
            max_workers: 最大并行工作线程数，默认为None（自动选择）

        Returns:
            计算结果列表（按输入顺序排序），每个元素包含:
            - index: 表达式在输入列表中的索引
            - expression: 原始表达式
            - result: 计算结果 (成功时)
            - error: 错误信息 (失败时)
            - success: 是否成功

        Examples:
            >>> calc = LaTeXCalculator()
            >>> results = calc.calculate_batch_parallel(["2+3", "\\sin{30}", "4^2"], max_workers=4)
            >>> for r in results:
            ...     print(f"{r['expression']} = {r['result']}")
        """
        results = {}

        def calculate_single(idx: int, expr: str) -> Dict[str, Any]:
            """计算单个表达式"""
            result = {
                "index": idx,
                "expression": expr,
                "success": False,
                "result": None,
                "error": None
            }

            try:
                calculated = self.calculate_value(
                    latex_expr=expr,
                    n=n,
                    sci=sci,
                    all_formula=all_formula,
                    degree=degree,
                    display_mode=display_mode,
                    result_transfer_to_degree=result_transfer_to_degree,
                    output_dms=output_dms
                )
                result["result"] = calculated
                result["success"] = True
                logger.info(f"并行计算[{idx}]: {expr} -> {calculated}")

            except Exception as e:
                result["error"] = str(e)
                logger.error(f"并行计算[{idx}]失败: {expr}, 错误: {e}")

            return result

        # 使用线程池并行执行计算
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(calculate_single, idx, expr): idx
                for idx, expr in enumerate(latex_exprs)
            }

            # 收集完成的任务
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    result = future.result()
                    results[idx] = result
                except Exception as e:
                    # 处理任务执行本身的异常
                    results[idx] = {
                        "index": idx,
                        "expression": latex_exprs[idx],
                        "success": False,
                        "result": None,
                        "error": f"任务执行异常: {str(e)}"
                    }
                    logger.error(f"并行计算任务[{idx}]执行异常: {e}")

        # 按原始顺序排序结果
        sorted_results = [results[i] for i in range(len(latex_exprs))]
        return sorted_results


# 创建计算器全局实例
calculator = LaTeXCalculator()

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict, Any]:
    """管理服务器生命周期"""
    try:
        logger.info("LaTeX计算器MCP服务器启动中...")
        yield {"calculator": calculator}
    finally:
        logger.info("LaTeX计算器MCP服务器关闭中...")

# 创建MCP服务器
mcp = FastMCP(
    name="LaTeXCalculator",
    instructions="LaTeX公式计算服务，提供计算LaTeX数学公式的功能",
    lifespan=server_lifespan
)

@mcp.tool()
def calculate_latex(ctx: Context, latex_expr: str, decimal_places: int = 2,
                   scientific_notation: bool = False, show_formula: bool = False,
                   degree: bool = True, result_need_transform_degree: bool = False,
                   display_mode: int = 0, output_dms: bool = False) -> str:
    r"""
    计算LaTeX数学表达式，支持基础运算、三角函数、反三角函数、度分秒(DMS)格式等。

    主要功能:
    - 基础运算: 加减乘除、幂运算、开方、分数
    - 三角函数: sin, cos, tan, cot, sec, csc (支持角度制/弧度制)
    - 反三角函数: asin, acos, atan, acot, asec, acsc
    - 度分秒格式: 162°2'3'', 45°30', 44s, 30m (自动识别转换)
    - 格式化输出: 十进制、科学计数法、度分秒格式

    参数说明:

    latex_expr (必填):
        LaTeX数学表达式字符串，注意LaTeX命令前需要加反斜杠\

        正确示例:
        - 基础运算: "2+3", "10-4", "6 \times 7", "\frac{15}{3}", "2^3", "\sqrt{16}"
        - 三角函数: "\sin{30}", "\cos{60}", "\tan{45}" (度数需配合degree=True)
        - 反三角函数: "\atan{1}", "\asin{0.5}", "\acos{0.5}"
        - 度分秒: "162°2'3'' - 152°2'3''", "44'' / 4", "30s + 15s", "45m / 3"
        - 复合运算: "2 \times \sin{30} + 3 \times \cos{60}"

        错误示例:
        - "e = 2+3" (不要包含等式)
        - "sin(30)" (缺少反斜杠\)
        - "x + 2" (不要包含变量)

    decimal_places (默认2):
        结果保留的小数位数，必须为非负整数

    scientific_notation (默认False):
        是否使用科学计数法输出结果

    show_formula (默认False):
        是否在结果中显示原始公式

    degree (默认True):
        三角函数的角度单位
        True: 输入角度为度数 (sin{30}表示sin(30°))
        False: 输入角度为弧度 (sin{1.5708}表示sin(π/2))

    result_need_transform_degree (默认False):
        是否将弧度结果转换为度数

    display_mode (默认0):
        公式显示格式（配合show_formula使用）
        0: 无符号
        1: 单$ (行内公式)
        2: 双$$ (独立公式)

    output_dms (默认False):
        是否将结果输出为度分秒格式
    """
    try:
        result = calculator.calculate_value(
            latex_expr=latex_expr,
            n=decimal_places,
            sci=scientific_notation,
            all_formula=show_formula,
            degree=degree,
            display_mode=display_mode,
            result_transfer_to_degree=result_need_transform_degree,
            output_dms=output_dms)
        return str(result)
    except ValidationError as e:
        error_msg = f"参数验证错误: {str(e)}"
        logger.error(error_msg)
        return error_msg
    except ParseError as e:
        error_msg = f"LaTeX解析错误: {str(e)}"
        logger.error(error_msg)
        return error_msg
    except MathDomainError as e:
        error_msg = f"数学域错误: {str(e)}"
        logger.error(error_msg)
        return error_msg
    except TimeoutError as e:
        error_msg = f"计算超时: {str(e)}"
        logger.error(error_msg)
        return error_msg
    except CalculationError as e:
        error_msg = f"计算错误: {str(e)}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"未知错误: {str(e)}"
        logger.error(error_msg)
        traceback.print_exc()
        return error_msg

@mcp.tool()
def get_calculation_history(ctx: Context) -> str:
    """
    获取最近一次计算的历史记录，包括原始表达式和计算结果。

    返回值:
    - 有历史记录时: "最近计算的表达式: {表达式}\n计算结果: {结果}"
    - 无历史记录时: "尚未进行过计算"
    """
    try:
        with calculator._history_lock:
            if calculator.last_expression and calculator.last_result is not None:
                return f"最近计算的表达式: {calculator.last_expression}\n计算结果: {calculator.last_result}"
            else:
                return "尚未进行过计算"
    except Exception as e:
        error_msg = f"获取计算历史失败: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool()
def calculate_batch_latex(ctx: Context, latex_exprs: List[str], decimal_places: int = 2,
                         scientific_notation: bool = False, show_formula: bool = False,
                         degree: bool = True, result_need_transform_degree: bool = False,
                         display_mode: int = 0, output_dms: bool = False,
                         stop_on_error: bool = False, parallel: bool = False,
                         max_workers: Optional[int] = None) -> str:
    r"""
    批量计算多个LaTeX数学表达式，支持顺序执行或并行计算。

    主要功能:
    - 一次性计算多个LaTeX表达式
    - 支持顺序执行和并行计算两种模式
    - 每个表达式独立计算，互不影响
    - 返回结构化的计算结果，包含成功/失败状态

    参数说明:

    latex_exprs (必填):
        LaTeX数学表达式列表
        示例: ["2+3", "\\sin{30}", "4^2"]

    parallel (默认False):
        是否使用并行计算模式
        False: 顺序执行
        True: 并行执行

    其他参数与 calculate_latex 相同
    """
    try:
        # 验证输入
        if not isinstance(latex_exprs, list):
            return f"参数错误: latex_exprs必须是列表类型"

        if not latex_exprs:
            return "参数错误: 表达式列表不能为空"

        # 选择计算模式
        if parallel:
            results = calculator.calculate_batch_parallel(
                latex_exprs=latex_exprs,
                n=decimal_places,
                sci=scientific_notation,
                all_formula=show_formula,
                degree=degree,
                display_mode=display_mode,
                result_transfer_to_degree=result_need_transform_degree,
                output_dms=output_dms,
                max_workers=max_workers
            )
            mode_str = "并行"
        else:
            results = calculator.calculate_batch(
                latex_exprs=latex_exprs,
                n=decimal_places,
                sci=scientific_notation,
                all_formula=show_formula,
                degree=degree,
                display_mode=display_mode,
                result_transfer_to_degree=result_need_transform_degree,
                output_dms=output_dms,
                stop_on_error=stop_on_error
            )
            mode_str = "顺序"

        # 统计结果
        success_count = sum(1 for r in results if r["success"])
        fail_count = len(results) - success_count

        # 格式化输出
        output_lines = [
            f"批量计算完成 ({mode_str}模式)",
            f"总计: {len(results)} 个表达式",
            f"成功: {success_count} 个",
            f"失败: {fail_count} 个",
            "",
            "详细结果:"
        ]

        for r in results:
            if r["success"]:
                output_lines.append(f"[{r['index']}] {r['expression']} = {r['result']}")
            else:
                output_lines.append(f"[{r['index']}] {r['expression']} -> 错误: {r['error']}")

        return "\n".join(output_lines)

    except Exception as e:
        error_msg = f"批量计算错误: {str(e)}"
        logger.error(error_msg)
        traceback.print_exc()
        return error_msg
