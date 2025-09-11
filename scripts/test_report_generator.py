#!/usr/bin/env python3
"""
测试报告生成器
生成综合测试报告和质量分析报告
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import glob
import re


class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, output_dir: str = "test-reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 测试类型配置
        self.test_types = {
            "unit": {
                "name": "单元测试",
                "pattern": "**/junit.xml",
                "weight": 0.3
            },
            "integration": {
                "name": "集成测试", 
                "pattern": "**/integration-junit.xml",
                "weight": 0.25
            },
            "api": {
                "name": "API测试",
                "pattern": "**/api-test-results.xml",
                "weight": 0.2
            },
            "e2e": {
                "name": "端到端测试",
                "pattern": "**/e2e-results.xml",
                "weight": 0.15
            },
            "performance": {
                "name": "性能测试",
                "pattern": "**/performance-junit.xml",
                "weight": 0.1
            }
        }
        
        # 质量指标阈值
        self.quality_thresholds = {
            "test_pass_rate": 0.95,      # 95% 测试通过率
            "code_coverage": 0.80,        # 80% 代码覆盖率
            "api_success_rate": 0.95,     # 95% API成功率
            "performance_score": 0.85,    # 85% 性能评分
            "ai_effectiveness": 0.80      # 80% AI有效性
        }
    
    def parse_junit_xml(self, file_path: str) -> Dict[str, Any]:
        """解析JUnit XML文件"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 获取测试套件信息
            testsuite = root if root.tag == 'testsuite' else root.find('testsuite')
            if testsuite is None:
                return {"error": "No testsuite found in XML"}
            
            total_tests = int(testsuite.get('tests', 0))
            failures = int(testsuite.get('failures', 0))
            errors = int(testsuite.get('errors', 0))
            skipped = int(testsuite.get('skipped', 0))
            time = float(testsuite.get('time', 0))
            
            # 解析测试用例
            testcases = []
            for testcase in testsuite.findall('testcase'):
                case_info = {
                    "name": testcase.get('name'),
                    "classname": testcase.get('classname'),
                    "time": float(testcase.get('time', 0)),
                    "status": "passed"
                }
                
                # 检查失败和错误
                if testcase.find('failure') is not None:
                    case_info["status"] = "failed"
                    case_info["failure"] = testcase.find('failure').text
                elif testcase.find('error') is not None:
                    case_info["status"] = "error"
                    case_info["error"] = testcase.find('error').text
                elif testcase.find('skipped') is not None:
                    case_info["status"] = "skipped"
                
                testcases.append(case_info)
            
            return {
                "file_path": file_path,
                "total_tests": total_tests,
                "passed": total_tests - failures - errors - skipped,
                "failures": failures,
                "errors": errors,
                "skipped": skipped,
                "pass_rate": (total_tests - failures - errors) / max(total_tests, 1),
                "execution_time": time,
                "testcases": testcases
            }
            
        except Exception as e:
            return {"error": f"Failed to parse {file_path}: {str(e)}"}
    
    def parse_coverage_xml(self, file_path: str) -> Dict[str, Any]:
        """解析代码覆盖率XML文件"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            coverage_data = {
                "line_coverage": 0,
                "branch_coverage": 0,
                "function_coverage": 0,
                "overall_coverage": 0,
                "files": []
            }
            
            # 查找coverage元素
            if root.tag == 'coverage':
                # Cobertura格式
                line_rate = float(root.get('line-rate', 0))
                branch_rate = float(root.get('branch-rate', 0))
                
                coverage_data["line_coverage"] = line_rate * 100
                coverage_data["branch_coverage"] = branch_rate * 100
                coverage_data["overall_coverage"] = (line_rate + branch_rate) / 2 * 100
                
                # 解析包和类信息
                for package in root.findall('.//package'):
                    for cls in package.findall('classes/class'):
                        file_info = {
                            "name": cls.get('name'),
                            "filename": cls.get('filename'),
                            "line_rate": float(cls.get('line-rate', 0)),
                            "branch_rate": float(cls.get('branch-rate', 0))
                        }
                        coverage_data["files"].append(file_info)
            
            return coverage_data
            
        except Exception as e:
            return {"error": f"Failed to parse coverage {file_path}: {str(e)}"}
    
    def collect_test_results(self, base_dir: str = ".") -> Dict[str, List[Dict]]:
        """收集所有测试结果"""
        results = {}
        base_path = Path(base_dir)
        
        for test_type, config in self.test_types.items():
            pattern = config["pattern"]
            test_files = list(base_path.glob(pattern))
            
            type_results = []
            for file_path in test_files:
                result = self.parse_junit_xml(str(file_path))
                if "error" not in result:
                    result["test_type"] = test_type
                    type_results.append(result)
                else:
                    print(f"⚠️  {result['error']}")
            
            results[test_type] = type_results
            print(f"📊 Found {len(type_results)} {config['name']} result files")
        
        return results
    
    def collect_coverage_data(self, base_dir: str = ".") -> Dict[str, Any]:
        """收集代码覆盖率数据"""
        coverage_data = {}
        base_path = Path(base_dir)
        
        # 查找覆盖率文件
        coverage_patterns = [
            "**/coverage.xml",
            "**/cobertura.xml", 
            "**/coverage-final.json"
        ]
        
        for pattern in coverage_patterns:
            files = list(base_path.glob(pattern))
            for file_path in files:
                if file_path.suffix == '.xml':
                    data = self.parse_coverage_xml(str(file_path))
                elif file_path.suffix == '.json':
                    data = self.parse_coverage_json(str(file_path))
                else:
                    continue
                
                if "error" not in data:
                    component = "backend" if "backend" in str(file_path) else "frontend"
                    coverage_data[component] = data
        
        return coverage_data
    
    def parse_coverage_json(self, file_path: str) -> Dict[str, Any]:
        """解析JSON格式的覆盖率报告"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # 处理Jest覆盖率格式
            if 'total' in data:
                total = data['total']
                return {
                    "line_coverage": total.get('lines', {}).get('pct', 0),
                    "branch_coverage": total.get('branches', {}).get('pct', 0),
                    "function_coverage": total.get('functions', {}).get('pct', 0),
                    "statement_coverage": total.get('statements', {}).get('pct', 0),
                    "overall_coverage": (
                        total.get('lines', {}).get('pct', 0) + 
                        total.get('branches', {}).get('pct', 0) +
                        total.get('functions', {}).get('pct', 0) +
                        total.get('statements', {}).get('pct', 0)
                    ) / 4,
                    "files": len(data) - 1  # 减去total字段
                }
            
            return {"error": "Unsupported coverage JSON format"}
            
        except Exception as e:
            return {"error": f"Failed to parse coverage JSON {file_path}: {str(e)}"}
    
    def collect_performance_data(self, base_dir: str = ".") -> Dict[str, Any]:
        """收集性能测试数据"""
        performance_data = {}
        base_path = Path(base_dir)
        
        # 查找性能测试报告
        patterns = [
            "**/performance-results_stats.csv",
            "**/performance-report.json",
            "**/locust-stats.json"
        ]
        
        for pattern in patterns:
            files = list(base_path.glob(pattern))
            for file_path in files:
                try:
                    if file_path.suffix == '.csv':
                        data = self.parse_locust_csv(str(file_path))
                    elif file_path.suffix == '.json':
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                    
                    performance_data[file_path.stem] = data
                    
                except Exception as e:
                    print(f"⚠️  Failed to parse performance data {file_path}: {e}")
        
        return performance_data
    
    def parse_locust_csv(self, file_path: str) -> Dict[str, Any]:
        """解析Locust CSV统计文件"""
        import csv
        
        results = []
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["Type"] != "Aggregated":  # 跳过汇总行
                    results.append({
                        "name": row["Name"],
                        "method": row["Type"], 
                        "request_count": int(row["Request Count"]),
                        "failure_count": int(row["Failure Count"]),
                        "avg_response_time": float(row["Average Response Time"]),
                        "median_response_time": float(row["Median Response Time"]),
                        "min_response_time": float(row["Min Response Time"]),
                        "max_response_time": float(row["Max Response Time"]),
                        "requests_per_second": float(row["Requests/s"])
                    })
        
        return {"endpoints": results}
    
    def calculate_quality_score(self, test_results: Dict, coverage_data: Dict, performance_data: Dict) -> Dict[str, Any]:
        """计算综合质量评分"""
        scores = {}
        
        # 1. 测试通过率评分
        total_tests = 0
        total_passed = 0
        
        for test_type, results in test_results.items():
            weight = self.test_types[test_type]["weight"]
            
            for result in results:
                total_tests += result["total_tests"]
                total_passed += result["passed"]
        
        test_pass_rate = total_passed / max(total_tests, 1)
        scores["test_pass_rate"] = {
            "value": test_pass_rate,
            "score": min(100, (test_pass_rate / self.quality_thresholds["test_pass_rate"]) * 100),
            "threshold": self.quality_thresholds["test_pass_rate"]
        }
        
        # 2. 代码覆盖率评分
        avg_coverage = 0
        coverage_count = 0
        
        for component, data in coverage_data.items():
            if "overall_coverage" in data:
                avg_coverage += data["overall_coverage"]
                coverage_count += 1
        
        if coverage_count > 0:
            avg_coverage /= coverage_count
            scores["code_coverage"] = {
                "value": avg_coverage / 100,
                "score": min(100, (avg_coverage / (self.quality_thresholds["code_coverage"] * 100)) * 100),
                "threshold": self.quality_thresholds["code_coverage"]
            }
        
        # 3. 性能评分
        performance_score = 0
        if performance_data:
            # 基于响应时间和成功率计算性能评分
            total_score = 0
            score_count = 0
            
            for report_name, data in performance_data.items():
                if "endpoints" in data:
                    for endpoint in data["endpoints"]:
                        # 响应时间评分 (越低越好)
                        avg_time = endpoint.get("avg_response_time", 1000)
                        time_score = max(0, 100 - (avg_time / 10))  # 10ms = 1分扣除
                        
                        # 成功率评分
                        success_rate = 1 - (endpoint.get("failure_count", 0) / max(endpoint.get("request_count", 1), 1))
                        success_score = success_rate * 100
                        
                        endpoint_score = (time_score + success_score) / 2
                        total_score += endpoint_score
                        score_count += 1
            
            if score_count > 0:
                performance_score = total_score / score_count
        
        scores["performance"] = {
            "value": performance_score / 100,
            "score": performance_score,
            "threshold": self.quality_thresholds["performance_score"]
        }
        
        # 4. 综合评分
        overall_score = 0
        total_weight = 0
        
        if "test_pass_rate" in scores:
            overall_score += scores["test_pass_rate"]["score"] * 0.4
            total_weight += 0.4
        
        if "code_coverage" in scores:
            overall_score += scores["code_coverage"]["score"] * 0.3
            total_weight += 0.3
        
        if "performance" in scores:
            overall_score += scores["performance"]["score"] * 0.3
            total_weight += 0.3
        
        if total_weight > 0:
            overall_score /= total_weight
        
        scores["overall"] = {
            "value": overall_score / 100,
            "score": overall_score,
            "grade": self.get_quality_grade(overall_score)
        }
        
        return scores
    
    def get_quality_grade(self, score: float) -> str:
        """根据分数获取质量等级"""
        if score >= 90:
            return "A+ (优秀)"
        elif score >= 85:
            return "A (良好)"
        elif score >= 80:
            return "B+ (中上)"
        elif score >= 75:
            return "B (中等)"
        elif score >= 70:
            return "B- (中下)"
        elif score >= 65:
            return "C+ (及格)"
        elif score >= 60:
            return "C (勉强)"
        else:
            return "D (不及格)"
    
    def generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """生成HTML格式报告"""
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI教学助手系统 - 测试质量报告</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header .subtitle { margin: 10px 0 0 0; opacity: 0.9; font-size: 1.1em; }
        .content { padding: 30px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; text-align: center; }
        .metric-value { font-size: 2.5em; font-weight: bold; margin: 10px 0; }
        .metric-label { color: #6c757d; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }
        .grade-A { color: #28a745; }
        .grade-B { color: #17a2b8; }
        .grade-C { color: #ffc107; }
        .grade-D { color: #dc3545; }
        .section { margin: 30px 0; }
        .section h2 { color: #343a40; border-bottom: 2px solid #dee2e6; padding-bottom: 10px; }
        .test-results { display: grid; gap: 20px; }
        .test-type { background: white; border: 1px solid #dee2e6; border-radius: 6px; overflow: hidden; }
        .test-type-header { background: #e9ecef; padding: 15px; font-weight: bold; }
        .test-type-content { padding: 15px; }
        .progress-bar { width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; transition: width 0.3s ease; }
        .progress-success { background: #28a745; }
        .progress-warning { background: #ffc107; }
        .progress-danger { background: #dc3545; }
        .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin: 15px 0; }
        .stat-item { text-align: center; }
        .stat-number { font-size: 1.5em; font-weight: bold; }
        .stat-label { font-size: 0.8em; color: #6c757d; }
        .footer { background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px; text-align: center; color: #6c757d; }
        .timestamp { font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 AI教学助手系统</h1>
            <div class="subtitle">测试质量报告 - {timestamp}</div>
        </div>
        
        <div class="content">
            <!-- 总体评分 -->
            <div class="section">
                <h2>📊 质量评分总览</h2>
                <div class="summary">
                    <div class="metric-card">
                        <div class="metric-label">综合评分</div>
                        <div class="metric-value grade-{grade_class}">{overall_score:.1f}</div>
                        <div>{overall_grade}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">测试通过率</div>
                        <div class="metric-value grade-{test_grade_class}">{test_pass_rate:.1%}</div>
                        <div>目标: ≥{test_threshold:.0%}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">代码覆盖率</div>
                        <div class="metric-value grade-{coverage_grade_class}">{coverage_rate:.1%}</div>
                        <div>目标: ≥{coverage_threshold:.0%}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">性能评分</div>
                        <div class="metric-value grade-{perf_grade_class}">{performance_score:.1f}</div>
                        <div>目标: ≥{perf_threshold:.0f}</div>
                    </div>
                </div>
            </div>
            
            <!-- 测试结果详情 -->
            <div class="section">
                <h2>🔍 测试结果详情</h2>
                <div class="test-results">
                    {test_details}
                </div>
            </div>
            
            <!-- 覆盖率详情 -->
            {coverage_section}
            
            <!-- 性能测试详情 -->
            {performance_section}
            
            <!-- 趋势分析 -->
            {trend_section}
        </div>
        
        <div class="footer">
            <div class="timestamp">报告生成时间: {timestamp}</div>
            <div>AI教学助手系统质量保证团队</div>
        </div>
    </div>
</body>
</html>
        """
        
        # 准备模板数据
        overall_score = report_data["quality_scores"]["overall"]["score"]
        overall_grade = report_data["quality_scores"]["overall"]["grade"]
        
        template_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "overall_score": overall_score,
            "overall_grade": overall_grade,
            "grade_class": self.get_grade_class(overall_score),
            
            "test_pass_rate": report_data["quality_scores"]["test_pass_rate"]["value"],
            "test_threshold": report_data["quality_scores"]["test_pass_rate"]["threshold"],
            "test_grade_class": self.get_grade_class(report_data["quality_scores"]["test_pass_rate"]["score"]),
            
            "coverage_rate": report_data["quality_scores"].get("code_coverage", {}).get("value", 0),
            "coverage_threshold": report_data["quality_scores"].get("code_coverage", {}).get("threshold", 0.8),
            "coverage_grade_class": self.get_grade_class(report_data["quality_scores"].get("code_coverage", {}).get("score", 0)),
            
            "performance_score": report_data["quality_scores"]["performance"]["score"],
            "perf_threshold": report_data["quality_scores"]["performance"]["threshold"] * 100,
            "perf_grade_class": self.get_grade_class(report_data["quality_scores"]["performance"]["score"]),
            
            "test_details": self.generate_test_details_html(report_data["test_results"]),
            "coverage_section": self.generate_coverage_section_html(report_data["coverage_data"]),
            "performance_section": self.generate_performance_section_html(report_data["performance_data"]),
            "trend_section": ""  # 趋势分析部分可以后续添加
        }
        
        return html_template.format(**template_data)
    
    def get_grade_class(self, score: float) -> str:
        """获取CSS等级类名"""
        if score >= 85:
            return "A"
        elif score >= 75:
            return "B" 
        elif score >= 65:
            return "C"
        else:
            return "D"
    
    def generate_test_details_html(self, test_results: Dict) -> str:
        """生成测试详情HTML"""
        details_html = []
        
        for test_type, results in test_results.items():
            if not results:
                continue
                
            config = self.test_types[test_type]
            total_tests = sum(r["total_tests"] for r in results)
            total_passed = sum(r["passed"] for r in results)
            pass_rate = total_passed / max(total_tests, 1)
            
            progress_class = "progress-success" if pass_rate >= 0.9 else ("progress-warning" if pass_rate >= 0.7 else "progress-danger")
            
            detail_html = f"""
            <div class="test-type">
                <div class="test-type-header">{config['name']} ({len(results)} 个测试套件)</div>
                <div class="test-type-content">
                    <div class="progress-bar">
                        <div class="progress-fill {progress_class}" style="width: {pass_rate*100:.1f}%"></div>
                    </div>
                    <div class="stat-grid">
                        <div class="stat-item">
                            <div class="stat-number">{total_tests}</div>
                            <div class="stat-label">总测试数</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{total_passed}</div>
                            <div class="stat-label">通过</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{sum(r["failures"] for r in results)}</div>
                            <div class="stat-label">失败</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{pass_rate:.1%}</div>
                            <div class="stat-label">通过率</div>
                        </div>
                    </div>
                </div>
            </div>
            """
            details_html.append(detail_html)
        
        return "\n".join(details_html)
    
    def generate_coverage_section_html(self, coverage_data: Dict) -> str:
        """生成覆盖率部分HTML"""
        if not coverage_data:
            return ""
        
        section_html = """
        <div class="section">
            <h2>📈 代码覆盖率</h2>
            <div class="test-results">
        """
        
        for component, data in coverage_data.items():
            if "error" in data:
                continue
            
            coverage = data.get("overall_coverage", 0)
            progress_class = "progress-success" if coverage >= 80 else ("progress-warning" if coverage >= 60 else "progress-danger")
            
            component_html = f"""
            <div class="test-type">
                <div class="test-type-header">{component.title()} 覆盖率</div>
                <div class="test-type-content">
                    <div class="progress-bar">
                        <div class="progress-fill {progress_class}" style="width: {coverage:.1f}%"></div>
                    </div>
                    <div class="stat-grid">
                        <div class="stat-item">
                            <div class="stat-number">{data.get('line_coverage', 0):.1f}%</div>
                            <div class="stat-label">行覆盖率</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{data.get('branch_coverage', 0):.1f}%</div>
                            <div class="stat-label">分支覆盖率</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{data.get('function_coverage', 0):.1f}%</div>
                            <div class="stat-label">函数覆盖率</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{len(data.get('files', []))}</div>
                            <div class="stat-label">测试文件数</div>
                        </div>
                    </div>
                </div>
            </div>
            """
            section_html += component_html
        
        section_html += "</div></div>"
        return section_html
    
    def generate_performance_section_html(self, performance_data: Dict) -> str:
        """生成性能测试部分HTML"""
        if not performance_data:
            return ""
        
        return """
        <div class="section">
            <h2>⚡ 性能测试结果</h2>
            <p>性能测试数据已收集，详细分析请查看性能报告文件。</p>
        </div>
        """
    
    def generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """生成JSON格式报告"""
        return json.dumps(report_data, indent=2, ensure_ascii=False, default=str)
    
    def generate_markdown_report(self, report_data: Dict[str, Any]) -> str:
        """生成Markdown格式报告"""
        md_lines = [
            "# 🧪 AI教学助手系统 - 测试质量报告",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 📊 质量评分总览",
            ""
        ]
        
        # 总体评分
        overall = report_data["quality_scores"]["overall"]
        md_lines.extend([
            f"**综合评分**: {overall['score']:.1f}/100 ({overall['grade']})",
            ""
        ])
        
        # 各项指标
        md_lines.extend([
            "| 指标 | 实际值 | 评分 | 目标值 | 状态 |",
            "|------|--------|------|--------|------|"
        ])
        
        for key, data in report_data["quality_scores"].items():
            if key == "overall":
                continue
            
            value = f"{data['value']:.1%}" if "rate" in key or "coverage" in key else f"{data.get('score', 0):.1f}"
            threshold = f"{data['threshold']:.1%}" if "rate" in key or "coverage" in key else f"{data['threshold']*100:.0f}"
            status = "✅" if data.get('score', 0) >= (data['threshold'] * 100 if 'rate' in key or 'coverage' in key else data['threshold']) else "❌"
            
            md_lines.append(f"| {key.replace('_', ' ').title()} | {value} | {data.get('score', 0):.1f} | ≥{threshold} | {status} |")
        
        md_lines.extend(["", "## 🔍 测试结果详情", ""])
        
        # 测试结果
        for test_type, results in report_data["test_results"].items():
            if not results:
                continue
            
            config = self.test_types[test_type]
            total_tests = sum(r["total_tests"] for r in results)
            total_passed = sum(r["passed"] for r in results)
            pass_rate = total_passed / max(total_tests, 1)
            
            md_lines.extend([
                f"### {config['name']}",
                "",
                f"- **测试套件数**: {len(results)}",
                f"- **总测试数**: {total_tests}",
                f"- **通过数**: {total_passed}",
                f"- **失败数**: {sum(r['failures'] for r in results)}",
                f"- **通过率**: {pass_rate:.1%}",
                ""
            ])
        
        return "\n".join(md_lines)
    
    def save_report(self, report_data: Dict[str, Any], format_type: str = "html"):
        """保存报告到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "html":
            content = self.generate_html_report(report_data)
            filename = self.output_dir / f"test_report_{timestamp}.html"
        elif format_type == "json":
            content = self.generate_json_report(report_data)
            filename = self.output_dir / f"test_report_{timestamp}.json"
        elif format_type == "markdown":
            content = self.generate_markdown_report(report_data)
            filename = self.output_dir / f"test_report_{timestamp}.md"
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Report saved to {filename}")
        return str(filename)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试报告生成器")
    parser.add_argument("--input-dir", default=".", help="测试结果输入目录")
    parser.add_argument("--output-dir", default="test-reports", help="报告输出目录")
    parser.add_argument("--format", choices=["html", "json", "markdown", "all"], 
                       default="html", help="报告格式")
    
    args = parser.parse_args()
    
    # 创建报告生成器
    generator = TestReportGenerator(args.output_dir)
    
    try:
        print("📊 Collecting test results...")
        
        # 收集测试数据
        test_results = generator.collect_test_results(args.input_dir)
        coverage_data = generator.collect_coverage_data(args.input_dir)
        performance_data = generator.collect_performance_data(args.input_dir)
        
        # 计算质量评分
        quality_scores = generator.calculate_quality_score(
            test_results, coverage_data, performance_data
        )
        
        # 汇总报告数据
        report_data = {
            "generation_time": datetime.now().isoformat(),
            "test_results": test_results,
            "coverage_data": coverage_data,
            "performance_data": performance_data,
            "quality_scores": quality_scores
        }
        
        # 生成报告
        if args.format == "all":
            formats = ["html", "json", "markdown"]
        else:
            formats = [args.format]
        
        report_files = []
        for fmt in formats:
            filename = generator.save_report(report_data, fmt)
            report_files.append(filename)
        
        print(f"\n🎉 Report generation completed!")
        print(f"Overall Quality Score: {quality_scores['overall']['score']:.1f}/100 ({quality_scores['overall']['grade']})")
        
        for filename in report_files:
            print(f"📄 Report: {filename}")
    
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()