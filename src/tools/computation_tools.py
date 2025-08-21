"""
Computation and calculation tools.
"""
import ast
import operator
import math
import re
from typing import Any, Dict, List
import asyncio

import sys
from pathlib import Path

# Ensure proper path setup
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

from base import BaseTool, ToolResult, ToolCategory, register_tool


@register_tool
class CalculatorTool(BaseTool):
    """Advanced calculator that can handle mathematical expressions."""
    
    def __init__(self):
        super().__init__()
        self.category = ToolCategory.COMPUTATION
        self.description = "Evaluate mathematical expressions safely"
        
        # Safe operators and functions
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.BitXor: operator.xor,
            ast.USub: operator.neg,
        }
        
        self.functions = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'pi': math.pi,
            'e': math.e,
        }
    
    def _safe_eval(self, node):
        """Safely evaluate an AST node."""
        if isinstance(node, ast.Constant):  # Python 3.8+ (handles numbers, strings, etc.)
            return node.value
        elif hasattr(ast, 'Num') and isinstance(node, ast.Num):  # Backward compatibility
            return node.n
        elif isinstance(node, ast.BinOp):  # Binary operations
            left = self._safe_eval(node.left)
            right = self._safe_eval(node.right)
            return self.operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):  # Unary operations
            operand = self._safe_eval(node.operand)
            return self.operators[type(node.op)](operand)
        elif isinstance(node, ast.Call):  # Function calls
            if isinstance(node.func, ast.Name) and node.func.id in self.functions:
                args = [self._safe_eval(arg) for arg in node.args]
                return self.functions[node.func.id](*args)
            else:
                raise ValueError(f"Function not allowed: {node.func.id}")
        elif isinstance(node, ast.Name):  # Variables/constants
            if node.id in self.functions:
                return self.functions[node.id]
            else:
                raise ValueError(f"Variable not allowed: {node.id}")
        elif isinstance(node, ast.List):  # Lists
            return [self._safe_eval(item) for item in node.elts]
        else:
            raise ValueError(f"Operation not allowed: {type(node)}")
    
    async def execute(self, expression: str) -> ToolResult:
        """Execute mathematical calculation."""
        try:
            # Clean the expression
            expression = expression.strip()
            
            # Handle simple number extraction for basic queries
            if "sum" in expression.lower() or "add" in expression.lower():
                numbers = re.findall(r'-?\d+\.?\d*', expression)
                if numbers:
                    result = sum(float(n) for n in numbers)
                    return ToolResult(
                        success=True,
                        data={
                            "expression": expression,
                            "result": result,
                            "numbers_found": numbers
                        }
                    )
            
            # Parse and evaluate the expression
            tree = ast.parse(expression, mode='eval')
            result = self._safe_eval(tree.body)
            
            return ToolResult(
                success=True,
                data={
                    "expression": expression,
                    "result": result,
                    "type": type(result).__name__
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Calculation failed: {str(e)}"
            )


@register_tool
class CodeExecutorTool(BaseTool):
    """Execute Python code in a safe environment."""
    
    def __init__(self):
        super().__init__()
        self.category = ToolCategory.COMPUTATION
        self.description = "Execute Python code safely with limited scope"
    
    async def execute(self, code: str, timeout: int = 10) -> ToolResult:
        """Execute Python code."""
        from config import settings
        
        if not settings.enable_code_execution:
            return ToolResult(
                success=False,
                error="Code execution is disabled"
            )
        
        try:
            # Create a restricted environment
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'sorted': sorted,
                    'sum': sum,
                    'min': min,
                    'max': max,
                    'abs': abs,
                    'round': round,
                    'int': int,
                    'float': float,
                    'str': str,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                },
                'math': math,
            }
            
            # Capture output
            import io
            import sys
            from contextlib import redirect_stdout, redirect_stderr
            
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Execute with timeout
            async def run_code():
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    exec(code, safe_globals)
            
            try:
                await asyncio.wait_for(run_code(), timeout=timeout)
                
                output = stdout_capture.getvalue()
                errors = stderr_capture.getvalue()
                
                return ToolResult(
                    success=True,
                    data={
                        "code": code,
                        "output": output,
                        "errors": errors if errors else None
                    }
                )
            
            except asyncio.TimeoutError:
                return ToolResult(
                    success=False,
                    error=f"Code execution timed out after {timeout} seconds"
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Code execution failed: {str(e)}"
            )


@register_tool
class UnitConverterTool(BaseTool):
    """Convert between different units of measurement."""
    
    def __init__(self):
        super().__init__()
        self.category = ToolCategory.COMPUTATION
        self.description = "Convert between different units of measurement"
        
        # Conversion factors to base units
        self.conversions = {
            # Length (base: meters)
            'length': {
                'mm': 0.001,
                'cm': 0.01,
                'm': 1.0,
                'km': 1000.0,
                'in': 0.0254,
                'ft': 0.3048,
                'yd': 0.9144,
                'mi': 1609.34,
            },
            # Weight (base: grams)
            'weight': {
                'mg': 0.001,
                'g': 1.0,
                'kg': 1000.0,
                'oz': 28.3495,
                'lb': 453.592,
            },
            # Temperature (special handling)
            'temperature': {
                'c': 'celsius',
                'f': 'fahrenheit',
                'k': 'kelvin',
            }
        }
    
    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert temperature between different scales."""
        # Convert to Celsius first
        if from_unit == 'f':
            celsius = (value - 32) * 5/9
        elif from_unit == 'k':
            celsius = value - 273.15
        else:  # from_unit == 'c'
            celsius = value
        
        # Convert from Celsius to target
        if to_unit == 'f':
            return celsius * 9/5 + 32
        elif to_unit == 'k':
            return celsius + 273.15
        else:  # to_unit == 'c'
            return celsius
    
    async def execute(self, value: float, from_unit: str, to_unit: str) -> ToolResult:
        """Execute unit conversion."""
        try:
            from_unit = from_unit.lower()
            to_unit = to_unit.lower()
            
            # Find the category
            category = None
            for cat, units in self.conversions.items():
                if from_unit in units and to_unit in units:
                    category = cat
                    break
            
            if not category:
                return ToolResult(
                    success=False,
                    error=f"Cannot convert from '{from_unit}' to '{to_unit}'"
                )
            
            if category == 'temperature':
                result = self._convert_temperature(value, from_unit, to_unit)
            else:
                # Convert to base unit, then to target unit
                base_value = value * self.conversions[category][from_unit]
                result = base_value / self.conversions[category][to_unit]
            
            return ToolResult(
                success=True,
                data={
                    "original_value": value,
                    "from_unit": from_unit,
                    "to_unit": to_unit,
                    "result": result,
                    "category": category
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Unit conversion failed: {str(e)}"
            )