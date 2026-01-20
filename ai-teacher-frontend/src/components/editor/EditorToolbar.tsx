/**
 * Editor Toolbar Component
 * 代码编辑器工具栏
 *
 * Features:
 * - 语言选择
 * - 主题切换
 * - 字体大小调节
 * - 运行/保存按钮
 * - 快捷键提示
 */

import React from 'react';
import {
  PlayIcon,
  DocumentArrowDownIcon,
  SunIcon,
  MoonIcon,
  Cog6ToothIcon,
  ArrowPathIcon,
  DocumentDuplicateIcon,
  ClipboardDocumentIcon,
} from '@heroicons/react/24/outline';

export type EditorLanguage = 'c' | 'cpp' | 'python' | 'java' | 'javascript' | 'typescript';
export type EditorTheme = 'vs-dark' | 'vs-light' | 'hc-black';

interface EditorToolbarProps {
  language: EditorLanguage;
  onLanguageChange: (language: EditorLanguage) => void;
  theme: EditorTheme;
  onThemeChange: (theme: EditorTheme) => void;
  fontSize: number;
  onFontSizeChange: (size: number) => void;
  onRun?: () => void;
  onSave?: () => void;
  onReset?: () => void;
  onCopy?: () => void;
  onFormat?: () => void;
  isRunning?: boolean;
  isSaving?: boolean;
  showLanguageSelector?: boolean;
  showThemeSelector?: boolean;
  showFontSizeSelector?: boolean;
  className?: string;
}

// 支持的语言列表
const languages: { value: EditorLanguage; label: string; extension: string }[] = [
  { value: 'c', label: 'C', extension: '.c' },
  { value: 'cpp', label: 'C++', extension: '.cpp' },
  { value: 'python', label: 'Python', extension: '.py' },
  { value: 'java', label: 'Java', extension: '.java' },
  { value: 'javascript', label: 'JavaScript', extension: '.js' },
  { value: 'typescript', label: 'TypeScript', extension: '.ts' },
];

// 主题列表
const themes: { value: EditorTheme; label: string; icon: React.ReactNode }[] = [
  { value: 'vs-dark', label: 'Dark', icon: <MoonIcon className="w-4 h-4" /> },
  { value: 'vs-light', label: 'Light', icon: <SunIcon className="w-4 h-4" /> },
  { value: 'hc-black', label: 'High Contrast', icon: <Cog6ToothIcon className="w-4 h-4" /> },
];

// 字体大小选项
const fontSizes = [12, 13, 14, 15, 16, 18, 20, 22, 24];

export const EditorToolbar: React.FC<EditorToolbarProps> = ({
  language,
  onLanguageChange,
  theme,
  onThemeChange,
  fontSize,
  onFontSizeChange,
  onRun,
  onSave,
  onReset,
  onCopy,
  onFormat,
  isRunning = false,
  isSaving = false,
  showLanguageSelector = true,
  showThemeSelector = true,
  showFontSizeSelector = true,
  className = '',
}) => {
  return (
    <div
      className={`flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700 ${className}`}
    >
      {/* 左侧: 语言选择和设置 */}
      <div className="flex items-center gap-4">
        {/* 语言选择 */}
        {showLanguageSelector && (
          <div className="flex items-center gap-2">
            <label className="text-gray-400 text-sm">Language:</label>
            <select
              value={language}
              onChange={(e) => onLanguageChange(e.target.value as EditorLanguage)}
              className="bg-gray-700 text-white text-sm rounded px-2 py-1 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {languages.map((lang) => (
                <option key={lang.value} value={lang.value}>
                  {lang.label}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* 主题切换 */}
        {showThemeSelector && (
          <div className="flex items-center gap-2">
            <label className="text-gray-400 text-sm">Theme:</label>
            <select
              value={theme}
              onChange={(e) => onThemeChange(e.target.value as EditorTheme)}
              className="bg-gray-700 text-white text-sm rounded px-2 py-1 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {themes.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* 字体大小 */}
        {showFontSizeSelector && (
          <div className="flex items-center gap-2">
            <label className="text-gray-400 text-sm">Font:</label>
            <select
              value={fontSize}
              onChange={(e) => onFontSizeChange(Number(e.target.value))}
              className="bg-gray-700 text-white text-sm rounded px-2 py-1 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {fontSizes.map((size) => (
                <option key={size} value={size}>
                  {size}px
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* 右侧: 操作按钮 */}
      <div className="flex items-center gap-2">
        {/* 复制按钮 */}
        {onCopy && (
          <ToolbarButton
            icon={<ClipboardDocumentIcon className="w-4 h-4" />}
            label="Copy"
            onClick={onCopy}
            shortcut="Ctrl+C"
          />
        )}

        {/* 格式化按钮 */}
        {onFormat && (
          <ToolbarButton
            icon={<DocumentDuplicateIcon className="w-4 h-4" />}
            label="Format"
            onClick={onFormat}
            shortcut="Shift+Alt+F"
          />
        )}

        {/* 重置按钮 */}
        {onReset && (
          <ToolbarButton
            icon={<ArrowPathIcon className="w-4 h-4" />}
            label="Reset"
            onClick={onReset}
            variant="secondary"
          />
        )}

        {/* 保存按钮 */}
        {onSave && (
          <ToolbarButton
            icon={<DocumentArrowDownIcon className="w-4 h-4" />}
            label={isSaving ? 'Saving...' : 'Save'}
            onClick={onSave}
            disabled={isSaving}
            shortcut="Ctrl+S"
          />
        )}

        {/* 运行按钮 */}
        {onRun && (
          <ToolbarButton
            icon={
              isRunning ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <PlayIcon className="w-4 h-4" />
              )
            }
            label={isRunning ? 'Running...' : 'Run'}
            onClick={onRun}
            disabled={isRunning}
            variant="primary"
            shortcut="Ctrl+Enter"
          />
        )}
      </div>
    </div>
  );
};

// 工具栏按钮组件
interface ToolbarButtonProps {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'default' | 'primary' | 'secondary' | 'danger';
  shortcut?: string;
}

const ToolbarButton: React.FC<ToolbarButtonProps> = ({
  icon,
  label,
  onClick,
  disabled = false,
  variant = 'default',
  shortcut,
}) => {
  const variantClasses = {
    default:
      'bg-gray-700 hover:bg-gray-600 text-white border-gray-600',
    primary:
      'bg-green-600 hover:bg-green-500 text-white border-green-500',
    secondary:
      'bg-gray-600 hover:bg-gray-500 text-white border-gray-500',
    danger:
      'bg-red-600 hover:bg-red-500 text-white border-red-500',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        flex items-center gap-1.5 px-3 py-1.5 rounded text-sm font-medium
        border transition-colors duration-150
        ${variantClasses[variant]}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
      title={shortcut ? `${label} (${shortcut})` : label}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
};

export default EditorToolbar;
