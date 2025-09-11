#!/usr/bin/env python3
"""
AI Teaching Assistant System - Comprehensive Test Runner
综合测试运行器

This is the main entry point for running the complete test suite.
Integrates test orchestration, data management, reporting, and quality monitoring.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# 设置Python路径以便导入本地模块
sys.path.insert(0, str(Path(__file__).parent))

try:
    from scripts.test_orchestrator import TestOrchestrator
    from scripts.test_data_manager import TestDataManager
    from scripts.test_report_generator import TestReportGenerator
    from scripts.test_dashboard_generator import TestDashboardGenerator
except ImportError as e:
    print(f"❌ Failed to import test modules: {e}")
    print("Please ensure all test framework components are properly installed.")
    sys.exit(1)


class ComprehensiveTestRunner:
    """综合测试运行器"""
    
    def __init__(self, config_path: str = "test-orchestration.yml"):
        self.config_path = config_path
        self.logger = self._setup_logging()
        self.start_time = None
        self.results = {}
        
        # 初始化组件
        self.orchestrator = TestOrchestrator(config_path)
        self.data_manager = TestDataManager()
        self.report_generator = TestReportGenerator()
        self.dashboard_generator = TestDashboardGenerator()
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger('comprehensive_test_runner')
        logger.setLevel(logging.INFO)
        
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        file_handler = logging.FileHandler(
            log_dir / f"test-runner-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        )
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d %(funcName)s(): %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _print_banner(self):
        """显示横幅"""
        print("\n" + "="*80)
        print("🎯 AI Teaching Assistant System - Comprehensive Test Runner")
        print("="*80)
        print(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⚙️  Configuration: {self.config_path}")
        print("="*80 + "\n")
    
    def _check_prerequisites(self) -> bool:
        """检查运行前提条件"""
        self.logger.info("🔍 Checking prerequisites...")
        
        issues = []
        
        # 检查配置文件
        if not Path(self.config_path).exists():
            issues.append(f"Configuration file not found: {self.config_path}")
        
        # 检查测试目录
        test_dirs = ["tests", "ai-teacher-frontend"]
        for test_dir in test_dirs:
            if not Path(test_dir).exists():
                issues.append(f"Test directory not found: {test_dir}")
        
        # 检查必要的Python包
        required_packages = ["pytest", "httpx", "asyncio"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            issues.append(f"Missing Python packages: {', '.join(missing_packages)}")
        
        # 检查环境变量
        required_env_vars = ["DATABASE_URL", "REDIS_URL"]
        missing_env_vars = []
        
        for env_var in required_env_vars:
            if not os.getenv(env_var):
                missing_env_vars.append(env_var)
        
        if missing_env_vars:
            issues.append(f"Missing environment variables: {', '.join(missing_env_vars)}")
        
        if issues:
            self.logger.error("❌ Prerequisites check failed:")
            for issue in issues:
                self.logger.error(f"  • {issue}")
            return False
        
        self.logger.info("✅ Prerequisites check passed")
        return True
    
    async def setup_test_environment(self):
        """设置测试环境"""
        self.logger.info("🚀 Setting up test environment...")
        
        try:
            # 创建测试目录
            test_dirs = [
                "test-results",
                "test-results/reports",
                "test-results/artifacts",
                "test-results/logs",
                "test-results/charts"
            ]
            
            for test_dir in test_dirs:
                Path(test_dir).mkdir(parents=True, exist_ok=True)
            
            # 初始化测试数据
            await self.data_manager.setup_test_environment()
            self.logger.info("✅ Test data environment initialized")
            
            # 启动服务依赖检查
            await self._check_service_dependencies()
            
            self.logger.info("✅ Test environment setup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup test environment: {e}")
            raise
    
    async def _check_service_dependencies(self):
        """检查服务依赖"""
        self.logger.info("🔍 Checking service dependencies...")
        
        # 检查数据库连接
        try:
            database_url = os.getenv("DATABASE_URL")
            if database_url and "postgresql" in database_url:
                # 检查PostgreSQL连接
                result = subprocess.run(
                    ["pg_isready", "-d", database_url],
                    capture_output=True,
                    timeout=10
                )
                if result.returncode != 0:
                    self.logger.warning("⚠️ PostgreSQL connection check failed")
        except Exception as e:
            self.logger.warning(f"⚠️ Database connectivity check failed: {e}")
        
        # 检查Redis连接
        try:
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                result = subprocess.run(
                    ["redis-cli", "-u", redis_url, "ping"],
                    capture_output=True,
                    timeout=10
                )
                if result.returncode == 0 and b"PONG" in result.stdout:
                    self.logger.info("✅ Redis connection verified")
                else:
                    self.logger.warning("⚠️ Redis connection check failed")
        except Exception as e:
            self.logger.warning(f"⚠️ Redis connectivity check failed: {e}")
    
    async def run_test_phases(self, suites_filter: Optional[List[str]] = None,
                            parallel_execution: bool = True) -> Dict[str, Any]:
        """运行测试阶段"""
        self.logger.info("🎯 Starting test execution phases...")
        
        # 阶段1: 准备测试数据
        self.logger.info("📊 Phase 1: Preparing test data...")
        await self.data_manager.generate_comprehensive_test_data()
        
        # 阶段2: 执行测试套件
        self.logger.info("🧪 Phase 2: Executing test suites...")
        test_results = await self.orchestrator.run_test_suites(
            suites_filter=suites_filter,
            parallel_execution=parallel_execution
        )
        
        # 阶段3: 生成报告
        self.logger.info("📋 Phase 3: Generating reports...")
        await self._generate_comprehensive_reports(test_results)
        
        # 阶段4: 更新仪表板
        self.logger.info("📈 Phase 4: Updating dashboard...")
        await self._update_quality_dashboard(test_results)
        
        # 阶段5: 清理测试环境
        self.logger.info("🧹 Phase 5: Cleaning up test environment...")
        await self.cleanup_test_environment(test_results)
        
        return test_results
    
    async def _generate_comprehensive_reports(self, test_results: Dict[str, Any]):
        """生成综合报告"""
        try:
            # 保存原始结果
            results_file = Path("test-results/orchestration-summary.json")
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(test_results, f, indent=2, ensure_ascii=False)
            
            # 生成HTML报告
            html_report = await self.report_generator.generate_comprehensive_report(
                str(results_file),
                output_path="test-results/reports/comprehensive-report.html"
            )
            self.logger.info(f"✅ Generated HTML report: {html_report}")
            
            # 生成Markdown报告
            md_report = self.report_generator.generate_markdown_report(
                test_results,
                output_path="test-results/reports/test-summary.md"
            )
            self.logger.info(f"✅ Generated Markdown report: {md_report}")
            
            # 生成JUnit XML报告（如果有pytest结果）
            junit_report = self._generate_consolidated_junit_report()
            if junit_report:
                self.logger.info(f"✅ Generated JUnit report: {junit_report}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to generate reports: {e}")
    
    def _generate_consolidated_junit_report(self) -> Optional[str]:
        """生成合并的JUnit报告"""
        junit_files = list(Path("test-results").glob("**/junit.xml"))
        
        if not junit_files:
            return None
        
        try:
            import xml.etree.ElementTree as ET
            
            # 创建根测试套件
            root_suite = ET.Element("testsuites")
            
            for junit_file in junit_files:
                tree = ET.parse(junit_file)
                suite = tree.getroot()
                
                # 添加套件标识
                suite.set("name", junit_file.parent.name)
                root_suite.append(suite)
            
            # 保存合并的报告
            consolidated_path = Path("test-results/reports/consolidated-junit.xml")
            tree = ET.ElementTree(root_suite)
            tree.write(consolidated_path, encoding='utf-8', xml_declaration=True)
            
            return str(consolidated_path)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to generate consolidated JUnit report: {e}")
            return None
    
    async def _update_quality_dashboard(self, test_results: Dict[str, Any]):
        """更新质量仪表板"""
        try:
            # 导入测试结果到仪表板数据库
            results_file = Path("test-results/orchestration-summary.json")
            self.dashboard_generator.import_test_results(str(results_file))
            
            # 生成HTML仪表板
            dashboard_path = self.dashboard_generator.generate_html_dashboard(
                "test-results/dashboard.html"
            )
            self.logger.info(f"✅ Updated quality dashboard: {dashboard_path}")
            
            # 生成图表（如果支持）
            try:
                self.dashboard_generator.generate_charts("test-results/charts")
                self.logger.info("✅ Generated quality charts")
            except Exception as e:
                self.logger.warning(f"⚠️ Chart generation failed: {e}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to update dashboard: {e}")
    
    async def cleanup_test_environment(self, test_results: Dict[str, Any]):
        """清理测试环境"""
        try:
            # 根据测试结果决定清理策略
            has_failures = test_results.get('summary', {}).get('failed_suites', 0) > 0
            
            if has_failures:
                self.logger.info("⚠️ Tests had failures, preserving test data for analysis")
                await self.data_manager.preserve_test_data("test-results/preserved-data")
            else:
                self.logger.info("🧹 Cleaning up test data")
                await self.data_manager.cleanup_test_environment()
            
            # 压缩日志文件
            await self._compress_log_files()
            
            self.logger.info("✅ Test environment cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup failed: {e}")
    
    async def _compress_log_files(self):
        """压缩日志文件"""
        try:
            import gzip
            import shutil
            
            log_files = list(Path("logs").glob("*.log"))
            compressed_count = 0
            
            for log_file in log_files:
                if log_file.stat().st_size > 1024 * 1024:  # 大于1MB的文件进行压缩
                    compressed_file = log_file.with_suffix(log_file.suffix + '.gz')
                    
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(compressed_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    log_file.unlink()  # 删除原文件
                    compressed_count += 1
            
            if compressed_count > 0:
                self.logger.info(f"🗜️ Compressed {compressed_count} log files")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Log compression failed: {e}")
    
    def _print_summary(self, test_results: Dict[str, Any]):
        """打印执行摘要"""
        summary = test_results.get('summary', {})
        execution_time = test_results.get('execution_time', {})
        quality_gates = test_results.get('quality_gates', {})
        
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE TEST EXECUTION SUMMARY")
        print("="*80)
        
        print(f"⏱️  Total Duration: {execution_time.get('duration_formatted', 'Unknown')}")
        print(f"📊 Total Test Suites: {summary.get('total_suites', 0)}")
        print(f"✅ Passed Suites: {summary.get('passed_suites', 0)}")
        print(f"❌ Failed Suites: {summary.get('failed_suites', 0)}")
        print(f"🧪 Total Tests: {summary.get('total_tests', 0)}")
        print(f"📈 Success Rate: {summary.get('success_rate', 0):.1f}%")
        print(f"🎯 Overall Coverage: {summary.get('overall_coverage', 0):.1f}%")
        
        # 质量门限状态
        quality_status = "✅ PASSED" if quality_gates.get('passed', False) else "❌ FAILED"
        print(f"🚪 Quality Gates: {quality_status}")
        
        if quality_gates.get('issues'):
            print("\n🚨 Quality Issues:")
            for issue in quality_gates['issues']:
                print(f"  • {issue}")
        
        print("\n📋 Generated Artifacts:")
        artifacts = [
            "test-results/reports/comprehensive-report.html",
            "test-results/reports/test-summary.md", 
            "test-results/dashboard.html",
            "test-results/orchestration-summary.json"
        ]
        
        for artifact in artifacts:
            if Path(artifact).exists():
                print(f"  ✅ {artifact}")
            else:
                print(f"  ❌ {artifact}")
        
        print("\n🚀 Next Steps:")
        if quality_gates.get('passed', False) and summary.get('failed_suites', 0) == 0:
            print("  • All tests passed and quality gates met!")
            print("  • Review the comprehensive report for detailed insights")
            print("  • Monitor the quality dashboard for trends")
        else:
            print("  • Review failed tests and quality issues")
            print("  • Check detailed logs in test-results/logs/")
            print("  • Address quality gate failures before deployment")
        
        print("="*80)
    
    async def run(self, suites_filter: Optional[List[str]] = None,
                 parallel_execution: bool = True,
                 skip_prerequisites: bool = False) -> int:
        """运行完整的测试流程"""
        self.start_time = datetime.now()
        
        try:
            self._print_banner()
            
            # 检查前提条件
            if not skip_prerequisites and not self._check_prerequisites():
                return 1
            
            # 设置测试环境
            await self.setup_test_environment()
            
            # 运行测试阶段
            test_results = await self.run_test_phases(
                suites_filter=suites_filter,
                parallel_execution=parallel_execution
            )
            
            # 打印摘要
            self._print_summary(test_results)
            
            # 根据结果返回退出码
            quality_passed = test_results.get('quality_gates', {}).get('passed', False)
            has_failures = test_results.get('summary', {}).get('failed_suites', 0) > 0
            
            if not quality_passed or has_failures:
                self.logger.warning("⚠️ Test execution completed with issues")
                return 1
            else:
                self.logger.info("🎉 Test execution completed successfully!")
                return 0
        
        except KeyboardInterrupt:
            self.logger.warning("⚠️ Test execution interrupted by user")
            return 130
        
        except Exception as e:
            self.logger.error(f"❌ Test execution failed: {e}")
            return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI Teaching Assistant Comprehensive Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                          # Run all test suites
  python run_tests.py -s unit_tests api_tests # Run specific suites
  python run_tests.py --sequential             # Run suites sequentially
  python run_tests.py --quick                  # Quick test run (skip performance tests)
  python run_tests.py --config custom.yml     # Use custom configuration
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        default='test-orchestration.yml',
        help='Test orchestration configuration file'
    )
    
    parser.add_argument(
        '--suites', '-s',
        nargs='*',
        help='Specific test suites to run (e.g., unit_tests api_tests)'
    )
    
    parser.add_argument(
        '--sequential',
        action='store_true',
        help='Run test suites sequentially instead of in parallel'
    )
    
    parser.add_argument(
        '--skip-prerequisites',
        action='store_true',
        help='Skip prerequisites check (use with caution)'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick test run (exclude slow test suites)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 快速模式：排除慢速测试
    if args.quick and not args.suites:
        args.suites = ['unit_tests', 'integration_tests', 'api_tests']
        print("🚀 Quick mode: Running unit, integration, and API tests only")
    
    # 创建并运行测试运行器
    runner = ComprehensiveTestRunner(args.config)
    
    try:
        exit_code = asyncio.run(runner.run(
            suites_filter=args.suites,
            parallel_execution=not args.sequential,
            skip_prerequisites=args.skip_prerequisites
        ))
        sys.exit(exit_code)
    
    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted")
        sys.exit(130)


if __name__ == "__main__":
    main()