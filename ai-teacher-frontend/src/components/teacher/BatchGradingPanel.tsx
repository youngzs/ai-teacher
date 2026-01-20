/**
 * Batch Grading Panel Component
 * 批量批改面板
 *
 * 教师批量批改学生作业的界面
 * Features:
 * - 作业提交列表
 * - 批量AI评分
 * - 单个作业详情查看
 * - 批注和反馈
 */

import React, { useState, useMemo, useCallback } from 'react';
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  EyeIcon,
  SparklesIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  CheckIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

// 提交状态
export type SubmissionStatus = 'pending' | 'graded' | 'reviewed' | 'returned';

// 学生提交记录
export interface StudentSubmission {
  id: string;
  studentId: string;
  studentName: string;
  studentAvatar?: string;
  exerciseId: string;
  exerciseTitle: string;
  code: string;
  submittedAt: string;
  status: SubmissionStatus;
  aiScore?: number;
  teacherScore?: number;
  aiFeedback?: string;
  teacherFeedback?: string;
  testsPassed?: number;
  totalTests?: number;
  executionTime?: number;
}

interface BatchGradingPanelProps {
  submissions: StudentSubmission[];
  onViewSubmission: (submission: StudentSubmission) => void;
  onGradeSubmission: (submissionId: string, score: number, feedback: string) => void;
  onBatchAIGrade: (submissionIds: string[]) => Promise<void>;
  onReturnSubmissions: (submissionIds: string[]) => void;
  isLoading?: boolean;
  className?: string;
}

// 状态配置
const statusConfig: Record<
  SubmissionStatus,
  { label: string; color: string; bgColor: string; icon: React.ReactNode }
> = {
  pending: {
    label: '待批改',
    color: 'text-yellow-400',
    bgColor: 'bg-yellow-400/10',
    icon: <ClockIcon className="w-4 h-4" />,
  },
  graded: {
    label: 'AI已评分',
    color: 'text-blue-400',
    bgColor: 'bg-blue-400/10',
    icon: <SparklesIcon className="w-4 h-4" />,
  },
  reviewed: {
    label: '已审核',
    color: 'text-green-400',
    bgColor: 'bg-green-400/10',
    icon: <CheckCircleIcon className="w-4 h-4" />,
  },
  returned: {
    label: '已返还',
    color: 'text-gray-400',
    bgColor: 'bg-gray-400/10',
    icon: <CheckIcon className="w-4 h-4" />,
  },
};

export const BatchGradingPanel: React.FC<BatchGradingPanelProps> = ({
  submissions,
  onViewSubmission,
  onGradeSubmission,
  onBatchAIGrade,
  onReturnSubmissions,
  isLoading = false,
  className = '',
}) => {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<SubmissionStatus | 'all'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'name' | 'score'>('date');
  const [isAIGrading, setIsAIGrading] = useState(false);

  // 过滤和排序
  const filteredSubmissions = useMemo(() => {
    let result = [...submissions];

    // 搜索过滤
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (s) =>
          s.studentName.toLowerCase().includes(query) ||
          s.exerciseTitle.toLowerCase().includes(query)
      );
    }

    // 状态过滤
    if (statusFilter !== 'all') {
      result = result.filter((s) => s.status === statusFilter);
    }

    // 排序
    result.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.studentName.localeCompare(b.studentName);
        case 'score':
          return (b.aiScore || b.teacherScore || 0) - (a.aiScore || a.teacherScore || 0);
        case 'date':
        default:
          return new Date(b.submittedAt).getTime() - new Date(a.submittedAt).getTime();
      }
    });

    return result;
  }, [submissions, searchQuery, statusFilter, sortBy]);

  // 统计
  const stats = useMemo(() => {
    const total = submissions.length;
    const pending = submissions.filter((s) => s.status === 'pending').length;
    const graded = submissions.filter((s) => s.status === 'graded').length;
    const reviewed = submissions.filter((s) => s.status === 'reviewed').length;
    return { total, pending, graded, reviewed };
  }, [submissions]);

  // 选择处理
  const handleSelectAll = useCallback(() => {
    if (selectedIds.size === filteredSubmissions.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredSubmissions.map((s) => s.id)));
    }
  }, [filteredSubmissions, selectedIds]);

  const handleSelectOne = useCallback((id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  // 批量AI评分
  const handleBatchAIGrade = async () => {
    if (selectedIds.size === 0) return;
    setIsAIGrading(true);
    try {
      await onBatchAIGrade(Array.from(selectedIds));
    } finally {
      setIsAIGrading(false);
      setSelectedIds(new Set());
    }
  };

  // 批量返还
  const handleBatchReturn = () => {
    if (selectedIds.size === 0) return;
    onReturnSubmissions(Array.from(selectedIds));
    setSelectedIds(new Set());
  };

  return (
    <div className={`bg-gray-800 rounded-lg ${className}`}>
      {/* 头部统计 */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-white">批量批改</h2>
          <div className="flex items-center gap-4 text-sm">
            <StatBadge label="总计" value={stats.total} />
            <StatBadge label="待批" value={stats.pending} color="text-yellow-400" />
            <StatBadge label="AI评分" value={stats.graded} color="text-blue-400" />
            <StatBadge label="已审核" value={stats.reviewed} color="text-green-400" />
          </div>
        </div>

        {/* 工具栏 */}
        <div className="flex items-center gap-4">
          {/* 搜索框 */}
          <div className="relative flex-1 max-w-md">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="搜索学生或题目..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* 状态筛选 */}
          <div className="flex items-center gap-2">
            <FunnelIcon className="w-4 h-4 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as SubmissionStatus | 'all')}
              className="bg-gray-700 text-white text-sm rounded px-3 py-2 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">全部状态</option>
              <option value="pending">待批改</option>
              <option value="graded">AI已评分</option>
              <option value="reviewed">已审核</option>
              <option value="returned">已返还</option>
            </select>
          </div>

          {/* 排序 */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'date' | 'name' | 'score')}
            className="bg-gray-700 text-white text-sm rounded px-3 py-2 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="date">按时间排序</option>
            <option value="name">按姓名排序</option>
            <option value="score">按分数排序</option>
          </select>
        </div>
      </div>

      {/* 批量操作栏 */}
      {selectedIds.size > 0 && (
        <div className="px-4 py-3 bg-blue-500/10 border-b border-gray-700 flex items-center justify-between">
          <span className="text-blue-400 text-sm">
            已选择 {selectedIds.size} 项
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={handleBatchAIGrade}
              disabled={isAIGrading}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm disabled:opacity-50"
            >
              {isAIGrading ? (
                <ArrowPathIcon className="w-4 h-4 animate-spin" />
              ) : (
                <SparklesIcon className="w-4 h-4" />
              )}
              AI批量评分
            </button>
            <button
              onClick={handleBatchReturn}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-green-600 hover:bg-green-500 text-white rounded text-sm"
            >
              <CheckIcon className="w-4 h-4" />
              批量返还
            </button>
          </div>
        </div>
      )}

      {/* 提交列表 */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-gray-400 text-sm border-b border-gray-700">
              <th className="p-4 text-left">
                <input
                  type="checkbox"
                  checked={selectedIds.size === filteredSubmissions.length && filteredSubmissions.length > 0}
                  onChange={handleSelectAll}
                  className="rounded bg-gray-700 border-gray-600 text-blue-500 focus:ring-blue-500"
                />
              </th>
              <th className="p-4 text-left">学生</th>
              <th className="p-4 text-left">题目</th>
              <th className="p-4 text-left">提交时间</th>
              <th className="p-4 text-center">测试结果</th>
              <th className="p-4 text-center">AI评分</th>
              <th className="p-4 text-center">教师评分</th>
              <th className="p-4 text-center">状态</th>
              <th className="p-4 text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={9} className="p-8 text-center">
                  <div className="flex items-center justify-center gap-2 text-gray-400">
                    <ArrowPathIcon className="w-5 h-5 animate-spin" />
                    加载中...
                  </div>
                </td>
              </tr>
            ) : filteredSubmissions.length === 0 ? (
              <tr>
                <td colSpan={9} className="p-8 text-center text-gray-400">
                  没有找到匹配的提交记录
                </td>
              </tr>
            ) : (
              filteredSubmissions.map((submission) => (
                <SubmissionRow
                  key={submission.id}
                  submission={submission}
                  isSelected={selectedIds.has(submission.id)}
                  onSelect={() => handleSelectOne(submission.id)}
                  onView={() => onViewSubmission(submission)}
                />
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// 统计徽章组件
const StatBadge: React.FC<{ label: string; value: number; color?: string }> = ({
  label,
  value,
  color = 'text-white',
}) => (
  <div className="flex items-center gap-1">
    <span className="text-gray-400">{label}:</span>
    <span className={`font-medium ${color}`}>{value}</span>
  </div>
);

// 提交行组件
interface SubmissionRowProps {
  submission: StudentSubmission;
  isSelected: boolean;
  onSelect: () => void;
  onView: () => void;
}

const SubmissionRow: React.FC<SubmissionRowProps> = ({
  submission,
  isSelected,
  onSelect,
  onView,
}) => {
  const status = statusConfig[submission.status];
  const testResult =
    submission.testsPassed !== undefined && submission.totalTests !== undefined
      ? `${submission.testsPassed}/${submission.totalTests}`
      : '-';

  const testColor =
    submission.testsPassed === submission.totalTests
      ? 'text-green-400'
      : submission.testsPassed === 0
      ? 'text-red-400'
      : 'text-yellow-400';

  return (
    <tr className="border-b border-gray-700/50 hover:bg-gray-700/30 transition-colors">
      <td className="p-4">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={onSelect}
          className="rounded bg-gray-700 border-gray-600 text-blue-500 focus:ring-blue-500"
        />
      </td>
      <td className="p-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center text-white text-sm font-medium">
            {submission.studentName.charAt(0)}
          </div>
          <span className="text-white">{submission.studentName}</span>
        </div>
      </td>
      <td className="p-4">
        <span className="text-gray-300">{submission.exerciseTitle}</span>
      </td>
      <td className="p-4">
        <span className="text-gray-400 text-sm">
          {new Date(submission.submittedAt).toLocaleString('zh-CN')}
        </span>
      </td>
      <td className="p-4 text-center">
        <span className={`text-sm font-medium ${testColor}`}>{testResult}</span>
      </td>
      <td className="p-4 text-center">
        {submission.aiScore !== undefined ? (
          <span className="text-blue-400 font-medium">{submission.aiScore}</span>
        ) : (
          <span className="text-gray-500">-</span>
        )}
      </td>
      <td className="p-4 text-center">
        {submission.teacherScore !== undefined ? (
          <span className="text-green-400 font-medium">{submission.teacherScore}</span>
        ) : (
          <span className="text-gray-500">-</span>
        )}
      </td>
      <td className="p-4 text-center">
        <span
          className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs ${status.color} ${status.bgColor}`}
        >
          {status.icon}
          {status.label}
        </span>
      </td>
      <td className="p-4 text-center">
        <button
          onClick={onView}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-600 rounded transition-colors"
          title="查看详情"
        >
          <EyeIcon className="w-5 h-5" />
        </button>
      </td>
    </tr>
  );
};

export default BatchGradingPanel;
