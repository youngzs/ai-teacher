/**
 * Submission Detail Modal Component
 * 作业提交详情模态框
 *
 * 查看和批改单个学生作业
 * Features:
 * - 代码查看与高亮
 * - AI评分和反馈显示
 * - 教师评分和批注
 * - 反馈模板快速插入
 */

import React, { useState, useCallback } from 'react';
import {
  XMarkIcon,
  SparklesIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/react/24/outline';
import type { StudentSubmission } from './BatchGradingPanel';

interface SubmissionDetailModalProps {
  submission: StudentSubmission;
  isOpen: boolean;
  onClose: () => void;
  onSaveGrade: (score: number, feedback: string) => void;
  onRequestAIGrade: () => Promise<void>;
  feedbackTemplates?: FeedbackTemplate[];
  className?: string;
}

export interface FeedbackTemplate {
  id: string;
  name: string;
  content: string;
  category: string;
}

export const SubmissionDetailModal: React.FC<SubmissionDetailModalProps> = ({
  submission,
  isOpen,
  onClose,
  onSaveGrade,
  onRequestAIGrade,
  feedbackTemplates = [],
  className = '',
}) => {
  const [teacherScore, setTeacherScore] = useState<number>(submission.teacherScore || submission.aiScore || 0);
  const [teacherFeedback, setTeacherFeedback] = useState<string>(submission.teacherFeedback || '');
  const [isRequestingAI, setIsRequestingAI] = useState(false);
  const [activeTab, setActiveTab] = useState<'code' | 'ai' | 'feedback'>('code');
  const [isSaving, setIsSaving] = useState(false);

  // 请求AI评分
  const handleRequestAI = async () => {
    setIsRequestingAI(true);
    try {
      await onRequestAIGrade();
    } finally {
      setIsRequestingAI(false);
    }
  };

  // 保存评分
  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSaveGrade(teacherScore, teacherFeedback);
      onClose();
    } finally {
      setIsSaving(false);
    }
  };

  // 插入反馈模板
  const insertTemplate = useCallback((template: FeedbackTemplate) => {
    setTeacherFeedback((prev) => {
      if (prev.trim()) {
        return prev + '\n\n' + template.content;
      }
      return template.content;
    });
  }, []);

  // 采用AI评分
  const adoptAIScore = useCallback(() => {
    if (submission.aiScore !== undefined) {
      setTeacherScore(submission.aiScore);
    }
  }, [submission.aiScore]);

  // 采用AI反馈
  const adoptAIFeedback = useCallback(() => {
    if (submission.aiFeedback) {
      setTeacherFeedback(submission.aiFeedback);
    }
  }, [submission.aiFeedback]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className={`bg-gray-800 rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] flex flex-col ${className}`}>
        {/* 头部 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-medium">
              {submission.studentName.charAt(0)}
            </div>
            <div>
              <h2 className="text-lg font-medium text-white">{submission.studentName}</h2>
              <p className="text-sm text-gray-400">{submission.exerciseTitle}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* 主体内容 */}
        <div className="flex flex-1 overflow-hidden">
          {/* 左侧: 代码和AI反馈 */}
          <div className="flex-1 flex flex-col border-r border-gray-700">
            {/* 标签页 */}
            <div className="flex border-b border-gray-700">
              <TabButton
                active={activeTab === 'code'}
                onClick={() => setActiveTab('code')}
                icon={<DocumentTextIcon className="w-4 h-4" />}
                label="代码"
              />
              <TabButton
                active={activeTab === 'ai'}
                onClick={() => setActiveTab('ai')}
                icon={<SparklesIcon className="w-4 h-4" />}
                label="AI分析"
              />
            </div>

            {/* 内容区 */}
            <div className="flex-1 overflow-auto p-4">
              {activeTab === 'code' && (
                <div className="h-full">
                  {/* 测试结果摘要 */}
                  {submission.testsPassed !== undefined && (
                    <div className="mb-4 flex items-center gap-4 p-3 bg-gray-900 rounded-lg">
                      <div className="flex items-center gap-2">
                        {submission.testsPassed === submission.totalTests ? (
                          <CheckCircleIcon className="w-5 h-5 text-green-400" />
                        ) : (
                          <XCircleIcon className="w-5 h-5 text-red-400" />
                        )}
                        <span className="text-white">
                          测试通过: {submission.testsPassed}/{submission.totalTests}
                        </span>
                      </div>
                      {submission.executionTime !== undefined && (
                        <div className="flex items-center gap-2 text-gray-400">
                          <ClockIcon className="w-4 h-4" />
                          <span>{submission.executionTime}ms</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* 代码展示 */}
                  <pre className="bg-gray-900 rounded-lg p-4 overflow-auto text-sm font-mono text-gray-300 whitespace-pre-wrap">
                    {submission.code}
                  </pre>
                </div>
              )}

              {activeTab === 'ai' && (
                <div className="space-y-4">
                  {submission.aiScore !== undefined ? (
                    <>
                      {/* AI评分 */}
                      <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-blue-400 font-medium flex items-center gap-2">
                            <SparklesIcon className="w-5 h-5" />
                            AI评分
                          </span>
                          <span className="text-2xl font-bold text-white">{submission.aiScore}</span>
                        </div>
                        <button
                          onClick={adoptAIScore}
                          className="text-sm text-blue-400 hover:text-blue-300"
                        >
                          采用此评分
                        </button>
                      </div>

                      {/* AI反馈 */}
                      {submission.aiFeedback && (
                        <div className="p-4 bg-gray-900 rounded-lg">
                          <div className="flex items-center justify-between mb-3">
                            <span className="text-gray-300 font-medium">AI反馈</span>
                            <button
                              onClick={adoptAIFeedback}
                              className="text-sm text-blue-400 hover:text-blue-300"
                            >
                              采用此反馈
                            </button>
                          </div>
                          <div className="text-gray-400 text-sm whitespace-pre-wrap">
                            {submission.aiFeedback}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-12">
                      <SparklesIcon className="w-12 h-12 text-gray-500 mb-4" />
                      <p className="text-gray-400 mb-4">尚未进行AI分析</p>
                      <button
                        onClick={handleRequestAI}
                        disabled={isRequestingAI}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg disabled:opacity-50"
                      >
                        {isRequestingAI ? (
                          <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                            分析中...
                          </>
                        ) : (
                          <>
                            <SparklesIcon className="w-4 h-4" />
                            请求AI分析
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* 右侧: 教师评分 */}
          <div className="w-96 flex flex-col">
            <div className="p-4 border-b border-gray-700">
              <h3 className="text-white font-medium flex items-center gap-2">
                <ChatBubbleLeftRightIcon className="w-5 h-5" />
                教师批改
              </h3>
            </div>

            <div className="flex-1 overflow-auto p-4 space-y-4">
              {/* 评分输入 */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">评分 (0-100)</label>
                <input
                  type="number"
                  min={0}
                  max={100}
                  value={teacherScore}
                  onChange={(e) => setTeacherScore(Math.min(100, Math.max(0, parseInt(e.target.value) || 0)))}
                  className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-lg font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* 快速评分按钮 */}
              <div className="flex gap-2">
                {[60, 70, 80, 90, 100].map((score) => (
                  <button
                    key={score}
                    onClick={() => setTeacherScore(score)}
                    className={`flex-1 py-2 rounded text-sm font-medium transition-colors ${
                      teacherScore === score
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {score}
                  </button>
                ))}
              </div>

              {/* 反馈输入 */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">反馈评语</label>
                <textarea
                  value={teacherFeedback}
                  onChange={(e) => setTeacherFeedback(e.target.value)}
                  placeholder="输入对学生的反馈..."
                  rows={6}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* 反馈模板 */}
              {feedbackTemplates.length > 0 && (
                <div>
                  <label className="block text-sm text-gray-400 mb-2">快速反馈模板</label>
                  <div className="space-y-2 max-h-40 overflow-auto">
                    {feedbackTemplates.map((template) => (
                      <button
                        key={template.id}
                        onClick={() => insertTemplate(template)}
                        className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-300 transition-colors"
                      >
                        <span className="text-gray-400 text-xs">[{template.category}]</span>{' '}
                        {template.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* 底部操作按钮 */}
            <div className="p-4 border-t border-gray-700 space-y-2">
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-green-600 hover:bg-green-500 text-white rounded-lg font-medium disabled:opacity-50 transition-colors"
              >
                {isSaving ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    保存中...
                  </>
                ) : (
                  <>
                    <CheckCircleIcon className="w-5 h-5" />
                    保存批改
                  </>
                )}
              </button>
              <button
                onClick={onClose}
                className="w-full px-4 py-2.5 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg font-medium transition-colors"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// 标签按钮组件
interface TabButtonProps {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}

const TabButton: React.FC<TabButtonProps> = ({ active, onClick, icon, label }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
      active
        ? 'text-blue-400 border-blue-400'
        : 'text-gray-400 border-transparent hover:text-gray-300'
    }`}
  >
    {icon}
    {label}
  </button>
);

export default SubmissionDetailModal;
