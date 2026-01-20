/**
 * Progress Line Chart Component
 * 学习进度折线图
 *
 * 显示学生分数随时间的变化趋势
 */

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ChartOptions,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export interface ProgressDataPoint {
  date: string;
  score: number;
  label?: string;
}

interface ProgressLineChartProps {
  data: ProgressDataPoint[];
  title?: string;
  showArea?: boolean;
  height?: number;
  color?: string;
  className?: string;
}

export const ProgressLineChart: React.FC<ProgressLineChartProps> = ({
  data,
  title = 'Learning Progress',
  showArea = true,
  height = 300,
  color = '#3b82f6', // blue-500
  className = '',
}) => {
  const chartData = {
    labels: data.map((d) => d.date),
    datasets: [
      {
        label: 'Score',
        data: data.map((d) => d.score),
        borderColor: color,
        backgroundColor: showArea ? `${color}20` : 'transparent',
        fill: showArea,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: color,
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      },
    ],
  };

  const options: ChartOptions<'line'> = {
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
        displayColors: false,
        callbacks: {
          label: (context) => `Score: ${context.parsed.y}%`,
        },
      },
    },
    scales: {
      x: {
        grid: {
          color: '#374151',
          drawBorder: false,
        },
        ticks: {
          color: '#9ca3af',
          maxRotation: 45,
          minRotation: 0,
        },
      },
      y: {
        min: 0,
        max: 100,
        grid: {
          color: '#374151',
          drawBorder: false,
        },
        ticks: {
          color: '#9ca3af',
          callback: (value) => `${value}%`,
        },
      },
    },
    interaction: {
      mode: 'index',
      intersect: false,
    },
  };

  return (
    <div className={`bg-gray-800 rounded-lg p-4 ${className}`}>
      <div style={{ height }}>
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
};

export default ProgressLineChart;
