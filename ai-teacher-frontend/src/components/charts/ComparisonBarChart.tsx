/**
 * Comparison Bar Chart Component
 * 对比柱状图
 *
 * 用于对比学生成绩与班级/年级平均等数据
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

export interface ComparisonDataset {
  label: string;
  values: number[];
  color?: string;
}

interface ComparisonBarChartProps {
  categories: string[];
  datasets: ComparisonDataset[];
  title?: string;
  height?: number;
  horizontal?: boolean;
  showValues?: boolean;
  maxValue?: number;
  className?: string;
}

// 默认颜色方案
const defaultColors = [
  { bg: 'rgba(59, 130, 246, 0.7)', border: 'rgb(59, 130, 246)' }, // blue
  { bg: 'rgba(34, 197, 94, 0.7)', border: 'rgb(34, 197, 94)' }, // green
  { bg: 'rgba(251, 146, 60, 0.7)', border: 'rgb(251, 146, 60)' }, // orange
  { bg: 'rgba(168, 85, 247, 0.7)', border: 'rgb(168, 85, 247)' }, // purple
  { bg: 'rgba(236, 72, 153, 0.7)', border: 'rgb(236, 72, 153)' }, // pink
];

export const ComparisonBarChart: React.FC<ComparisonBarChartProps> = ({
  categories,
  datasets,
  title = 'Comparison',
  height = 300,
  horizontal = false,
  showValues = false,
  maxValue,
  className = '',
}) => {
  const chartDatasets = datasets.map((dataset, index) => {
    const colorIndex = index % defaultColors.length;
    const colors = dataset.color
      ? { bg: `${dataset.color}b3`, border: dataset.color }
      : defaultColors[colorIndex];

    return {
      label: dataset.label,
      data: dataset.values,
      backgroundColor: colors.bg,
      borderColor: colors.border,
      borderWidth: 1,
      borderRadius: 4,
    };
  });

  const chartData = {
    labels: categories,
    datasets: chartDatasets,
  };

  const options: ChartOptions<'bar'> = {
    indexAxis: horizontal ? ('y' as const) : ('x' as const),
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: datasets.length > 1,
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
    scales: {
      x: {
        grid: {
          color: horizontal ? '#374151' : 'transparent',
        },
        ticks: {
          color: '#9ca3af',
        },
        ...(horizontal && maxValue ? { max: maxValue } : {}),
      },
      y: {
        beginAtZero: true,
        grid: {
          color: horizontal ? 'transparent' : '#374151',
        },
        ticks: {
          color: '#9ca3af',
        },
        ...(!horizontal && maxValue ? { max: maxValue } : {}),
      },
    },
  };

  // 计算各数据集的平均值
  const averages = datasets.map((dataset) => {
    const sum = dataset.values.reduce((a, b) => a + b, 0);
    return dataset.values.length > 0 ? (sum / dataset.values.length).toFixed(1) : '0';
  });

  return (
    <div className={`bg-gray-800 rounded-lg p-4 ${className}`}>
      {/* 平均值摘要 */}
      <div className="flex items-center justify-end gap-4 mb-4">
        {datasets.map((dataset, index) => (
          <div key={dataset.label} className="text-sm">
            <span className="text-gray-400">{dataset.label} Avg:</span>
            <span
              className="font-medium ml-2"
              style={{
                color: dataset.color || defaultColors[index % defaultColors.length].border,
              }}
            >
              {averages[index]}
            </span>
          </div>
        ))}
      </div>

      {/* 图表 */}
      <div style={{ height }}>
        <Bar data={chartData} options={options} />
      </div>

      {/* 数值详情表格（可选） */}
      {showValues && (
        <div className="mt-4 pt-4 border-t border-gray-700 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400">
                <th className="text-left py-1 px-2">Category</th>
                {datasets.map((ds) => (
                  <th key={ds.label} className="text-right py-1 px-2">
                    {ds.label}
                  </th>
                ))}
                {datasets.length > 1 && (
                  <th className="text-right py-1 px-2">Diff</th>
                )}
              </tr>
            </thead>
            <tbody>
              {categories.map((category, catIndex) => {
                const values = datasets.map((ds) => ds.values[catIndex] || 0);
                const diff = datasets.length > 1 ? values[0] - values[1] : 0;
                return (
                  <tr key={category} className="text-white border-t border-gray-700/50">
                    <td className="py-1 px-2 text-gray-300">{category}</td>
                    {values.map((value, valueIndex) => (
                      <td key={valueIndex} className="text-right py-1 px-2">
                        {value}
                      </td>
                    ))}
                    {datasets.length > 1 && (
                      <td
                        className={`text-right py-1 px-2 ${
                          diff > 0 ? 'text-green-400' : diff < 0 ? 'text-red-400' : 'text-gray-400'
                        }`}
                      >
                        {diff > 0 ? '+' : ''}
                        {diff.toFixed(1)}
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ComparisonBarChart;
