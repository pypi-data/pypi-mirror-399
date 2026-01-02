"""
LaTeX Calculator MCP Server

一个强大的LaTeX数学公式计算MCP服务，支持基础运算、三角函数、反三角函数、度分秒(DMS)格式。

使用方法:
    uvx latex-calculator-mcp

或在 MCP 配置中:
    {
        "mcpServers": {
            "latex_calculator": {
                "command": "uvx",
                "args": ["latex-calculator-mcp"]
            }
        }
    }
"""

__version__ = "2.0.1"
__author__ = "Your Name"

from .server import mcp, calculator, LaTeXCalculator

def main():
    """MCP服务器入口点"""
    mcp.run()

__all__ = ["main", "mcp", "calculator", "LaTeXCalculator", "__version__"]
