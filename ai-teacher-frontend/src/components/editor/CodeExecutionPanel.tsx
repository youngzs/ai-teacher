/**
 * Code Execution Panel Component
 * 代码执行结果面板
 *
 * Features:
 * - 执行输出显示
 * - 测试用例结果
 * - 错误信息展示
 * - 执行时间和内存统计
 */

import React, { useState } from 'react';
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  CpuChipIcon,
  ExclamationTriangleIcon,
  ChevronDownIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';

// 执行状态
export type ExecutionStatus = 'idle' | 'running' | 'success' | 'error' | 'timeout';

// 测试用例结果
export interface TestCaseResult {
  id: string;
  name: string;
  input: string;
  expectedOutput: string;
  actualOutput: string;
  passed: boolean;
  executionTime: number; // ms
  memoryUsed: number; // KB
  error?: string;
}

// 执行结果
export interface ExecutionResult {
  status: ExecutionStatus;
  output: string;
  error?: string;
  executionTime: number; // ms
  memoryUsed: number; // KB
  testResults?: TestCaseResult[];
  compilationError?: string;
}

interface CodeExecutionPanelProps {
  result: ExecutionResult | null;
  isRunning: boolean;
  onClose?: () => void;
  className?: string;
}

export const CodeExecutionPanel: React.FC<CodeExecutionPanelProps> = ({
  result,
  isRunning,
  onClose,
  className = '',
}) => {
  const [activeTab, setActiveTab] = useState<'output' | 'tests'>('output');
  const [expandedTests, setExpandedTests] = useState<Set<string>>(new Set());

  // 切换测试用例展开
  const toggleTestExpand = (testId: string) => {
    setExpandedTests((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(testId)) {
        newSet.delete(testId);
      } else {
        newSet.add(testId);
      }
      return newSet;
    });
  };

  // 获取状态图标和颜色
  const getStatusInfo = (status: ExecutionStatus) => {
    switch (status) {
      case 'success':
        return {
          icon: <CheckCircleIcon className="w-5 h-5 text-green-500" />,
          color: 'text-green-500',
          bg: 'bg-green-500/10',
          label: 'Success',
        };
      case 'error':
        return {
          icon: <XCircleIcon className="w-5 h-5 text-red-500" />,
          color: 'text-red-500',
          bg: 'bg-red-500/10',
          label: 'Error',
        };
      case 'timeout':
        return {
          icon: <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />,
          color: 'text-yellow-500',
          bg: 'bg-yellow-500/10',
          label: 'Timeout',
        };
      case 'running':
        return {
          icon: (
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          ),
          color: 'text-blue-500',
          bg: 'bg-blue-500/10',
          label: 'Running',
        };
      default:
        return {
          icon: null,
          color: 'text-gray-500',
          bg: 'bg-gray-500/10',
          label: 'Idle',
        };
    }
  };

  // 计算测试通过率
  const getTestStats = () => {
    if (!result?.testResults || result.testResults.length === 0) {
      return { passed: 0, total: 0, percentage: 0 };
    }
    const passed = result.testResults.filter((t) => t.passed).length;
    const total = result.testResults.length;
    return {
      passed,
      total,
      percentage: Math.round((passed / total) * 100),
    };
  };

  const statusInfo = result ? getStatusInfo(result.status) : getStatusInfo('idle');
  const testStats = getTestStats();

  return (
    <div
      className={`bg-gray-900 border-t border-gray-700 ${className}`}
    >
      {/* 头部 */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
        {/* 标签页 */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => setActiveTab('output')}
            className={`px-3 py-1 text-sm font-medium rounded transition-colors ${
              activeTab === 'output'
                ? 'bg-gray-700 text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Output
          </button>
          {result?.testResults && result.testResults.length > 0 && (
            <button
              onClick={() => setActiveTab('tests')}
              className={`px-3 py-1 text-sm font-medium rounded transition-colors flex items-center gap-2 ${
                activeTab === 'tests'
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Tests
              <span
                className={`text-xs px-1.5 py-0.5 rounded ${
                  testStats.percentage === 100
                    ? 'bg-green-500/20 text-green-400'
                    : 'bg-yellow-500/20 text-yellow-400'
                }`}
              >
                {testStats.passed}/{testStats.total}
              </span>
            </button>
          )}
        </div>

        {/* 状态和统计 */}
        <div className="flex items-center gap-4">
          {result && (
            <>
              {/* 执行时间 */}
              <div className="flex items-center gap-1 text-gray-400 text-sm">
                <ClockIcon className="w-4 h-4" />
                <span>{result.executionTime}ms</span>
              </div>

              {/* 内存使用 */}
              <div className="flex items-center gap-1 text-gray-400 text-sm">
                <CpuChipIcon className="w-4 h-4" />
                <span>{(result.memoryUsed / 1024).toFixed(2)}MB</span>
              </div>

              {/* 状态 */}
              <div className={`flex items-center gap-1 ${statusInfo.color}`}>
                {statusInfo.icon}
                <span className="text-sm font-medium">{statusInfo.label}</span>
              </div>
            </>
          )}

          {isRunning && (
            <div className="flex items-center gap-2 text-blue-400">
              <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
              <span className="text-sm">Running...</span>
            </div>
          )}
        </div>
      </div>

      {/* 内容区域 */}
      <div className="h-48 overflow-auto">
        {activeTab === 'output' ? (
          <OutputView result={result} isRunning={isRunning} />
        ) : (
          <TestsView
            results={result?.testResults || []}
            expandedTests={expandedTests}
            onToggleExpand={toggleTestExpand}
          />
        )}
      </div>
    </div>
  );
};

// 输出视图
const OutputView: React.FC<{
  result: ExecutionResult | null;
  isRunning: boolean;
}> = ({ result, isRunning }) => {
  if (isRunning) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span>Executing code...</span>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <span>Click "Run" to execute your code</span>
      </div>
    );
  }

  // 编译错误
  if (result.compilationError) {
    return (
      <div className="p-4">
        <div className="text-red-400 font-medium mb-2">Compilation Error:</div>
        <pre className="text-red-300 text-sm whitespace-pre-wrap font-mono bg-red-500/10 p-3 rounded">
          {result.compilationError}
        </pre>
      </div>
    );
  }

  // 运行时错误
  if (result.error) {
    return (
      <div className="p-4">
        <div className="text-red-400 font-medium mb-2">Runtime Error:</div>
        <pre className="text-red-300 text-sm whitespace-pre-wrap font-mono bg-red-500/10 p-3 rounded">
          {result.error}
        </pre>
      </div>
    );
  }

  // 正常输出
  return (
    <div className="p-4">
      <div className="text-gray-400 font-medium mb-2">Output:</div>
      <pre className="text-green-300 text-sm whitespace-pre-wrap font-mono bg-gray-800 p-3 rounded">
        {result.output || '(No output)'}
      </pre>
    </div>
  );
};

// 测试用例视图
const TestsView: React.FC<{
  results: TestCaseResult[];
  expandedTests: Set<string>;
  onToggleExpand: (id: string) => void;
}> = ({ results, expandedTests, onToggleExpand }) => {
  if (results.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <span>No test cases available</span>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-2">
      {results.map((test) => (
        <div
          key={test.id}
          className={`border rounded overflow-hidden ${
            test.passed ? 'border-green-500/30' : 'border-red-500/30'
          }`}
        >
          {/* 测试用例头部 */}
          <button
            onClick={() => onToggleExpand(test.id)}
            className={`w-full flex items-center justify-between px-3 py-2 ${
              test.passed ? 'bg-green-500/10' : 'bg-red-500/10'
            } hover:bg-opacity-20 transition-colors`}
          >
            <div className="flex items-center gap-2">
              {expandedTests.has(test.id) ? (
                <ChevronDownIcon className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronRightIcon className="w-4 h-4 text-gray-400" />
              )}
              {test.passed ? (
                <CheckCircleIcon className="w-5 h-5 text-green-500" />
              ) : (
                <XCircleIcon className="w-5 h-5 text-red-500" />
              )}
              <span className="text-white font-medium">{test.name}</span>
            </div>
            <div className="flex items-center gap-3 text-sm text-gray-400">
              <span>{test.executionTime}ms</span>
              <span>{(test.memoryUsed / 1024).toFixed(2)}MB</span>
            </div>
          </button>

          {/* 展开内容 */}
          {expandedTests.has(test.id) && (
            <div className="px-4 py-3 bg-gray-800/50 space-y-3">
              {/* 输入 */}
              <div>
                <div className="text-gray-400 text-xs mb-1">Input:</div>
                <pre className="text-gray-300 text-sm bg-gray-800 p-2 rounded font-mono">
                  {test.input || '(empty)'}
                </pre>
              </div>

              {/* 期望输出 */}
              <div>
                <div className="text-gray-400 text-xs mb-1">Expected Output:</div>
                <pre className="text-gray-300 text-sm bg-gray-800 p-2 rounded font-mono">
                  {test.expectedOutput}
                </pre>
              </div>

              {/* 实际输出 */}
              <div>
                <div className="text-gray-400 text-xs mb-1">Actual Output:</div>
                <pre
                  className={`text-sm p-2 rounded font-mono ${
                    test.passed
                      ? 'text-green-300 bg-green-500/10'
                      : 'text-red-300 bg-red-500/10'
                  }`}
                >
                  {test.actualOutput || '(empty)'}
                </pre>
              </div>

              {/* 错误信息 */}
              {test.error && (
                <div>
                  <div className="text-red-400 text-xs mb-1">Error:</div>
                  <pre className="text-red-300 text-sm bg-red-500/10 p-2 rounded font-mono">
                    {test.error}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default CodeExecutionPanel;
