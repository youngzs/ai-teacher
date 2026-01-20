/**
 * Skill Radar Chart Component
 * 技能雷达图
 *
 * 显示学生在各个技能维度的掌握程度
 */

import React from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import { Radar } from 'react-chartjs-2';

// 注册Chart.js组件
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

export interface SkillData {
  name: string;
  score: number;
  maxScore: number;
}

interface SkillRadarChartProps {
  skills: SkillData[];
  title?: string;
  height?: number;
  color?: string;
  compareData?: SkillData[]; // 用于对比的数据（如班级平均）
  compareLabel?: string;
  className?: string;
}

export const SkillRadarChart: React.FC<SkillRadarChartProps> = ({
  skills,
  title = 'Skill Assessment',
  height = 300,
  color = '#3b82f6', // blue-500
  compareData,
  compareLabel = 'Class Average',
  className = '',
}) => {
  const labels = skills.map((s) => s.name);
  const scores = skills.map((s) => (s.score / s.maxScore) * 100);

  const datasets = [
    {
      label: 'Your Score',
      data: scores,
      backgroundColor: `${color}40`,
      borderColor: color,
      borderWidth: 2,
      pointBackgroundColor: color,
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6,
    },
  ];

  // 添加对比数据集
  if (compareData && compareData.length === skills.length) {
    const compareScores = compareData.map((s) => (s.score / s.maxScore) * 100);
    datasets.push({
      label: compareLabel,
      data: compareScores,
      backgroundColor: '#10b98140', // green with opacity
      borderColor: '#10b981', // green-500
      borderWidth: 2,
      pointBackgroundColor: '#10b981',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6,
    });
  }

  const chartData = {
    labels,
    datasets,
  };

  const options: ChartOptions<'radar'> = {
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
        callbacks: {
          label: (context) => `${context.dataset.label}: ${context.parsed.r.toFixed(1)}%`,
        },
      },
    },
    scales: {
      r: {
        min: 0,
        max: 100,
        beginAtZero: true,
        angleLines: {
          color: '#374151',
        },
        grid: {
          color: '#374151',
        },
        pointLabels: {
          color: '#d1d5db',
          font: {
            size: 11,
          },
        },
        ticks: {
          color: '#6b7280',
          backdropColor: 'transparent',
          stepSize: 20,
          callback: (value) => `${value}%`,
        },
      },
    },
  };

  return (
    <div className={`bg-gray-800 rounded-lg p-4 ${className}`}>
      <div style={{ height }}>
        <Radar data={chartData} options={options} />
      </div>
    </div>
  );
};

export default SkillRadarChart;
