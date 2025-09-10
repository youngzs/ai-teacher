"""
AI教学助手系统 - 代码分析工具类
提供安全的代码执行、语法检查、质量评估等功能

Author: AI Architecture Expert
Date: 2025-09-09
"""

import ast
import sys
import subprocess
import tempfile
import os
import time
import signal
from typing import Dict, Any, List, Optional, Tuple
import threading
import queue
from contextlib import contextmanager
import re
import json
from dataclasses import dataclass

from ..models.teaching_models import ProgrammingLanguage, ErrorType, CodeError
from .logger import get_logger

logger = get_logger(__name__)

@dataclass
class ExecutionResult:
    """代码执行结果"""
    success: bool
    output: str
    error: str
    execution_time: float
    memory_usage: Optional[float] = None
    exit_code: Optional[int] = None

class TimeoutError(Exception):
    """执行超时异常"""
    pass

class CodeExecutor:
    """安全的代码执行器"""
    
    def __init__(self, max_execution_time: int = 10):
        self.max_execution_time = max_execution_time
        self.restricted_imports = {
            'os', 'sys', 'subprocess', 'shutil', 'glob', 'socket', 
            'urllib', 'http', 'ftplib', 'smtplib', 'pickle', 'eval', 'exec'
        }
    
    async def execute_safely(self, code: str, language: str = "python", timeout: int = None) -> ExecutionResult:
        """
        安全执行学生代码
        
        Args:
            code: 要执行的代码
            language: 编程语言类型
            timeout: 超时时间（秒）
            
        Returns:
            ExecutionResult: 执行结果
        """
        timeout = timeout or self.max_execution_time
        
        try:
            if language.lower() == "python":
                return await self._execute_python_code(code, timeout)
            elif language.lower() == "c":
                return await self._execute_c_code(code, timeout)
            else:
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"Unsupported language: {language}",
                    execution_time=0.0
                )
                
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=0.0
            )
    
    async def _execute_python_code(self, code: str, timeout: int) -> ExecutionResult:
        """执行Python代码"""
        
        # 安全检查
        if not self._is_python_code_safe(code):
            return ExecutionResult(
                success=False,
                output="",
                error="代码包含不安全的操作，执行被阻止",
                execution_time=0.0
            )
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            start_time = time.time()
            
            # 使用subprocess执行代码
            process = subprocess.Popen(
                [sys.executable, temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=process.returncode == 0,
                output=stdout,
                error=stderr,
                execution_time=execution_time,
                exit_code=process.returncode
            )
            
        except subprocess.TimeoutExpired:
            process.kill()
            return ExecutionResult(
                success=False,
                output="",
                error=f"代码执行超时（>{timeout}秒）",
                execution_time=float(timeout)
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=0.0
            )
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass
    
    async def _execute_c_code(self, code: str, timeout: int) -> ExecutionResult:
        """执行C代码"""
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(code)
            c_file = f.name
        
        executable = c_file.replace('.c', '')
        
        try:
            start_time = time.time()
            
            # 编译C代码
            compile_process = subprocess.Popen(
                ['gcc', '-o', executable, c_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            compile_stdout, compile_stderr = compile_process.communicate()
            
            if compile_process.returncode != 0:
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"编译错误:\n{compile_stderr}",
                    execution_time=time.time() - start_time
                )
            
            # 执行编译后的程序
            run_process = subprocess.Popen(
                [executable],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            
            stdout, stderr = run_process.communicate(timeout=timeout)
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=run_process.returncode == 0,
                output=stdout,
                error=stderr,
                execution_time=execution_time,
                exit_code=run_process.returncode
            )
            
        except subprocess.TimeoutExpired:
            run_process.kill()
            return ExecutionResult(
                success=False,
                output="",
                error=f"程序执行超时（>{timeout}秒）",
                execution_time=float(timeout)
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=0.0
            )
        finally:
            # 清理临时文件
            for temp_path in [c_file, executable]:
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except:
                    pass
    
    def _is_python_code_safe(self, code: str) -> bool:
        """检查Python代码是否安全"""
        try:
            # 解析AST以检查危险操作
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # 检查危险的import
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.restricted_imports:
                            return False
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.restricted_imports:
                        return False
                
                # 检查危险的函数调用
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec', 'compile', '__import__']:
                            return False
            
            return True
            
        except SyntaxError:
            # 语法错误的代码也需要让学生看到错误信息
            return True
        except Exception as e:
            logger.warning(f"Code safety check failed: {e}")
            return False

class StaticCodeAnalyzer:
    """静态代码分析器"""
    
    def __init__(self, language: ProgrammingLanguage):
        self.language = language
        
    def analyze_code_quality(self, code: str) -> Dict[str, Any]:
        """分析代码质量"""
        try:
            if self.language == ProgrammingLanguage.PYTHON:
                return self._analyze_python_quality(code)
            elif self.language == ProgrammingLanguage.C:
                return self._analyze_c_quality(code)
            else:
                return {"error": f"Unsupported language: {self.language}"}
                
        except Exception as e:
            logger.error(f"Code quality analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_python_quality(self, code: str) -> Dict[str, Any]:
        """分析Python代码质量"""
        issues = []
        suggestions = []
        strengths = []
        
        try:
            tree = ast.parse(code)
            
            # 代码结构分析
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            # 命名规范检查
            naming_issues = self._check_python_naming(tree)
            issues.extend(naming_issues)
            
            # 复杂度分析
            complexity = self._calculate_cyclomatic_complexity(tree)
            if complexity > 10:
                issues.append({
                    "type": "complexity",
                    "message": "代码复杂度较高，建议分解为更小的函数",
                    "severity": "medium"
                })
            
            # 代码长度检查
            lines = code.split('\n')
            if len(lines) > 100:
                suggestions.append("代码较长，考虑分解为多个函数或模块")
            
            # 注释检查
            comment_ratio = self._calculate_comment_ratio(code)
            if comment_ratio < 0.1:
                suggestions.append("建议添加更多注释来解释代码逻辑")
            elif comment_ratio > 0.3:
                strengths.append("代码注释充分，有助于理解")
            
            # 函数设计检查
            if functions:
                strengths.append("良好的函数化设计")
                for func in functions:
                    if len(func.body) > 20:
                        suggestions.append(f"函数 '{func.name}' 较长，建议分解")
            
            return {
                "issues": issues,
                "suggestions": suggestions,
                "strengths": strengths,
                "complexity": complexity,
                "comment_ratio": comment_ratio,
                "function_count": len(functions),
                "class_count": len(classes)
            }
            
        except SyntaxError as e:
            return {
                "syntax_error": {
                    "message": str(e),
                    "line": e.lineno,
                    "offset": e.offset
                }
            }
    
    def _analyze_c_quality(self, code: str) -> Dict[str, Any]:
        """分析C代码质量"""
        issues = []
        suggestions = []
        strengths = []
        
        # 基础的正则表达式分析（更复杂的分析需要C解析器）
        lines = code.split('\n')
        
        # 检查include语句
        includes = [line for line in lines if line.strip().startswith('#include')]
        if includes:
            strengths.append("正确使用头文件包含")
        
        # 检查main函数
        main_pattern = r'int\s+main\s*\('
        if re.search(main_pattern, code):
            strengths.append("包含标准的main函数")
        
        # 检查变量声明
        variable_declarations = len(re.findall(r'\b(int|float|double|char|long|short)\s+\w+', code))
        if variable_declarations > 0:
            strengths.append("有明确的变量声明")
        
        # 检查常见错误模式
        if '=' in code and '==' in code:
            # 检查可能的赋值/比较混淆
            assignment_in_condition = re.search(r'if\s*\([^)]*=(?!=)[^)]*\)', code)
            if assignment_in_condition:
                issues.append({
                    "type": "logic",
                    "message": "if语句中可能错误使用了赋值操作符",
                    "severity": "high"
                })
        
        # 检查数组边界
        array_access = re.findall(r'\w+\[\w+\]', code)
        if array_access:
            suggestions.append("注意检查数组访问边界，避免越界错误")
        
        # 检查指针操作
        pointer_usage = len(re.findall(r'\*\w+', code))
        if pointer_usage > 0:
            suggestions.append("使用指针时要注意内存管理和空指针检查")
        
        return {
            "issues": issues,
            "suggestions": suggestions,
            "strengths": strengths,
            "include_count": len(includes),
            "variable_declarations": variable_declarations,
            "pointer_usage": pointer_usage
        }
    
    def _check_python_naming(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """检查Python命名规范"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    issues.append({
                        "type": "naming",
                        "message": f"函数名 '{node.name}' 不符合Python命名规范（应使用小写+下划线）",
                        "severity": "low",
                        "line": node.lineno
                    })
            
            elif isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][A-Za-z0-9]*$', node.name):
                    issues.append({
                        "type": "naming", 
                        "message": f"类名 '{node.name}' 不符合Python命名规范（应使用驼峰命名）",
                        "severity": "low",
                        "line": node.lineno
                    })
            
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                if re.match(r'^[A-Z_][A-Z0-9_]*$', node.id) and len(node.id) > 1:
                    # 可能是常量，这是正确的
                    continue
                elif not re.match(r'^[a-z_][a-z0-9_]*$', node.id):
                    issues.append({
                        "type": "naming",
                        "message": f"变量名 '{node.id}' 不符合Python命名规范",
                        "severity": "low",
                        "line": getattr(node, 'lineno', 0)
                    })
        
        return issues
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                # and/or操作增加复杂度
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_comment_ratio(self, code: str) -> float:
        """计算注释比例"""
        lines = code.split('\n')
        total_lines = len([line for line in lines if line.strip()])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        if total_lines == 0:
            return 0.0
        
        return comment_lines / total_lines

class PerformanceAnalyzer:
    """性能分析器"""
    
    def analyze_algorithm_complexity(self, code: str, language: ProgrammingLanguage) -> Dict[str, Any]:
        """分析算法复杂度"""
        try:
            if language == ProgrammingLanguage.PYTHON:
                return self._analyze_python_complexity(code)
            else:
                return {"message": "复杂度分析暂不支持此语言"}
                
        except Exception as e:
            logger.error(f"Complexity analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_python_complexity(self, code: str) -> Dict[str, Any]:
        """分析Python代码的时间复杂度"""
        try:
            tree = ast.parse(code)
            
            nested_loops = 0
            max_nesting = 0
            current_nesting = 0
            
            class ComplexityVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.loop_nesting = 0
                    self.max_nesting = 0
                    self.has_recursion = False
                
                def visit_For(self, node):
                    self.loop_nesting += 1
                    self.max_nesting = max(self.max_nesting, self.loop_nesting)
                    self.generic_visit(node)
                    self.loop_nesting -= 1
                
                def visit_While(self, node):
                    self.loop_nesting += 1
                    self.max_nesting = max(self.max_nesting, self.loop_nesting)
                    self.generic_visit(node)
                    self.loop_nesting -= 1
                
                def visit_Call(self, node):
                    if isinstance(node.func, ast.Name):
                        # 检查是否有递归调用的迹象
                        # 这里简化处理，实际需要更复杂的分析
                        pass
                    self.generic_visit(node)
            
            visitor = ComplexityVisitor()
            visitor.visit(tree)
            
            # 基于循环嵌套层数估算复杂度
            if visitor.max_nesting == 0:
                complexity = "O(1)"
            elif visitor.max_nesting == 1:
                complexity = "O(n)"
            elif visitor.max_nesting == 2:
                complexity = "O(n²)"
            elif visitor.max_nesting == 3:
                complexity = "O(n³)"
            else:
                complexity = f"O(n^{visitor.max_nesting})"
            
            return {
                "time_complexity": complexity,
                "max_loop_nesting": visitor.max_nesting,
                "analysis": f"基于{visitor.max_nesting}层循环嵌套的复杂度分析"
            }
            
        except Exception as e:
            return {"error": f"复杂度分析失败: {str(e)}"}

# 测试函数
def test_code_executor():
    """测试代码执行器"""
    executor = CodeExecutor()
    
    # 测试Python代码
    python_code = """
for i in range(5):
    print(f"Hello {i}")
"""
    
    import asyncio
    result = asyncio.run(executor.execute_safely(python_code, "python"))
    print(f"Python执行结果: {result}")
    
    # 测试代码分析
    analyzer = StaticCodeAnalyzer(ProgrammingLanguage.PYTHON)
    quality_result = analyzer.analyze_code_quality(python_code)
    print(f"质量分析结果: {quality_result}")

if __name__ == "__main__":
    test_code_executor()