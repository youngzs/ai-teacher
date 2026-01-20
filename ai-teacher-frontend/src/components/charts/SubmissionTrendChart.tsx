/**
 * Submission Trend Chart Component
 * 提交趋势图
 *
 * 显示代码提交数量和成功率的趋势变化
 */

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import { Chart } from 'react-chartjs-2';

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export interface SubmissionData {
  date: string;
  totalSubmissions: number;
  successfulSubmissions: number;
  uniqueStudents?: number;
}

interface SubmissionTrendChartProps {
  data: SubmissionData[];
  title?: string;
  height?: number;
  showSuccessRate?: boolean;
  showStudentCount?: boolean;
  className?: string;
}

export const SubmissionTrendChart: React.FC<SubmissionTrendChartProps> = ({
  data,
  title = 'Submission Trends',
  height = 300,
  showSuccessRate = true,
  showStudentCount = false,
  className = '',
}) => {
  const labels = data.map((d) => d.date);
  const totalSubmissions = data.map((d) => d.totalSubmissions);
  const successRates = data.map((d) =>
    d.totalSubmissions > 0
      ? Math.round((d.successfulSubmissions / d.totalSubmissions) * 100)
      : 0
  );
  const studentCounts = data.map((d) => d.uniqueStudents || 0);

  // 计算统计数据
  const totalAll = totalSubmissions.reduce((sum, v) => sum + v, 0);
  const successAll = data.reduce((sum, d) => sum + d.successfulSubmissions, 0);
  const avgSuccessRate = totalAll > 0 ? Math.round((successAll / totalAll) * 100) : 0;

  const datasets: any[] = [
    {
      type: 'bar' as const,
      label: 'Total Submissions',
      data: totalSubmissions,
      backgroundColor: 'rgba(59, 130, 246, 0.7)',
      borderColor: 'rgb(59, 130, 246)',
      borderWidth: 1,
      borderRadius: 4,
      yAxisID: 'y',
      order: 2,
    },
  ];

  if (showSuccessRate) {
    datasets.push({
      type: 'line' as const,
      label: 'Success Rate (%)',
      data: successRates,
      borderColor: 'rgb(34, 197, 94)',
      backgroundColor: 'rgba(34, 197, 94, 0.1)',
      borderWidth: 2,
      pointRadius: 4,
      pointBackgroundColor: 'rgb(34, 197, 94)',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      tension: 0.3,
      fill: false,
      yAxisID: 'y1',
      order: 1,
    });
  }

  if (showStudentCount) {
    datasets.push({
      type: 'line' as const,
      label: 'Active Students',
      data: studentCounts,
      borderColor: 'rgb(251, 146, 60)',
      backgroundColor: 'rgba(251, 146, 60, 0.1)',
      borderWidth: 2,
      pointRadius: 4,
      pointBackgroundColor: 'rgb(251, 146, 60)',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      tension: 0.3,
      fill: false,
      yAxisID: 'y2',
      order: 0,
    });
  }

  const chartData = {
    labels,
    datasets,
  };

  const scales: any = {
    x: {
      grid: {
        color: '#374151',
        display: false,
      },
      ticks: {
        color: '#9ca3af',
      },
    },
    y: {
      type: 'linear' as const,
      display: true,
      position: 'left' as const,
      beginAtZero: true,
      grid: {
        color: '#374151',
      },
      ticks: {
        color: '#9ca3af',
        stepSize: 1,
      },
      title: {
        display: true,
        text: 'Submissions',
        color: '#6b7280',
      },
    },
  };

  if (showSuccessRate) {
    scales.y1 = {
      type: 'linear' as const,
      display: true,
      position: 'right' as const,
      min: 0,
      max: 100,
      grid: {
        drawOnChartArea: false,
      },
      ticks: {
        color: '#22c55e',
        callback: (value: number) => `${value}%`,
      },
      title: {
        display: true,
        text: 'Success Rate',
        color: '#22c55e',
      },
    };
  }

  if (showStudentCount) {
    scales.y2 = {
      type: 'linear' as const,
      display: true,
      position: 'right' as const,
      beginAtZero: true,
      grid: {
        drawOnChartArea: false,
      },
      ticks: {
        color: '#fb923c',
      },
      title: {
        display: true,
        text: 'Students',
        color: '#fb923c',
      },
    };
  }

  const options: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: {
          color: '#9ca3af',
          usePointStyle: true,
          padding: 16,
        },
      },
      title: {
        display: !!title,
        text: title,
        color: '#9ca3af',
        font: {
          size: 14,
          weight: 'normal',
        },
        padding: {
          bottom: 16,
        },
      },
      tooltip: {
        backgroundColor: '#1f2937',
        titleColor: '#f9fafb',
        bodyColor: '#d1d5db',
        borderColor: '#374151',
        borderWidth: 1,
        padding: 12,
      },
    },
    scales,
  };

  return (
    <div className={`bg-gray-800 rounded-lg p-4 ${className}`}>
      {/* 统计摘要 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-6">
          <div className="text-sm">
            <span className="text-gray-400">Total Submissions:</span>
            <span className="text-white font-medium ml-2">{totalAll}</span>
          </div>
          <div className="text-sm">
            <span className="text-gray-400">Avg Success Rate:</span>
            <span className="text-green-400 font-medium ml-2">{avgSuccessRate}%</span>
          </div>
        </div>
      </div>

      {/* 图表 */}
      <div style={{ height }}>
        <Chart type="bar" data={chartData} options={options} />
      </div>

      {/* 最近趋势指示 */}
      {data.length >= 2 && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="flex items-center justify-center gap-6">
            <TrendIndicator
              label="Submissions"
              current={totalSubmissions[totalSubmissions.length - 1]}
              previous={totalSubmissions[totalSubmissions.length - 2]}
            />
            {showSuccessRate && (
              <TrendIndicator
                label="Success Rate"
                current={successRates[successRates.length - 1]}
                previous={successRates[successRates.length - 2]}
                suffix="%"
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// 趋势指示器组件
interface TrendIndicatorProps {
  label: string;
  current: number;
  previous: number;
  suffix?: string;
}

const TrendIndicator: React.FC<TrendIndicatorProps> = ({
  label,
  current,
  previous,
  suffix = '',
}) => {
  const diff = current - previous;
  const isPositive = diff > 0;
  const isNeutral = diff === 0;

  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="text-gray-400">{label}:</span>
      <span className="text-white font-medium">
        {current}
        {suffix}
      </span>
      {!isNeutral && (
        <span className={`flex items-center ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
          {isPositive ? (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          )}
          <span className="text-xs">
            {isPositive ? '+' : ''}
            {diff}
            {suffix}
          </span>
        </span>
      )}
    </div>
  );
};

export default SubmissionTrendChart;
