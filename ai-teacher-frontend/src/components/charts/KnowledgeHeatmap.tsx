/**
 * Knowledge Heatmap Component
 * 知识点掌握热力图
 *
 * 以热力图形式展示学生对各知识点的掌握程度
 */

import React, { useMemo } from 'react';

export interface KnowledgePoint {
  id: string;
  name: string;
  category: string;
  masteryLevel: number; // 0-100
  practiceCount: number;
  lastPracticed?: string;
}

interface KnowledgeHeatmapProps {
  knowledgePoints: KnowledgePoint[];
  title?: string;
  showLegend?: boolean;
  onPointClick?: (point: KnowledgePoint) => void;
  className?: string;
}

// 根据掌握程度获取颜色
const getMasteryColor = (level: number): string => {
  if (level >= 90) return 'bg-green-500';
  if (level >= 75) return 'bg-green-400';
  if (level >= 60) return 'bg-yellow-400';
  if (level >= 45) return 'bg-yellow-500';
  if (level >= 30) return 'bg-orange-400';
  if (level >= 15) return 'bg-orange-500';
  if (level > 0) return 'bg-red-400';
  return 'bg-gray-600';
};

// 根据掌握程度获取文字颜色
const getMasteryTextColor = (level: number): string => {
  if (level >= 60) return 'text-gray-900';
  return 'text-white';
};

// 获取掌握程度描述
const getMasteryLabel = (level: number): string => {
  if (level >= 90) return '精通';
  if (level >= 75) return '熟练';
  if (level >= 60) return '掌握';
  if (level >= 45) return '理解';
  if (level >= 30) return '入门';
  if (level >= 15) return '了解';
  if (level > 0) return '接触';
  return '未学习';
};

export const KnowledgeHeatmap: React.FC<KnowledgeHeatmapProps> = ({
  knowledgePoints,
  title = 'Knowledge Mastery',
  showLegend = true,
  onPointClick,
  className = '',
}) => {
  // 按类别分组
  const groupedPoints = useMemo(() => {
    const groups: Record<string, KnowledgePoint[]> = {};
    knowledgePoints.forEach((point) => {
      if (!groups[point.category]) {
        groups[point.category] = [];
      }
      groups[point.category].push(point);
    });
    return groups;
  }, [knowledgePoints]);

  // 计算总体统计
  const stats = useMemo(() => {
    if (knowledgePoints.length === 0) {
      return { average: 0, mastered: 0, learning: 0, notStarted: 0 };
    }
    const total = knowledgePoints.reduce((sum, p) => sum + p.masteryLevel, 0);
    const mastered = knowledgePoints.filter((p) => p.masteryLevel >= 75).length;
    const learning = knowledgePoints.filter(
      (p) => p.masteryLevel > 0 && p.masteryLevel < 75
    ).length;
    const notStarted = knowledgePoints.filter((p) => p.masteryLevel === 0).length;

    return {
      average: Math.round(total / knowledgePoints.length),
      mastered,
      learning,
      notStarted,
    };
  }, [knowledgePoints]);

  return (
    <div className={`bg-gray-800 rounded-lg p-4 ${className}`}>
      {/* 标题和统计 */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-gray-200 font-medium">{title}</h3>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-1">
            <span className="text-gray-400">Average:</span>
            <span className="text-white font-medium">{stats.average}%</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-gray-400">{stats.mastered}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-yellow-500" />
            <span className="text-gray-400">{stats.learning}</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-gray-600" />
            <span className="text-gray-400">{stats.notStarted}</span>
          </div>
        </div>
      </div>

      {/* 热力图网格 */}
      <div className="space-y-4">
        {Object.entries(groupedPoints).map(([category, points]) => (
          <div key={category}>
            <h4 className="text-gray-400 text-sm mb-2">{category}</h4>
            <div className="flex flex-wrap gap-2">
              {points.map((point) => (
                <div
                  key={point.id}
                  onClick={() => onPointClick?.(point)}
                  className={`
                    relative group cursor-pointer
                    ${getMasteryColor(point.masteryLevel)}
                    rounded px-3 py-2 min-w-[80px]
                    transition-all duration-200 hover:scale-105 hover:shadow-lg
                  `}
                  title={`${point.name}: ${point.masteryLevel}% - ${getMasteryLabel(point.masteryLevel)}`}
                >
                  <div
                    className={`text-xs font-medium ${getMasteryTextColor(point.masteryLevel)}`}
                  >
                    {point.name}
                  </div>
                  <div
                    className={`text-xs ${getMasteryTextColor(point.masteryLevel)} opacity-80`}
                  >
                    {point.masteryLevel}%
                  </div>

                  {/* Hover tooltip */}
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                    <div className="bg-gray-900 text-white text-xs rounded px-3 py-2 shadow-lg whitespace-nowrap">
                      <div className="font-medium">{point.name}</div>
                      <div className="text-gray-400">
                        Mastery: {point.masteryLevel}% ({getMasteryLabel(point.masteryLevel)})
                      </div>
                      <div className="text-gray-400">
                        Practice: {point.practiceCount} times
                      </div>
                      {point.lastPracticed && (
                        <div className="text-gray-400">Last: {point.lastPracticed}</div>
                      )}
                      <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* 图例 */}
      {showLegend && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <LegendItem color="bg-green-500" label="Mastered (90%+)" />
            <LegendItem color="bg-green-400" label="Proficient (75-89%)" />
            <LegendItem color="bg-yellow-400" label="Competent (60-74%)" />
            <LegendItem color="bg-yellow-500" label="Developing (45-59%)" />
            <LegendItem color="bg-orange-400" label="Beginner (30-44%)" />
            <LegendItem color="bg-orange-500" label="Novice (15-29%)" />
            <LegendItem color="bg-red-400" label="Started (1-14%)" />
            <LegendItem color="bg-gray-600" label="Not Started" />
          </div>
        </div>
      )}
    </div>
  );
};

// 图例项组件
const LegendItem: React.FC<{ color: string; label: string }> = ({ color, label }) => (
  <div className="flex items-center gap-1.5 text-xs text-gray-400">
    <span className={`w-3 h-3 rounded ${color}`} />
    <span>{label}</span>
  </div>
);

export default KnowledgeHeatmap;
