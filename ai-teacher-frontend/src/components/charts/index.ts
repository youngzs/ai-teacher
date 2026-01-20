/**
 * Charts Components Index
 * 图表组件导出
 */

// Progress Line Chart - 学习进度折线图
export { ProgressLineChart, type ProgressDataPoint } from './ProgressLineChart';
export { default as ProgressLineChartDefault } from './ProgressLineChart';

// Skill Radar Chart - 技能雷达图
export { SkillRadarChart, type SkillData } from './SkillRadarChart';
export { default as SkillRadarChartDefault } from './SkillRadarChart';

// Knowledge Heatmap - 知识点热力图
export { KnowledgeHeatmap, type KnowledgePoint } from './KnowledgeHeatmap';
export { default as KnowledgeHeatmapDefault } from './KnowledgeHeatmap';

// Score Distribution Chart - 分数分布柱状图
export {
  ScoreDistributionChart,
  type ScoreRange,
  DEFAULT_SCORE_RANGES,
  generateScoreDistribution,
} from './ScoreDistributionChart';
export { default as ScoreDistributionChartDefault } from './ScoreDistributionChart';

// Submission Trend Chart - 提交趋势图
export { SubmissionTrendChart, type SubmissionData } from './SubmissionTrendChart';
export { default as SubmissionTrendChartDefault } from './SubmissionTrendChart';

// Comparison Bar Chart - 对比柱状图
export { ComparisonBarChart, type ComparisonDataset } from './ComparisonBarChart';
export { default as ComparisonBarChartDefault } from './ComparisonBarChart';
