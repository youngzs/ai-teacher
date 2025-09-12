"""
AI教学助手系统 - 增强的多维度代码分析器
Sprint 2 优化：语法分析、逻辑评估、性能分析、风格检查

Author: AI Architecture Expert  
Date: 2025-09-11
Version: Sprint 2 - Enhanced Analysis
"""

import ast
import re
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import tokenize
import io
from collections import defaultdict, Counter
import subprocess
import tempfile
import os

logger = logging.getLogger(__name__)

class AnalysisDimension(Enum):
    """分析维度"""
    SYNTAX = "syntax"
    LOGIC = "logic"
    STYLE = "style"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"

class IssueLevel(Enum):
    """问题严重程度"""
    CRITICAL = "critical"    # 关键错误，导致无法运行
    HIGH = "high"           # 高优先级问题
    MEDIUM = "medium"       # 中等优先级问题
    LOW = "low"            # 低优先级问题
    INFO = "info"          # 信息性提示

@dataclass
class AnalysisIssue:
    """分析问题"""
    dimension: AnalysisDimension
    level: IssueLevel
    message: str
    line_number: Optional[int] = None
    column: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    rule_id: Optional[str] = None
    confidence: float = 1.0

@dataclass
class AnalysisMetrics:
    """分析指标"""
    lines_of_code: int = 0
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    function_count: int = 0
    class_count: int = 0
    comment_ratio: float = 0.0
    avg_function_length: float = 0.0
    max_nested_depth: int = 0
    unique_operators: int = 0
    unique_operands: int = 0

@dataclass
class CodeAnalysisResult:
    """代码分析结果"""
    language: str
    overall_score: float
    dimension_scores: Dict[AnalysisDimension, float] = field(default_factory=dict)
    issues: List[AnalysisIssue] = field(default_factory=list)
    metrics: AnalysisMetrics = field(default_factory=AnalysisMetrics)
    suggestions: List[str] = field(default_factory=list)
    execution_result: Optional[Dict[str, Any]] = None
    analysis_time: float = 0.0
    
    def get_issues_by_level(self, level: IssueLevel) -> List[AnalysisIssue]:
        """按严重程度获取问题"""
        return [issue for issue in self.issues if issue.level == level]
    
    def get_issues_by_dimension(self, dimension: AnalysisDimension) -> List[AnalysisIssue]:
        """按维度获取问题"""
        return [issue for issue in self.issues if issue.dimension == dimension]

class PythonSyntaxAnalyzer:
    """Python语法分析器"""
    
    def __init__(self):
        self.common_errors = {
            "IndentationError": "缩进错误，Python使用缩进来表示代码块",
            "SyntaxError": "语法错误，请检查代码语法",
            "NameError": "名称错误，使用了未定义的变量或函数",
            "TypeError": "类型错误，操作不兼容的数据类型",
            "ValueError": "值错误，函数参数类型正确但值不合适",
            "IndexError": "索引错误，访问了不存在的索引",
            "KeyError": "键错误，访问了不存在的字典键"
        }
    
    def analyze(self, code: str) -> Tuple[List[AnalysisIssue], float]:
        """分析Python代码语法"""
        issues = []
        syntax_score = 100.0
        
        try:
            # 尝试解析AST
            tree = ast.parse(code)
            
            # 检查语法规范性
            issues.extend(self._check_naming_conventions(tree))
            issues.extend(self._check_import_statements(tree))
            issues.extend(self._check_function_definitions(tree))
            issues.extend(self._check_class_definitions(tree))
            
        except SyntaxError as e:
            # 语法错误
            error_type = type(e).__name__
            description = self.common_errors.get(error_type, str(e))
            
            issues.append(AnalysisIssue(
                dimension=AnalysisDimension.SYNTAX,
                level=IssueLevel.CRITICAL,
                message=f"{error_type}: {description}",
                line_number=e.lineno,
                column=e.offset,
                suggestion="请修复语法错误后重新提交",
                rule_id="SYNTAX_001"
            ))
            syntax_score = 0.0
            
        except Exception as e:
            issues.append(AnalysisIssue(
                dimension=AnalysisDimension.SYNTAX,
                level=IssueLevel.HIGH,
                message=f"代码分析错误: {str(e)}",
                suggestion="请检查代码是否为有效的Python代码",
                rule_id="SYNTAX_002"
            ))
            syntax_score = 20.0
        
        # 根据问题数量调整分数
        for issue in issues:
            if issue.level == IssueLevel.CRITICAL:
                syntax_score = max(0, syntax_score - 50)
            elif issue.level == IssueLevel.HIGH:
                syntax_score = max(0, syntax_score - 20)
            elif issue.level == IssueLevel.MEDIUM:
                syntax_score = max(0, syntax_score - 10)
            elif issue.level == IssueLevel.LOW:
                syntax_score = max(0, syntax_score - 5)
        
        return issues, syntax_score
    
    def _check_naming_conventions(self, tree: ast.AST) -> List[AnalysisIssue]:
        """检查命名约定"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    issues.append(AnalysisIssue(
                        dimension=AnalysisDimension.STYLE,
                        level=IssueLevel.LOW,
                        message=f"函数名 '{node.name}' 不符合Python命名约定",
                        line_number=node.lineno,
                        suggestion="函数名应该使用小写字母和下划线",
                        rule_id="NAMING_001"
                    ))
            
            elif isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    issues.append(AnalysisIssue(
                        dimension=AnalysisDimension.STYLE,
                        level=IssueLevel.LOW,
                        message=f"类名 '{node.name}' 不符合Python命名约定",
                        line_number=node.lineno,
                        suggestion="类名应该使用大写字母开头的驼峰命名",
                        rule_id="NAMING_002"
                    ))
        
        return issues
    
    def _check_import_statements(self, tree: ast.AST) -> List[AnalysisIssue]:
        """检查import语句"""
        issues = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
        
        # 检查import顺序和分组
        if len(imports) > 1:
            # 简化的import顺序检查
            stdlib_imports = []
            third_party_imports = []
            
            for imp in imports:
                if isinstance(imp, ast.Import):
                    for alias in imp.names:
                        if alias.name in ['os', 'sys', 'json', 'time', 're']:
                            stdlib_imports.append((imp.lineno, alias.name))
                        else:
                            third_party_imports.append((imp.lineno, alias.name))
        
        return issues
    
    def _check_function_definitions(self, tree: ast.AST) -> List[AnalysisIssue]:
        """检查函数定义"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数长度
                function_lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 1
                if function_lines > 50:
                    issues.append(AnalysisIssue(
                        dimension=AnalysisDimension.MAINTAINABILITY,
                        level=IssueLevel.MEDIUM,
                        message=f"函数 '{node.name}' 过长 ({function_lines} 行)",
                        line_number=node.lineno,
                        suggestion="考虑将长函数拆分为多个小函数",
                        rule_id="FUNC_001"
                    ))
                
                # 检查参数数量
                if len(node.args.args) > 7:
                    issues.append(AnalysisIssue(
                        dimension=AnalysisDimension.MAINTAINABILITY,
                        level=IssueLevel.MEDIUM,
                        message=f"函数 '{node.name}' 参数过多 ({len(node.args.args)} 个)",
                        line_number=node.lineno,
                        suggestion="考虑使用字典或类来传递多个参数",
                        rule_id="FUNC_002"
                    ))
                
                # 检查docstring
                if not ast.get_docstring(node):
                    issues.append(AnalysisIssue(
                        dimension=AnalysisDimension.STYLE,
                        level=IssueLevel.LOW,
                        message=f"函数 '{node.name}' 缺少文档字符串",
                        line_number=node.lineno,
                        suggestion="添加docstring来描述函数的功能",
                        rule_id="DOC_001"
                    ))
        
        return issues
    
    def _check_class_definitions(self, tree: ast.AST) -> List[AnalysisIssue]:
        """检查类定义"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查类docstring
                if not ast.get_docstring(node):
                    issues.append(AnalysisIssue(
                        dimension=AnalysisDimension.STYLE,
                        level=IssueLevel.LOW,
                        message=f"类 '{node.name}' 缺少文档字符串",
                        line_number=node.lineno,
                        suggestion="添加docstring来描述类的功能",
                        rule_id="DOC_002"
                    ))
        
        return issues

class PythonLogicAnalyzer:
    """Python逻辑分析器"""
    
    def analyze(self, code: str, execution_result: Optional[Dict] = None) -> Tuple[List[AnalysisIssue], float]:
        """分析代码逻辑"""
        issues = []
        logic_score = 100.0
        
        try:
            tree = ast.parse(code)
            
            # 逻辑复杂度分析
            complexity_issues, complexity_score = self._analyze_complexity(tree)
            issues.extend(complexity_issues)
            
            # 控制流分析
            control_flow_issues, control_flow_score = self._analyze_control_flow(tree)
            issues.extend(control_flow_issues)
            
            # 变量使用分析
            variable_issues, variable_score = self._analyze_variables(tree)
            issues.extend(variable_issues)
            
            # 异常处理分析
            exception_issues, exception_score = self._analyze_exception_handling(tree)
            issues.extend(exception_issues)
            
            # 综合逻辑分数
            logic_score = (complexity_score + control_flow_score + 
                          variable_score + exception_score) / 4
            
            # 如果有执行结果，分析运行时行为
            if execution_result:
                runtime_issues = self._analyze_runtime_behavior(execution_result)
                issues.extend(runtime_issues)
            
        except Exception as e:
            issues.append(AnalysisIssue(
                dimension=AnalysisDimension.LOGIC,
                level=IssueLevel.HIGH,
                message=f"逻辑分析错误: {str(e)}",
                rule_id="LOGIC_ERROR"
            ))
            logic_score = 50.0
        
        return issues, logic_score
    
    def _analyze_complexity(self, tree: ast.AST) -> Tuple[List[AnalysisIssue], float]:
        """分析圈复杂度"""
        issues = []
        complexity_score = 100.0
        
        complexity_analyzer = CyclomaticComplexityAnalyzer()
        complexity_map = complexity_analyzer.analyze(tree)
        
        for func_name, complexity in complexity_map.items():
            if complexity > 10:
                issues.append(AnalysisIssue(
                    dimension=AnalysisDimension.LOGIC,
                    level=IssueLevel.HIGH,
                    message=f"函数 '{func_name}' 圈复杂度过高 ({complexity})",
                    suggestion="考虑拆分函数或简化逻辑",
                    rule_id="COMPLEXITY_001"
                ))
                complexity_score -= 15
            elif complexity > 7:
                issues.append(AnalysisIssue(
                    dimension=AnalysisDimension.LOGIC,
                    level=IssueLevel.MEDIUM,
                    message=f"函数 '{func_name}' 圈复杂度较高 ({complexity})",
                    suggestion="考虑简化函数逻辑",
                    rule_id="COMPLEXITY_002"
                ))
                complexity_score -= 8
        
        return issues, max(0, complexity_score)
    
    def _analyze_control_flow(self, tree: ast.AST) -> Tuple[List[AnalysisIssue], float]:
        """分析控制流"""
        issues = []
        flow_score = 100.0
        
        for node in ast.walk(tree):
            # 检查深度嵌套
            if isinstance(node, (ast.If, ast.For, ast.While)):
                nesting_depth = self._calculate_nesting_depth(node)
                if nesting_depth > 4:
                    issues.append(AnalysisIssue(
                        dimension=AnalysisDimension.LOGIC,
                        level=IssueLevel.MEDIUM,
                        message=f"嵌套层数过深 ({nesting_depth} 层)",
                        line_number=node.lineno,
                        suggestion="考虑提取函数或使用早期返回来减少嵌套",
                        rule_id="NESTING_001"
                    ))
                    flow_score -= 10
            
            # 检查无限循环风险
            if isinstance(node, ast.While):
                if self._is_potential_infinite_loop(node):
                    issues.append(AnalysisIssue(
                        dimension=AnalysisDimension.LOGIC,
                        level=IssueLevel.HIGH,
                        message="潜在的无限循环风险",
                        line_number=node.lineno,
                        suggestion="确保循环条件会在某个时候变为False",
                        rule_id="LOOP_001"
                    ))
                    flow_score -= 20
        
        return issues, max(0, flow_score)
    
    def _analyze_variables(self, tree: ast.AST) -> Tuple[List[AnalysisIssue], float]:
        """分析变量使用"""
        issues = []
        variable_score = 100.0
        
        variable_analyzer = VariableUsageAnalyzer()
        unused_vars, undefined_vars = variable_analyzer.analyze(tree)
        
        for var_name, line_num in unused_vars:
            issues.append(AnalysisIssue(
                dimension=AnalysisDimension.LOGIC,
                level=IssueLevel.LOW,
                message=f"未使用的变量: '{var_name}'",
                line_number=line_num,
                suggestion="删除未使用的变量或确认是否遗漏了使用",
                rule_id="VAR_001"
            ))
            variable_score -= 5
        
        for var_name, line_num in undefined_vars:
            issues.append(AnalysisIssue(
                dimension=AnalysisDimension.LOGIC,
                level=IssueLevel.CRITICAL,
                message=f"使用了未定义的变量: '{var_name}'",
                line_number=line_num,
                suggestion="确保变量在使用前已被定义",
                rule_id="VAR_002"
            ))
            variable_score -= 20
        
        return issues, max(0, variable_score)
    
    def _analyze_exception_handling(self, tree: ast.AST) -> Tuple[List[AnalysisIssue], float]:
        """分析异常处理"""
        issues = []
        exception_score = 100.0
        
        has_risky_operations = False
        has_exception_handling = False
        
        for node in ast.walk(tree):
            # 检查是否有异常处理
            if isinstance(node, ast.Try):
                has_exception_handling = True
                
                # 检查是否有裸露的except
                for handler in node.handlers:
                    if handler.type is None:
                        issues.append(AnalysisIssue(
                            dimension=AnalysisDimension.LOGIC,
                            level=IssueLevel.MEDIUM,
                            message="使用了裸露的except语句",
                            line_number=node.lineno,
                            suggestion="指定具体的异常类型",
                            rule_id="EXCEPT_001"
                        ))
                        exception_score -= 10
            
            # 检查可能引发异常的操作
            elif isinstance(node, (ast.Call, ast.Subscript, ast.BinOp)):
                has_risky_operations = True
        
        # 如果有风险操作但没有异常处理
        if has_risky_operations and not has_exception_handling:
            issues.append(AnalysisIssue(
                dimension=AnalysisDimension.LOGIC,
                level=IssueLevel.LOW,
                message="代码中存在可能引发异常的操作但没有异常处理",
                suggestion="考虑添加适当的异常处理",
                rule_id="EXCEPT_002"
            ))
            exception_score -= 15
        
        return issues, max(0, exception_score)
    
    def _analyze_runtime_behavior(self, execution_result: Dict) -> List[AnalysisIssue]:
        """分析运行时行为"""
        issues = []
        
        if not execution_result.get("success", False):
            error = execution_result.get("error", "")
            if error:
                issues.append(AnalysisIssue(
                    dimension=AnalysisDimension.LOGIC,
                    level=IssueLevel.CRITICAL,
                    message=f"运行时错误: {error}",
                    suggestion="修复导致运行时错误的问题",
                    rule_id="RUNTIME_001"
                ))
        
        # 检查执行时间
        execution_time = execution_result.get("execution_time", 0)
        if execution_time > 5000:  # 5秒
            issues.append(AnalysisIssue(
                dimension=AnalysisDimension.PERFORMANCE,
                level=IssueLevel.MEDIUM,
                message=f"代码执行时间较长 ({execution_time}ms)",
                suggestion="考虑优化算法或减少不必要的计算",
                rule_id="PERF_001"
            ))
        
        return issues
    
    def _calculate_nesting_depth(self, node: ast.AST, depth: int = 0) -> int:
        """计算嵌套深度"""
        max_depth = depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._calculate_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _is_potential_infinite_loop(self, while_node: ast.While) -> bool:
        """检查是否可能是无限循环"""
        # 简化的检查：如果条件是常量True
        if isinstance(while_node.test, ast.Constant) and while_node.test.value is True:
            # 检查循环体中是否有break语句
            for node in ast.walk(while_node):
                if isinstance(node, ast.Break):
                    return False
            return True
        return False

class CyclomaticComplexityAnalyzer:
    """圈复杂度分析器"""
    
    def analyze(self, tree: ast.AST) -> Dict[str, int]:
        """分析圈复杂度"""
        complexity_map = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                complexity_map[node.name] = complexity
        
        return complexity_map
    
    def _calculate_complexity(self, func_node: ast.FunctionDef) -> int:
        """计算函数的圈复杂度"""
        complexity = 1  # 基础复杂度
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                # and/or操作增加复杂度
                complexity += len(node.values) - 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
        
        return complexity

class VariableUsageAnalyzer:
    """变量使用分析器"""
    
    def analyze(self, tree: ast.AST) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]]]:
        """分析变量使用情况"""
        defined_vars = set()
        used_vars = set()
        assigned_vars = {}  # {var_name: line_number}
        used_undefined = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined_vars.add(target.id)
                        assigned_vars[target.id] = node.lineno
            
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_vars.add(node.id)
                if node.id not in defined_vars and node.id not in ['print', 'len', 'range', 'int', 'str', 'float', 'list', 'dict']:
                    used_undefined.append((node.id, node.lineno))
        
        unused_vars = [(var, line) for var, line in assigned_vars.items() if var not in used_vars]
        
        return unused_vars, used_undefined

class PythonPerformanceAnalyzer:
    """Python性能分析器"""
    
    def __init__(self):
        self.performance_patterns = {
            "list_comprehension": r"\[.*for.*in.*\]",
            "generator_expression": r"\(.*for.*in.*\)",
            "string_concatenation": r".*\+\s*['\"].*",
            "global_variable": r"global\s+\w+"
        }
    
    def analyze(self, code: str, execution_result: Optional[Dict] = None) -> Tuple[List[AnalysisIssue], float]:
        """分析代码性能"""
        issues = []
        performance_score = 100.0
        
        try:
            tree = ast.parse(code)
            
            # 分析算法复杂度
            complexity_issues, complexity_penalty = self._analyze_algorithm_complexity(tree)
            issues.extend(complexity_issues)
            performance_score -= complexity_penalty
            
            # 分析数据结构使用
            data_structure_issues, ds_penalty = self._analyze_data_structures(tree)
            issues.extend(data_structure_issues)
            performance_score -= ds_penalty
            
            # 分析循环效率
            loop_issues, loop_penalty = self._analyze_loops(tree)
            issues.extend(loop_issues)
            performance_score -= loop_penalty
            
            # 分析字符串操作
            string_issues, string_penalty = self._analyze_string_operations(code)
            issues.extend(string_issues)
            performance_score -= string_penalty
            
            # 如果有执行结果，分析实际性能
            if execution_result:
                runtime_issues, runtime_penalty = self._analyze_runtime_performance(execution_result)
                issues.extend(runtime_issues)
                performance_score -= runtime_penalty
            
        except Exception as e:
            issues.append(AnalysisIssue(
                dimension=AnalysisDimension.PERFORMANCE,
                level=IssueLevel.MEDIUM,
                message=f"性能分析错误: {str(e)}",
                rule_id="PERF_ERROR"
            ))
            performance_score = 70.0
        
        return issues, max(0, performance_score)
    
    def _analyze_algorithm_complexity(self, tree: ast.AST) -> Tuple[List[AnalysisIssue], float]:
        """分析算法复杂度"""
        issues = []
        penalty = 0.0
        
        for node in ast.walk(tree):
            # 检查嵌套循环
            if isinstance(node, (ast.For, ast.While)):
                nested_loops = self._count_nested_loops(node)
                if nested_loops > 2:
                    issues.append(AnalysisIssue(
                        dimension=AnalysisDimension.PERFORMANCE,
                        level=IssueLevel.HIGH,
                        message=f"检测到{nested_loops}层嵌套循环，时间复杂度可能很高",
                        line_number=node.lineno,
                        suggestion="考虑优化算法或使用更高效的数据结构",
                        rule_id="PERF_002"
                    ))
                    penalty += 20
                elif nested_loops > 1:
                    issues.append(AnalysisIssue(
                        dimension=AnalysisDimension.PERFORMANCE,
                        level=IssueLevel.MEDIUM,
                        message=f"检测到{nested_loops}层嵌套循环",
                        line_number=node.lineno,
                        suggestion="注意时间复杂度，考虑是否有优化空间",
                        rule_id="PERF_003"
                    ))
                    penalty += 10
        
        return issues, penalty
    
    def _analyze_data_structures(self, tree: ast.AST) -> Tuple[List[AnalysisIssue], float]:
        """分析数据结构使用"""
        issues = []
        penalty = 0.0
        
        for node in ast.walk(tree):
            # 检查列表中的查找操作
            if isinstance(node, ast.Compare):
                for op, comparator in zip(node.ops, node.comparators):
                    if isinstance(op, ast.In) and isinstance(node.left, ast.Name):
                        # 建议使用set进行成员检查
                        issues.append(AnalysisIssue(
                            dimension=AnalysisDimension.PERFORMANCE,
                            level=IssueLevel.LOW,
                            message="在列表中进行成员检查，考虑使用set提高效率",
                            line_number=node.lineno,
                            suggestion="如果需要频繁检查成员关系，使用set而不是list",
                            rule_id="PERF_004"
                        ))
                        penalty += 5
        
        return issues, penalty
    
    def _analyze_loops(self, tree: ast.AST) -> Tuple[List[AnalysisIssue], float]:
        """分析循环效率"""
        issues = []
        penalty = 0.0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # 检查是否在循环中进行了不必要的重复计算
                if self._has_repeated_computation_in_loop(node):
                    issues.append(AnalysisIssue(
                        dimension=AnalysisDimension.PERFORMANCE,
                        level=IssueLevel.MEDIUM,
                        message="循环中可能存在重复计算",
                        line_number=node.lineno,
                        suggestion="将不变的计算移到循环外部",
                        rule_id="PERF_005"
                    ))
                    penalty += 10
        
        return issues, penalty
    
    def _analyze_string_operations(self, code: str) -> Tuple[List[AnalysisIssue], float]:
        """分析字符串操作"""
        issues = []
        penalty = 0.0
        
        lines = code.split('\n')
        for i, line in enumerate(lines):
            # 检查字符串拼接
            if '+' in line and ('"' in line or "'" in line):
                # 简单检查是否是字符串拼接
                if re.search(r'["\'].*\+.*["\']', line):
                    issues.append(AnalysisIssue(
                        dimension=AnalysisDimension.PERFORMANCE,
                        level=IssueLevel.LOW,
                        message="使用+进行字符串拼接，考虑使用join()或f-string",
                        line_number=i + 1,
                        suggestion="使用join()方法或f-string格式化",
                        rule_id="PERF_006"
                    ))
                    penalty += 3
        
        return issues, penalty
    
    def _analyze_runtime_performance(self, execution_result: Dict) -> Tuple[List[AnalysisIssue], float]:
        """分析运行时性能"""
        issues = []
        penalty = 0.0
        
        execution_time = execution_result.get("execution_time", 0)
        
        if execution_time > 3000:  # 3秒
            issues.append(AnalysisIssue(
                dimension=AnalysisDimension.PERFORMANCE,
                level=IssueLevel.HIGH,
                message=f"代码执行时间过长: {execution_time}ms",
                suggestion="优化算法复杂度或减少不必要的计算",
                rule_id="PERF_007"
            ))
            penalty += 25
        elif execution_time > 1000:  # 1秒
            issues.append(AnalysisIssue(
                dimension=AnalysisDimension.PERFORMANCE,
                level=IssueLevel.MEDIUM,
                message=f"代码执行时间较长: {execution_time}ms",
                suggestion="考虑性能优化",
                rule_id="PERF_008"
            ))
            penalty += 10
        
        return issues, penalty
    
    def _count_nested_loops(self, node: ast.AST, depth: int = 1) -> int:
        """计算嵌套循环深度"""
        max_depth = depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                child_depth = self._count_nested_loops(child, depth + 1)
                max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _has_repeated_computation_in_loop(self, loop_node: ast.For) -> bool:
        """检查循环中是否有重复计算"""
        # 简化的检查：查找函数调用
        for node in ast.walk(loop_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                # 如果在循环中多次调用同一个函数，可能是重复计算
                return True
        return False

class EnhancedCodeAnalyzer:
    """增强的代码分析器主类"""
    
    def __init__(self):
        self.python_syntax_analyzer = PythonSyntaxAnalyzer()
        self.python_logic_analyzer = PythonLogicAnalyzer()
        self.python_performance_analyzer = PythonPerformanceAnalyzer()
        
    def analyze_code(self, code: str, language: str = "python", 
                    execution_result: Optional[Dict] = None) -> CodeAnalysisResult:
        """综合代码分析"""
        start_time = time.time()
        
        if language.lower() == "python":
            return self._analyze_python(code, execution_result)
        else:
            # 其他语言的分析器可以在这里添加
            return CodeAnalysisResult(
                language=language,
                overall_score=0.0,
                issues=[AnalysisIssue(
                    dimension=AnalysisDimension.SYNTAX,
                    level=IssueLevel.CRITICAL,
                    message=f"不支持的编程语言: {language}",
                    rule_id="LANG_001"
                )]
            )
    
    def _analyze_python(self, code: str, execution_result: Optional[Dict] = None) -> CodeAnalysisResult:
        """分析Python代码"""
        start_time = time.time()
        
        # 语法分析
        syntax_issues, syntax_score = self.python_syntax_analyzer.analyze(code)
        
        # 逻辑分析
        logic_issues, logic_score = self.python_logic_analyzer.analyze(code, execution_result)
        
        # 性能分析
        performance_issues, performance_score = self.python_performance_analyzer.analyze(code, execution_result)
        
        # 计算代码指标
        metrics = self._calculate_metrics(code)
        
        # 综合所有问题
        all_issues = syntax_issues + logic_issues + performance_issues
        
        # 计算维度分数
        dimension_scores = {
            AnalysisDimension.SYNTAX: syntax_score,
            AnalysisDimension.LOGIC: logic_score,
            AnalysisDimension.PERFORMANCE: performance_score,
            AnalysisDimension.STYLE: self._calculate_style_score(syntax_issues),
            AnalysisDimension.MAINTAINABILITY: self._calculate_maintainability_score(all_issues, metrics)
        }
        
        # 计算总体分数
        overall_score = sum(dimension_scores.values()) / len(dimension_scores)
        
        # 生成改进建议
        suggestions = self._generate_suggestions(all_issues, dimension_scores)
        
        analysis_time = time.time() - start_time
        
        return CodeAnalysisResult(
            language="python",
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            issues=all_issues,
            metrics=metrics,
            suggestions=suggestions,
            execution_result=execution_result,
            analysis_time=analysis_time
        )
    
    def _calculate_metrics(self, code: str) -> AnalysisMetrics:
        """计算代码指标"""
        try:
            tree = ast.parse(code)
            
            metrics = AnalysisMetrics()
            metrics.lines_of_code = len([line for line in code.split('\n') if line.strip()])
            
            # 统计函数和类
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics.function_count += 1
                elif isinstance(node, ast.ClassDef):
                    metrics.class_count += 1
            
            # 计算圈复杂度
            complexity_analyzer = CyclomaticComplexityAnalyzer()
            complexity_map = complexity_analyzer.analyze(tree)
            if complexity_map:
                metrics.cyclomatic_complexity = max(complexity_map.values())
            
            # 计算注释比例
            comment_lines = len([line for line in code.split('\n') 
                               if line.strip().startswith('#')])
            if metrics.lines_of_code > 0:
                metrics.comment_ratio = comment_lines / metrics.lines_of_code
            
            # 平均函数长度
            if metrics.function_count > 0:
                total_function_lines = 0
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 1
                        total_function_lines += func_lines
                metrics.avg_function_length = total_function_lines / metrics.function_count
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics calculation error: {e}")
            return AnalysisMetrics()
    
    def _calculate_style_score(self, syntax_issues: List[AnalysisIssue]) -> float:
        """计算代码风格分数"""
        style_issues = [issue for issue in syntax_issues if issue.dimension == AnalysisDimension.STYLE]
        style_score = 100.0
        
        for issue in style_issues:
            if issue.level == IssueLevel.HIGH:
                style_score -= 15
            elif issue.level == IssueLevel.MEDIUM:
                style_score -= 10
            elif issue.level == IssueLevel.LOW:
                style_score -= 5
        
        return max(0, style_score)
    
    def _calculate_maintainability_score(self, all_issues: List[AnalysisIssue], 
                                       metrics: AnalysisMetrics) -> float:
        """计算可维护性分数"""
        maintainability_issues = [issue for issue in all_issues 
                                if issue.dimension == AnalysisDimension.MAINTAINABILITY]
        
        maintainability_score = 100.0
        
        # 基于问题扣分
        for issue in maintainability_issues:
            if issue.level == IssueLevel.HIGH:
                maintainability_score -= 20
            elif issue.level == IssueLevel.MEDIUM:
                maintainability_score -= 10
            elif issue.level == IssueLevel.LOW:
                maintainability_score -= 5
        
        # 基于指标调整分数
        if metrics.avg_function_length > 30:
            maintainability_score -= 10
        
        if metrics.cyclomatic_complexity > 10:
            maintainability_score -= 15
        
        if metrics.comment_ratio < 0.1:  # 注释少于10%
            maintainability_score -= 10
        
        return max(0, maintainability_score)
    
    def _generate_suggestions(self, issues: List[AnalysisIssue], 
                            dimension_scores: Dict[AnalysisDimension, float]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 找出分数最低的维度
        lowest_dimension = min(dimension_scores.keys(), key=lambda k: dimension_scores[k])
        lowest_score = dimension_scores[lowest_dimension]
        
        if lowest_score < 60:
            suggestions.append(f"重点改进{lowest_dimension.value}相关问题")
        
        # 基于严重问题生成建议
        critical_issues = [issue for issue in issues if issue.level == IssueLevel.CRITICAL]
        if critical_issues:
            suggestions.append("首先解决所有严重错误（Critical级别）")
        
        high_issues = [issue for issue in issues if issue.level == IssueLevel.HIGH]
        if len(high_issues) > 3:
            suggestions.append("减少高优先级问题的数量")
        
        # 维度特定建议
        if dimension_scores.get(AnalysisDimension.PERFORMANCE, 100) < 70:
            suggestions.append("考虑优化算法复杂度和数据结构使用")
        
        if dimension_scores.get(AnalysisDimension.MAINTAINABILITY, 100) < 70:
            suggestions.append("提高代码可维护性：添加注释、拆分长函数、降低复杂度")
        
        return suggestions

# 导出主要类
__all__ = [
    'EnhancedCodeAnalyzer', 'CodeAnalysisResult', 'AnalysisIssue', 
    'AnalysisDimension', 'IssueLevel', 'AnalysisMetrics'
]