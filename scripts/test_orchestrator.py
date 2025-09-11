#!/usr/bin/env python3
"""
AI Teaching Assistant System - Test Orchestration Script
测试编排和执行脚本

This script provides comprehensive test orchestration capabilities including:
- Test suite selection and execution
- Parallel test execution management
- Real-time progress monitoring
- Quality gate enforcement
- Test result aggregation
- Performance benchmarking
"""

import asyncio
import argparse
import json
import logging
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import yaml


@dataclass
class TestSuite:
    """测试套件配置"""
    name: str
    path: str
    markers: List[str]
    priority: int
    timeout: int
    parallel: bool
    dependencies: List[str]


@dataclass
class TestResult:
    """测试结果"""
    suite_name: str
    status: str  # passed, failed, skipped, timeout
    duration: float
    passed: int
    failed: int
    skipped: int
    coverage: float
    log_file: str


class TestOrchestrator:
    """测试编排器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "test-orchestration.yml"
        self.results: Dict[str, TestResult] = {}
        self.start_time = None
        self.logger = self._setup_logging()
        
        # 加载配置
        self.config = self._load_config()
        self.test_suites = self._load_test_suites()
        
        # 质量门限
        self.quality_gates = self.config.get('quality_gates', {
            'min_coverage': 80.0,
            'max_failure_rate': 5.0,
            'max_duration_minutes': 30
        })
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger('test_orchestrator')
        logger.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / f"test-orchestrator-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        )
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d %(funcName)s(): %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            self.logger.warning(f"Configuration file {self.config_path} not found, using defaults")
            return self._get_default_config()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'test_suites': [
                {
                    'name': 'unit_tests',
                    'path': 'tests/unit',
                    'markers': ['unit'],
                    'priority': 1,
                    'timeout': 300,
                    'parallel': True,
                    'dependencies': []
                },
                {
                    'name': 'integration_tests',
                    'path': 'tests/integration',
                    'markers': ['integration'],
                    'priority': 2,
                    'timeout': 600,
                    'parallel': True,
                    'dependencies': ['unit_tests']
                },
                {
                    'name': 'api_tests',
                    'path': 'tests/api',
                    'markers': ['api'],
                    'priority': 2,
                    'timeout': 900,
                    'parallel': True,
                    'dependencies': ['unit_tests']
                },
                {
                    'name': 'ai_tests',
                    'path': 'tests/ai',
                    'markers': ['ai'],
                    'priority': 3,
                    'timeout': 1800,
                    'parallel': False,
                    'dependencies': ['unit_tests', 'integration_tests']
                },
                {
                    'name': 'e2e_tests',
                    'path': 'ai-teacher-frontend/e2e',
                    'markers': ['e2e'],
                    'priority': 4,
                    'timeout': 2400,
                    'parallel': False,
                    'dependencies': ['api_tests']
                },
                {
                    'name': 'performance_tests',
                    'path': 'tests/performance',
                    'markers': ['performance'],
                    'priority': 5,
                    'timeout': 3600,
                    'parallel': False,
                    'dependencies': ['api_tests']
                }
            ],
            'quality_gates': {
                'min_coverage': 80.0,
                'max_failure_rate': 5.0,
                'max_duration_minutes': 30
            },
            'reporting': {
                'formats': ['html', 'json', 'junit'],
                'output_dir': 'test-results',
                'notifications': {
                    'on_failure': True,
                    'on_quality_gate_fail': True
                }
            }
        }
    
    def _load_test_suites(self) -> List[TestSuite]:
        """加载测试套件配置"""
        suites = []
        
        for suite_config in self.config.get('test_suites', []):
            suite = TestSuite(
                name=suite_config['name'],
                path=suite_config['path'],
                markers=suite_config.get('markers', []),
                priority=suite_config.get('priority', 3),
                timeout=suite_config.get('timeout', 600),
                parallel=suite_config.get('parallel', True),
                dependencies=suite_config.get('dependencies', [])
            )
            suites.append(suite)
        
        return sorted(suites, key=lambda x: x.priority)
    
    def _execute_test_suite(self, suite: TestSuite) -> TestResult:
        """执行单个测试套件"""
        self.logger.info(f"🚀 Starting test suite: {suite.name}")
        start_time = time.time()
        
        # 准备测试命令
        if suite.name == 'e2e_tests':
            cmd = self._build_playwright_command(suite)
        elif suite.name == 'performance_tests':
            cmd = self._build_locust_command(suite)
        else:
            cmd = self._build_pytest_command(suite)
        
        # 执行测试
        try:
            result = subprocess.run(
                cmd,
                timeout=suite.timeout,
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            duration = time.time() - start_time
            
            # 解析结果
            if suite.name == 'e2e_tests':
                return self._parse_playwright_result(suite, result, duration)
            elif suite.name == 'performance_tests':
                return self._parse_locust_result(suite, result, duration)
            else:
                return self._parse_pytest_result(suite, result, duration)
                
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.logger.error(f"⏰ Test suite {suite.name} timed out after {suite.timeout}s")
            
            return TestResult(
                suite_name=suite.name,
                status='timeout',
                duration=duration,
                passed=0,
                failed=0,
                skipped=0,
                coverage=0.0,
                log_file=self._save_logs(suite.name, "", "TIMEOUT")
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"❌ Test suite {suite.name} failed with error: {e}")
            
            return TestResult(
                suite_name=suite.name,
                status='failed',
                duration=duration,
                passed=0,
                failed=1,
                skipped=0,
                coverage=0.0,
                log_file=self._save_logs(suite.name, "", str(e))
            )
    
    def _build_pytest_command(self, suite: TestSuite) -> List[str]:
        """构建pytest命令"""
        cmd = ['python', '-m', 'pytest']
        
        # 添加路径
        if Path(suite.path).exists():
            cmd.append(suite.path)
        
        # 添加标记
        for marker in suite.markers:
            cmd.extend(['-m', marker])
        
        # 添加报告选项
        output_dir = Path("test-results") / suite.name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cmd.extend([
            '--junitxml', str(output_dir / 'junit.xml'),
            '--html', str(output_dir / 'report.html'),
            '--self-contained-html',
            '--cov-report', f'html:{output_dir}/coverage',
            '--cov-report', f'xml:{output_dir}/coverage.xml',
            '--cov-report', 'term-missing',
            '-v'
        ])
        
        # 并行执行
        if suite.parallel:
            import multiprocessing
            workers = max(1, multiprocessing.cpu_count() - 1)
            cmd.extend(['-n', str(workers)])
        
        return cmd
    
    def _build_playwright_command(self, suite: TestSuite) -> List[str]:
        """构建Playwright命令"""
        frontend_dir = Path("ai-teacher-frontend")
        
        if not frontend_dir.exists():
            raise FileNotFoundError("Frontend directory not found")
        
        return ['npm', 'run', 'test:e2e', '--prefix', str(frontend_dir)]
    
    def _build_locust_command(self, suite: TestSuite) -> List[str]:
        """构建Locust性能测试命令"""
        locust_file = Path(suite.path) / "locustfile.py"
        
        if not locust_file.exists():
            raise FileNotFoundError(f"Locust file not found: {locust_file}")
        
        return [
            'locust',
            '-f', str(locust_file),
            '--users', '50',
            '--spawn-rate', '10',
            '--run-time', '5m',
            '--host', 'http://localhost:8000',
            '--headless',
            '--html', 'test-results/performance/report.html',
            '--csv', 'test-results/performance/results'
        ]
    
    def _parse_pytest_result(self, suite: TestSuite, result: subprocess.CompletedProcess, duration: float) -> TestResult:
        """解析pytest结果"""
        # 解析JUnit XML获取详细结果
        junit_file = Path("test-results") / suite.name / "junit.xml"
        
        passed = failed = skipped = 0
        coverage = 0.0
        
        if junit_file.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(junit_file)
                root = tree.getroot()
                
                for testcase in root.findall('.//testcase'):
                    if testcase.find('failure') is not None:
                        failed += 1
                    elif testcase.find('skipped') is not None:
                        skipped += 1
                    else:
                        passed += 1
                        
            except Exception as e:
                self.logger.warning(f"Failed to parse JUnit XML: {e}")
        
        # 解析覆盖率
        coverage_file = Path("test-results") / suite.name / "coverage.xml"
        if coverage_file.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(coverage_file)
                root = tree.getroot()
                coverage_elem = root.find('.//coverage')
                if coverage_elem is not None:
                    coverage = float(coverage_elem.get('line-rate', 0)) * 100
            except Exception as e:
                self.logger.warning(f"Failed to parse coverage XML: {e}")
        
        status = 'passed' if result.returncode == 0 else 'failed'
        log_file = self._save_logs(suite.name, result.stdout, result.stderr)
        
        return TestResult(
            suite_name=suite.name,
            status=status,
            duration=duration,
            passed=passed,
            failed=failed,
            skipped=skipped,
            coverage=coverage,
            log_file=log_file
        )
    
    def _parse_playwright_result(self, suite: TestSuite, result: subprocess.CompletedProcess, duration: float) -> TestResult:
        """解析Playwright结果"""
        # Playwright结果解析逻辑
        status = 'passed' if result.returncode == 0 else 'failed'
        log_file = self._save_logs(suite.name, result.stdout, result.stderr)
        
        # 简单解析输出中的测试数量
        stdout = result.stdout
        passed = stdout.count('✓') if stdout else 0
        failed = stdout.count('✗') if stdout else 0
        
        return TestResult(
            suite_name=suite.name,
            status=status,
            duration=duration,
            passed=passed,
            failed=failed,
            skipped=0,
            coverage=0.0,  # Playwright不提供代码覆盖率
            log_file=log_file
        )
    
    def _parse_locust_result(self, suite: TestSuite, result: subprocess.CompletedProcess, duration: float) -> TestResult:
        """解析Locust性能测试结果"""
        status = 'passed' if result.returncode == 0 else 'failed'
        log_file = self._save_logs(suite.name, result.stdout, result.stderr)
        
        # 性能测试通常以成功执行为准
        passed = 1 if status == 'passed' else 0
        failed = 1 if status == 'failed' else 0
        
        return TestResult(
            suite_name=suite.name,
            status=status,
            duration=duration,
            passed=passed,
            failed=failed,
            skipped=0,
            coverage=0.0,
            log_file=log_file
        )
    
    def _save_logs(self, suite_name: str, stdout: str, stderr: str) -> str:
        """保存测试日志"""
        log_dir = Path("test-results") / suite_name / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        log_file = log_dir / f"{suite_name}-{timestamp}.log"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== STDOUT ===\n{stdout}\n\n")
            f.write(f"=== STDERR ===\n{stderr}\n")
        
        return str(log_file)
    
    def _check_dependencies(self, suite: TestSuite) -> bool:
        """检查测试套件依赖"""
        for dep in suite.dependencies:
            if dep not in self.results:
                return False
            if self.results[dep].status != 'passed':
                self.logger.warning(f"Dependency {dep} failed, skipping {suite.name}")
                return False
        return True
    
    def _check_quality_gates(self) -> Tuple[bool, List[str]]:
        """检查质量门限"""
        issues = []
        
        # 检查整体覆盖率
        total_coverage = self._calculate_overall_coverage()
        min_coverage = self.quality_gates.get('min_coverage', 80.0)
        
        if total_coverage < min_coverage:
            issues.append(f"Coverage {total_coverage:.1f}% below minimum {min_coverage}%")
        
        # 检查失败率
        total_tests = sum(r.passed + r.failed for r in self.results.values())
        total_failures = sum(r.failed for r in self.results.values())
        failure_rate = (total_failures / max(total_tests, 1)) * 100
        max_failure_rate = self.quality_gates.get('max_failure_rate', 5.0)
        
        if failure_rate > max_failure_rate:
            issues.append(f"Failure rate {failure_rate:.1f}% exceeds maximum {max_failure_rate}%")
        
        # 检查执行时间
        total_duration = sum(r.duration for r in self.results.values()) / 60
        max_duration = self.quality_gates.get('max_duration_minutes', 30)
        
        if total_duration > max_duration:
            issues.append(f"Total duration {total_duration:.1f}min exceeds maximum {max_duration}min")
        
        return len(issues) == 0, issues
    
    def _calculate_overall_coverage(self) -> float:
        """计算整体代码覆盖率"""
        coverage_results = [r.coverage for r in self.results.values() if r.coverage > 0]
        return sum(coverage_results) / len(coverage_results) if coverage_results else 0.0
    
    def _generate_summary_report(self) -> Dict[str, Any]:
        """生成汇总报告"""
        total_duration = sum(r.duration for r in self.results.values())
        total_tests = sum(r.passed + r.failed + r.skipped for r in self.results.values())
        total_passed = sum(r.passed for r in self.results.values())
        total_failed = sum(r.failed for r in self.results.values())
        total_skipped = sum(r.skipped for r in self.results.values())
        
        quality_gates_passed, quality_issues = self._check_quality_gates()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'execution_time': {
                'start': self.start_time.isoformat() if self.start_time else None,
                'duration_seconds': total_duration,
                'duration_formatted': str(timedelta(seconds=int(total_duration)))
            },
            'summary': {
                'total_suites': len(self.results),
                'passed_suites': len([r for r in self.results.values() if r.status == 'passed']),
                'failed_suites': len([r for r in self.results.values() if r.status == 'failed']),
                'total_tests': total_tests,
                'passed_tests': total_passed,
                'failed_tests': total_failed,
                'skipped_tests': total_skipped,
                'success_rate': (total_passed / max(total_tests, 1)) * 100,
                'overall_coverage': self._calculate_overall_coverage()
            },
            'quality_gates': {
                'passed': quality_gates_passed,
                'issues': quality_issues
            },
            'suite_results': [
                {
                    'name': result.suite_name,
                    'status': result.status,
                    'duration': result.duration,
                    'passed': result.passed,
                    'failed': result.failed,
                    'skipped': result.skipped,
                    'coverage': result.coverage,
                    'log_file': result.log_file
                }
                for result in self.results.values()
            ]
        }
    
    async def run_test_suites(self, suites_filter: Optional[List[str]] = None, 
                            parallel_execution: bool = True) -> Dict[str, Any]:
        """运行测试套件"""
        self.start_time = datetime.now()
        self.logger.info("🎯 Starting test orchestration")
        
        # 过滤测试套件
        suites_to_run = self.test_suites
        if suites_filter:
            suites_to_run = [s for s in self.test_suites if s.name in suites_filter]
        
        self.logger.info(f"📋 Planning to execute {len(suites_to_run)} test suites")
        
        # 执行测试套件
        if parallel_execution:
            await self._run_parallel_suites(suites_to_run)
        else:
            await self._run_sequential_suites(suites_to_run)
        
        # 生成报告
        summary = self._generate_summary_report()
        
        # 保存报告
        report_file = Path("test-results") / "orchestration-summary.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # 输出结果
        self._print_summary(summary)
        
        return summary
    
    async def _run_parallel_suites(self, suites: List[TestSuite]):
        """并行执行测试套件（考虑依赖关系）"""
        executed = set()
        
        while len(executed) < len(suites):
            # 找到可以执行的测试套件
            ready_suites = []
            for suite in suites:
                if (suite.name not in executed and 
                    self._check_dependencies(suite) and 
                    all(dep in executed for dep in suite.dependencies)):
                    ready_suites.append(suite)
            
            if not ready_suites:
                # 如果没有可执行的套件，说明存在循环依赖或依赖失败
                remaining = [s.name for s in suites if s.name not in executed]
                self.logger.error(f"Cannot execute remaining suites due to dependencies: {remaining}")
                break
            
            # 并行执行就绪的测试套件
            with ThreadPoolExecutor(max_workers=min(len(ready_suites), 4)) as executor:
                futures = {
                    executor.submit(self._execute_test_suite, suite): suite 
                    for suite in ready_suites
                }
                
                for future in as_completed(futures):
                    suite = futures[future]
                    try:
                        result = future.result()
                        self.results[suite.name] = result
                        executed.add(suite.name)
                        
                        status_icon = "✅" if result.status == "passed" else "❌"
                        self.logger.info(
                            f"{status_icon} {suite.name}: {result.passed}P/{result.failed}F/"
                            f"{result.skipped}S in {result.duration:.1f}s"
                        )
                        
                    except Exception as e:
                        self.logger.error(f"❌ {suite.name} execution failed: {e}")
                        executed.add(suite.name)
    
    async def _run_sequential_suites(self, suites: List[TestSuite]):
        """顺序执行测试套件"""
        for suite in suites:
            if not self._check_dependencies(suite):
                self.logger.warning(f"⏭️ Skipping {suite.name} due to dependency failure")
                continue
            
            result = self._execute_test_suite(suite)
            self.results[suite.name] = result
            
            status_icon = "✅" if result.status == "passed" else "❌"
            self.logger.info(
                f"{status_icon} {suite.name}: {result.passed}P/{result.failed}F/"
                f"{result.skipped}S in {result.duration:.1f}s"
            )
    
    def _print_summary(self, summary: Dict[str, Any]):
        """打印测试摘要"""
        print("\n" + "=" * 80)
        print("🎯 TEST ORCHESTRATION SUMMARY")
        print("=" * 80)
        
        exec_summary = summary['summary']
        print(f"📊 Total Test Suites: {exec_summary['total_suites']}")
        print(f"✅ Passed Suites: {exec_summary['passed_suites']}")
        print(f"❌ Failed Suites: {exec_summary['failed_suites']}")
        print(f"🧪 Total Tests: {exec_summary['total_tests']}")
        print(f"📈 Success Rate: {exec_summary['success_rate']:.1f}%")
        print(f"🎯 Overall Coverage: {exec_summary['overall_coverage']:.1f}%")
        print(f"⏱️ Total Duration: {summary['execution_time']['duration_formatted']}")
        
        # 质量门限状态
        quality = summary['quality_gates']
        quality_status = "✅ PASSED" if quality['passed'] else "❌ FAILED"
        print(f"🚪 Quality Gates: {quality_status}")
        
        if quality['issues']:
            print("\n🚨 Quality Issues:")
            for issue in quality['issues']:
                print(f"  • {issue}")
        
        print("\n📋 Suite Details:")
        for suite_result in summary['suite_results']:
            status_icon = {"passed": "✅", "failed": "❌", "timeout": "⏰"}.get(suite_result['status'], "❓")
            print(f"  {status_icon} {suite_result['name']}: "
                  f"{suite_result['passed']}P/{suite_result['failed']}F/"
                  f"{suite_result['skipped']}S "
                  f"({suite_result['coverage']:.1f}% cov, {suite_result['duration']:.1f}s)")
        
        print("=" * 80)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI Teaching Assistant Test Orchestrator")
    
    parser.add_argument(
        '--config', '-c',
        help='Configuration file path',
        default='test-orchestration.yml'
    )
    
    parser.add_argument(
        '--suites', '-s',
        nargs='*',
        help='Specific test suites to run'
    )
    
    parser.add_argument(
        '--sequential',
        action='store_true',
        help='Run test suites sequentially instead of in parallel'
    )
    
    parser.add_argument(
        '--generate-config',
        action='store_true',
        help='Generate default configuration file'
    )
    
    args = parser.parse_args()
    
    if args.generate_config:
        # 生成默认配置文件
        orchestrator = TestOrchestrator()
        config_path = Path(args.config)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(orchestrator._get_default_config(), f, 
                     default_flow_style=False, allow_unicode=True, indent=2)
        
        print(f"✅ Generated default configuration: {config_path}")
        return
    
    # 运行测试编排
    orchestrator = TestOrchestrator(args.config)
    
    async def run_tests():
        try:
            summary = await orchestrator.run_test_suites(
                suites_filter=args.suites,
                parallel_execution=not args.sequential
            )
            
            # 根据质量门限设置退出码
            quality_passed = summary['quality_gates']['passed']
            has_failures = summary['summary']['failed_suites'] > 0
            
            if not quality_passed or has_failures:
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n⚠️ Test orchestration interrupted by user")
            sys.exit(130)
        except Exception as e:
            print(f"❌ Test orchestration failed: {e}")
            sys.exit(1)
    
    # 运行异步任务
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n⚠️ Test orchestration interrupted")
        sys.exit(130)


if __name__ == "__main__":
    main()