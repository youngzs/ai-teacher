#!/usr/bin/env python3
"""
AI Teaching Assistant System - Test Quality Dashboard Generator
测试质量仪表板生成器

This script generates comprehensive quality dashboards including:
- Real-time test execution monitoring
- Historical trend analysis
- Quality metrics visualization  
- Performance benchmarking
- Interactive HTML dashboards
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import argparse

# 尝试导入可选依赖
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import seaborn as sns
    import pandas as pd
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("⚠️ Visualization libraries not available. Install with: pip install matplotlib seaborn pandas")


class TestDashboardGenerator:
    """测试质量仪表板生成器"""
    
    def __init__(self, db_path: str = "test-results/test_history.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = self._setup_logging()
        self._init_database()
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger('dashboard_generator')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    suite_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    duration REAL NOT NULL,
                    passed INTEGER NOT NULL,
                    failed INTEGER NOT NULL,
                    skipped INTEGER NOT NULL,
                    coverage REAL NOT NULL,
                    quality_score REAL NOT NULL,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    threshold_min REAL,
                    threshold_max REAL,
                    status TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_runs_timestamp 
                ON test_runs(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_runs_suite 
                ON test_runs(suite_name, timestamp)
            """)
    
    def import_test_results(self, results_file: str):
        """导入测试结果到数据库"""
        results_path = Path(results_file)
        
        if not results_path.exists():
            self.logger.error(f"Results file not found: {results_file}")
            return
        
        try:
            with open(results_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with sqlite3.connect(self.db_path) as conn:
                timestamp = data.get('timestamp', datetime.now().isoformat())
                
                # 导入套件结果
                for suite in data.get('suite_results', []):
                    quality_score = self._calculate_quality_score(suite)
                    
                    conn.execute("""
                        INSERT INTO test_runs 
                        (timestamp, suite_name, status, duration, passed, failed, skipped, coverage, quality_score, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        timestamp,
                        suite['name'],
                        suite['status'],
                        suite['duration'],
                        suite['passed'],
                        suite['failed'],
                        suite['skipped'],
                        suite['coverage'],
                        quality_score,
                        json.dumps({'log_file': suite.get('log_file', '')})
                    ))
                
                # 导入质量指标
                summary = data.get('summary', {})
                self._store_quality_metrics(conn, timestamp, summary)
                
            self.logger.info(f"✅ Imported test results from {results_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to import results: {e}")
    
    def _calculate_quality_score(self, suite_result: Dict[str, Any]) -> float:
        """计算质量分数 (0-100)"""
        # 基础分数计算
        total_tests = suite_result['passed'] + suite_result['failed'] + suite_result['skipped']
        
        if total_tests == 0:
            return 0.0
        
        # 成功率权重 (50%)
        success_rate = suite_result['passed'] / total_tests
        success_score = success_rate * 50
        
        # 覆盖率权重 (30%)
        coverage_score = min(suite_result['coverage'], 100) * 0.3
        
        # 执行时间惩罚 (20%) - 假设理想执行时间为300秒
        ideal_duration = 300
        duration_penalty = max(0, 20 - (suite_result['duration'] / ideal_duration) * 20)
        
        return min(100, success_score + coverage_score + duration_penalty)
    
    def _store_quality_metrics(self, conn: sqlite3.Connection, timestamp: str, summary: Dict[str, Any]):
        """存储质量指标"""
        metrics = [
            ('success_rate', summary.get('success_rate', 0), 80, 100),
            ('overall_coverage', summary.get('overall_coverage', 0), 70, 90),
            ('total_tests', summary.get('total_tests', 0), 0, None),
            ('failed_tests', summary.get('failed_tests', 0), None, 10)
        ]
        
        for metric_name, value, threshold_min, threshold_max in metrics:
            # 确定状态
            status = 'good'
            if threshold_min is not None and value < threshold_min:
                status = 'warning'
            if threshold_max is not None and value > threshold_max:
                status = 'critical'
            
            conn.execute("""
                INSERT INTO quality_metrics 
                (timestamp, metric_name, metric_value, threshold_min, threshold_max, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, metric_name, value, threshold_min, threshold_max, status))
    
    def generate_html_dashboard(self, output_file: str = "test-results/dashboard.html", 
                              days_back: int = 30) -> str:
        """生成HTML仪表板"""
        dashboard_path = Path(output_file)
        dashboard_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 获取数据
        trend_data = self._get_trend_data(days_back)
        current_metrics = self._get_current_metrics()
        suite_performance = self._get_suite_performance()
        
        # 生成HTML
        html_content = self._generate_html_template(trend_data, current_metrics, suite_performance)
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"✅ Generated HTML dashboard: {dashboard_path}")
        return str(dashboard_path)
    
    def _get_trend_data(self, days_back: int) -> Dict[str, List]:
        """获取趋势数据"""
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # 获取每日汇总
            cursor = conn.execute("""
                SELECT 
                    DATE(timestamp) as test_date,
                    COUNT(*) as total_runs,
                    AVG(quality_score) as avg_quality,
                    AVG(coverage) as avg_coverage,
                    SUM(passed) as total_passed,
                    SUM(failed) as total_failed
                FROM test_runs 
                WHERE timestamp > ?
                GROUP BY DATE(timestamp)
                ORDER BY test_date
            """, (cutoff_date,))
            
            daily_data = cursor.fetchall()
            
        return {
            'dates': [row[0] for row in daily_data],
            'total_runs': [row[1] for row in daily_data],
            'avg_quality': [row[2] for row in daily_data],
            'avg_coverage': [row[3] for row in daily_data],
            'total_passed': [row[4] for row in daily_data],
            'total_failed': [row[5] for row in daily_data]
        }
    
    def _get_current_metrics(self) -> Dict[str, Any]:
        """获取当前指标"""
        with sqlite3.connect(self.db_path) as conn:
            # 最新测试运行汇总
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_suites,
                    AVG(quality_score) as avg_quality,
                    AVG(coverage) as avg_coverage,
                    SUM(passed) as total_passed,
                    SUM(failed) as total_failed,
                    SUM(skipped) as total_skipped
                FROM test_runs 
                WHERE DATE(timestamp) = DATE('now')
            """)
            
            current_data = cursor.fetchone()
            
            # 获取最新质量指标状态
            cursor = conn.execute("""
                SELECT metric_name, metric_value, status
                FROM quality_metrics 
                WHERE timestamp = (SELECT MAX(timestamp) FROM quality_metrics)
            """)
            
            quality_metrics = {row[0]: {'value': row[1], 'status': row[2]} 
                             for row in cursor.fetchall()}
            
        return {
            'total_suites': current_data[0] or 0,
            'avg_quality': round(current_data[1] or 0, 1),
            'avg_coverage': round(current_data[2] or 0, 1),
            'total_passed': current_data[3] or 0,
            'total_failed': current_data[4] or 0,
            'total_skipped': current_data[5] or 0,
            'quality_metrics': quality_metrics
        }
    
    def _get_suite_performance(self) -> List[Dict[str, Any]]:
        """获取套件性能数据"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    suite_name,
                    COUNT(*) as run_count,
                    AVG(quality_score) as avg_quality,
                    AVG(duration) as avg_duration,
                    AVG(coverage) as avg_coverage,
                    SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
                FROM test_runs 
                WHERE timestamp > date('now', '-7 days')
                GROUP BY suite_name
                ORDER BY avg_quality DESC
            """)
            
            return [
                {
                    'name': row[0],
                    'run_count': row[1],
                    'avg_quality': round(row[2], 1),
                    'avg_duration': round(row[3], 1),
                    'avg_coverage': round(row[4], 1),
                    'success_rate': round(row[5], 1)
                }
                for row in cursor.fetchall()
            ]
    
    def _generate_html_template(self, trend_data: Dict, current_metrics: Dict, 
                              suite_performance: List[Dict]) -> str:
        """生成HTML模板"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Teaching Assistant - Test Quality Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .metric-card {{ transition: all 0.3s ease; }}
        .metric-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
        .status-good {{ @apply bg-green-100 text-green-800 border-green-200; }}
        .status-warning {{ @apply bg-yellow-100 text-yellow-800 border-yellow-200; }}
        .status-critical {{ @apply bg-red-100 text-red-800 border-red-200; }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <!-- 标题栏 -->
        <div class="mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-2">🎯 Test Quality Dashboard</h1>
            <p class="text-gray-600">AI Teaching Assistant System - Quality Monitoring</p>
            <p class="text-sm text-gray-500">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <!-- 当前指标卡片 -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="metric-card bg-white rounded-lg p-6 shadow-lg border">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">测试套件</p>
                        <p class="text-2xl font-bold text-gray-900">{current_metrics['total_suites']}</p>
                    </div>
                    <div class="p-3 bg-blue-100 rounded-full">
                        <span class="text-blue-600 text-xl">📊</span>
                    </div>
                </div>
            </div>

            <div class="metric-card bg-white rounded-lg p-6 shadow-lg border">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">平均质量分</p>
                        <p class="text-2xl font-bold text-gray-900">{current_metrics['avg_quality']}/100</p>
                    </div>
                    <div class="p-3 bg-green-100 rounded-full">
                        <span class="text-green-600 text-xl">⭐</span>
                    </div>
                </div>
                <div class="mt-2">
                    <div class="bg-gray-200 rounded-full h-2">
                        <div class="bg-green-500 h-2 rounded-full" style="width: {current_metrics['avg_quality']}%"></div>
                    </div>
                </div>
            </div>

            <div class="metric-card bg-white rounded-lg p-6 shadow-lg border">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">代码覆盖率</p>
                        <p class="text-2xl font-bold text-gray-900">{current_metrics['avg_coverage']}%</p>
                    </div>
                    <div class="p-3 bg-purple-100 rounded-full">
                        <span class="text-purple-600 text-xl">🎯</span>
                    </div>
                </div>
                <div class="mt-2">
                    <div class="bg-gray-200 rounded-full h-2">
                        <div class="bg-purple-500 h-2 rounded-full" style="width: {current_metrics['avg_coverage']}%"></div>
                    </div>
                </div>
            </div>

            <div class="metric-card bg-white rounded-lg p-6 shadow-lg border">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">测试通过率</p>
                        <p class="text-2xl font-bold text-gray-900">
                            {round(current_metrics['total_passed'] / max(current_metrics['total_passed'] + current_metrics['total_failed'], 1) * 100, 1)}%
                        </p>
                    </div>
                    <div class="p-3 bg-red-100 rounded-full">
                        <span class="text-red-600 text-xl">✅</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- 图表区域 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <div class="bg-white rounded-lg p-6 shadow-lg border">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">📈 质量趋势 (30天)</h3>
                <canvas id="qualityTrendChart" width="400" height="200"></canvas>
            </div>

            <div class="bg-white rounded-lg p-6 shadow-lg border">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">🎯 覆盖率趋势</h3>
                <canvas id="coverageTrendChart" width="400" height="200"></canvas>
            </div>
        </div>

        <!-- 套件性能表格 -->
        <div class="bg-white rounded-lg shadow-lg border overflow-hidden">
            <div class="px-6 py-4 bg-gray-50 border-b">
                <h3 class="text-lg font-semibold text-gray-900">🏆 套件性能 (最近7天)</h3>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">套件名称</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">执行次数</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">质量分</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">成功率</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">平均耗时</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">覆盖率</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {self._generate_suite_table_rows(suite_performance)}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // 质量趋势图表
        const qualityCtx = document.getElementById('qualityTrendChart').getContext('2d');
        new Chart(qualityCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(trend_data['dates'])},
                datasets: [{{
                    label: '平均质量分',
                    data: {json.dumps(trend_data['avg_quality'])},
                    borderColor: 'rgb(34, 197, 94)',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});

        // 覆盖率趋势图表
        const coverageCtx = document.getElementById('coverageTrendChart').getContext('2d');
        new Chart(coverageCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(trend_data['dates'])},
                datasets: [{{
                    label: '平均覆盖率',
                    data: {json.dumps(trend_data['avg_coverage'])},
                    borderColor: 'rgb(168, 85, 247)',
                    backgroundColor: 'rgba(168, 85, 247, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});

        // 自动刷新
        setTimeout(() => {{
            location.reload();
        }}, 300000); // 5分钟自动刷新
    </script>
</body>
</html>
"""
    
    def _generate_suite_table_rows(self, suite_performance: List[Dict]) -> str:
        """生成套件表格行"""
        if not suite_performance:
            return '<tr><td colspan="6" class="px-6 py-4 text-center text-gray-500">暂无数据</td></tr>'
        
        rows = []
        for suite in suite_performance:
            quality_color = "text-green-600" if suite['avg_quality'] >= 80 else "text-yellow-600" if suite['avg_quality'] >= 60 else "text-red-600"
            success_color = "text-green-600" if suite['success_rate'] >= 95 else "text-yellow-600" if suite['success_rate'] >= 80 else "text-red-600"
            coverage_color = "text-green-600" if suite['avg_coverage'] >= 80 else "text-yellow-600" if suite['avg_coverage'] >= 60 else "text-red-600"
            
            rows.append(f"""
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{suite['name']}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{suite['run_count']}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm {quality_color}">{suite['avg_quality']}/100</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm {success_color}">{suite['success_rate']}%</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{suite['avg_duration']}s</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm {coverage_color}">{suite['avg_coverage']}%</td>
                </tr>
            """)
        
        return '\n'.join(rows)
    
    def generate_charts(self, output_dir: str = "test-results/charts", days_back: int = 30):
        """生成图表文件"""
        if not VISUALIZATION_AVAILABLE:
            self.logger.warning("Visualization libraries not available, skipping chart generation")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 获取数据
        trend_data = self._get_trend_data(days_back)
        
        if not trend_data['dates']:
            self.logger.warning("No trend data available for chart generation")
            return
        
        # 设置样式
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 质量趋势图
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('AI Teaching Assistant - Test Quality Dashboard', fontsize=16, fontweight='bold')
        
        dates = pd.to_datetime(trend_data['dates'])
        
        # 质量分趋势
        ax1.plot(dates, trend_data['avg_quality'], marker='o', linewidth=2, markersize=4)
        ax1.set_title('Average Quality Score Trend')
        ax1.set_ylabel('Quality Score')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax1.tick_params(axis='x', rotation=45)
        
        # 覆盖率趋势
        ax2.plot(dates, trend_data['avg_coverage'], marker='s', color='purple', linewidth=2, markersize=4)
        ax2.set_title('Average Coverage Trend')
        ax2.set_ylabel('Coverage (%)')
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax2.tick_params(axis='x', rotation=45)
        
        # 测试执行次数
        ax3.bar(dates, trend_data['total_runs'], alpha=0.7, color='skyblue')
        ax3.set_title('Daily Test Runs')
        ax3.set_ylabel('Number of Runs')
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax3.tick_params(axis='x', rotation=45)
        
        # 通过/失败比例
        ax4.bar(dates, trend_data['total_passed'], label='Passed', alpha=0.8, color='green')
        ax4.bar(dates, trend_data['total_failed'], bottom=trend_data['total_passed'], 
               label='Failed', alpha=0.8, color='red')
        ax4.set_title('Test Results Distribution')
        ax4.set_ylabel('Number of Tests')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        chart_path = output_path / 'quality_dashboard.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"✅ Generated quality dashboard chart: {chart_path}")
        
        # 套件性能对比图
        suite_data = self._get_suite_performance()
        if suite_data:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            fig.suptitle('Test Suite Performance Analysis', fontsize=14, fontweight='bold')
            
            suite_names = [suite['name'] for suite in suite_data]
            quality_scores = [suite['avg_quality'] for suite in suite_data]
            coverage_scores = [suite['avg_coverage'] for suite in suite_data]
            
            # 质量分对比
            bars1 = ax1.barh(suite_names, quality_scores, color=plt.cm.RdYlGn([q/100 for q in quality_scores]))
            ax1.set_title('Average Quality Score by Suite')
            ax1.set_xlabel('Quality Score')
            ax1.grid(True, alpha=0.3, axis='x')
            
            # 添加数值标签
            for bar, score in zip(bars1, quality_scores):
                ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                        f'{score:.1f}', ha='left', va='center')
            
            # 覆盖率对比
            bars2 = ax2.barh(suite_names, coverage_scores, color=plt.cm.viridis([c/100 for c in coverage_scores]))
            ax2.set_title('Average Coverage by Suite')
            ax2.set_xlabel('Coverage (%)')
            ax2.grid(True, alpha=0.3, axis='x')
            
            # 添加数值标签
            for bar, score in zip(bars2, coverage_scores):
                ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                        f'{score:.1f}%', ha='left', va='center')
            
            plt.tight_layout()
            suite_chart_path = output_path / 'suite_performance.png'
            plt.savefig(suite_chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"✅ Generated suite performance chart: {suite_chart_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Test Quality Dashboard Generator")
    
    parser.add_argument(
        '--import-results', '-i',
        help='Import test results from JSON file'
    )
    
    parser.add_argument(
        '--generate-dashboard', '-d',
        help='Generate HTML dashboard',
        default='test-results/dashboard.html'
    )
    
    parser.add_argument(
        '--generate-charts', '-c',
        action='store_true',
        help='Generate chart files'
    )
    
    parser.add_argument(
        '--days-back',
        type=int,
        default=30,
        help='Number of days to include in analysis'
    )
    
    parser.add_argument(
        '--db-path',
        default='test-results/test_history.db',
        help='Database path for storing test history'
    )
    
    args = parser.parse_args()
    
    dashboard = TestDashboardGenerator(args.db_path)
    
    try:
        if args.import_results:
            dashboard.import_test_results(args.import_results)
        
        if args.generate_dashboard:
            dashboard_path = dashboard.generate_html_dashboard(args.generate_dashboard, args.days_back)
            print(f"✅ Dashboard generated: {dashboard_path}")
        
        if args.generate_charts:
            dashboard.generate_charts(days_back=args.days_back)
            print("✅ Charts generated successfully")
        
        if not any([args.import_results, args.generate_dashboard, args.generate_charts]):
            # 默认生成仪表板
            dashboard_path = dashboard.generate_html_dashboard(days_back=args.days_back)
            print(f"✅ Default dashboard generated: {dashboard_path}")
    
    except Exception as e:
        print(f"❌ Dashboard generation failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())