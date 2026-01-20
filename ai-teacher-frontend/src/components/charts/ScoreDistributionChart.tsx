/**
 * Score Distribution Chart Component
 * 分数分布柱状图
 *
 * 显示班级学生分数分布情况
 */

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

// 注册Chart.js组件
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export interface ScoreRange {
  label: string;
  min: number;
  max: number;
  count: number;
}

interface ScoreDistributionChartProps {
  data: ScoreRange[];
  title?: string;
  height?: number;
  highlightRange?: string; // 高亮某个分数区间
  averageScore?: number;
  className?: string;
}

// 默认分数区间
export const DEFAULT_SCORE_RANGES: Omit<ScoreRange, 'count'>[] = [
  { label: '0-59', min: 0, max: 59 },
  { label: '60-69', min: 60, max: 69 },
  { label: '70-79', min: 70, max: 79 },
  { label: '80-89', min: 80, max: 89 },
  { label: '90-100', min: 90, max: 100 },
];

// 根据分数获取颜色
const getBarColor = (label: string, highlight?: string): string => {
  const colorMap: Record<string, { bg: string; border: string }> = {
    '0-59': { bg: 'rgba(239, 68, 68, 0.7)', border: 'rgb(239, 68, 68)' },
    '60-69': { bg: 'rgba(251, 146, 60, 0.7)', border: 'rgb(251, 146, 60)' },
    '70-79': { bg: 'rgba(250, 204, 21, 0.7)', border: 'rgb(250, 204, 21)' },
    '80-89': { bg: 'rgba(74, 222, 128, 0.7)', border: 'rgb(74, 222, 128)' },
    '90-100': { bg: 'rgba(34, 197, 94, 0.7)', border: 'rgb(34, 197, 94)' },
  };

  const colors = colorMap[label] || { bg: 'rgba(59, 130, 246, 0.7)', border: 'rgb(59, 130, 246)' };

  if (highlight && label === highlight) {
    return colors.border;
  }
  return colors.bg;
};

export const ScoreDistributionChart: React.FC<ScoreDistributionChartProps> = ({
  data,
  title = 'Score Distribution',
  height = 300,
  highlightRange,
  averageScore,
  className = '',
}) => {
  const labels = data.map((d) => d.label);
  const counts = data.map((d) => d.count);
  const totalStudents = counts.reduce((sum, c) => sum + c, 0);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Number of Students',
        data: counts,
        backgroundColor: labels.map((label) => getBarColor(label, highlightRange)),
        borderColor: labels.map((label) => {
          const colorMap: Record<string, string> = {
            '0-59': 'rgb(239, 68, 68)',
            '60-69': 'rgb(251, 146, 60)',
            '70-79': 'rgb(250, 204, 21)',
            '80-89': 'rgb(74, 222, 128)',
            '90-100': 'rgb(34, 197, 94)',
          };
          return colorMap[label] || 'rgb(59, 130, 246)';
        }),
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  };

  const options: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
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
        callbacks: {
          label: (context) => {
            const count = context.parsed.y;
            const percentage = totalStudents > 0 ? ((count / totalStudents) * 100).toFixed(1) : 0;
            return `${count} students (${percentage}%)`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          color: '#374151',
          display: false,
        },
        ticks: {
          color: '#9ca3af',
        },
        title: {
          display: true,
          text: 'Score Range',
          color: '#6b7280',
        },
      },
      y: {
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
          text: 'Number of Students',
          color: '#6b7280',
        },
      },
    },
  };

  return (
    <div className={`bg-gray-800 rounded-lg p-4 ${className}`}>
      {/* 统计摘要 */}
      <div className="flex items-center justify-between mb-4">
        <div className="text-sm text-gray-400">
          Total: <span className="text-white font-medium">{totalStudents}</span> students
        </div>
        {averageScore !== undefined && (
          <div className="text-sm text-gray-400">
            Average: <span className="text-white font-medium">{averageScore.toFixed(1)}</span>
          </div>
        )}
      </div>

      {/* 图表 */}
      <div style={{ height }}>
        <Bar data={chartData} options={options} />
      </div>

      {/* 分布详情 */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="grid grid-cols-5 gap-2 text-center">
          {data.map((range) => {
            const percentage = totalStudents > 0 ? ((range.count / totalStudents) * 100).toFixed(0) : 0;
            return (
              <div
                key={range.label}
                className={`rounded p-2 ${highlightRange === range.label ? 'bg-gray-700' : ''}`}
              >
                <div className="text-xs text-gray-400">{range.label}</div>
                <div className="text-lg font-medium text-white">{range.count}</div>
                <div className="text-xs text-gray-500">{percentage}%</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// 辅助函数：从分数列表生成分布数据
export const generateScoreDistribution = (
  scores: number[],
  ranges: Omit<ScoreRange, 'count'>[] = DEFAULT_SCORE_RANGES
): ScoreRange[] => {
  return ranges.map((range) => ({
    ...range,
    count: scores.filter((s) => s >= range.min && s <= range.max).length,
  }));
};

export default ScoreDistributionChart;
