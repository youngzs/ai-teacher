/**
 * Feedback Template Manager Component
 * 反馈模板管理器
 *
 * 管理和使用反馈模板的界面
 * Features:
 * - 模板分类管理
 * - 创建/编辑/删除模板
 * - 模板搜索
 * - 变量占位符支持
 */

import React, { useState, useMemo, useCallback } from 'react';
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  FolderIcon,
  DocumentTextIcon,
  XMarkIcon,
  CheckIcon,
  TagIcon,
} from '@heroicons/react/24/outline';

export interface FeedbackTemplate {
  id: string;
  name: string;
  content: string;
  category: string;
  variables?: string[]; // 变量占位符，如 {{studentName}}
  usageCount?: number;
  createdAt?: string;
  updatedAt?: string;
}

export interface TemplateCategory {
  id: string;
  name: string;
  color: string;
  templateCount: number;
}

interface FeedbackTemplateManagerProps {
  templates: FeedbackTemplate[];
  categories: TemplateCategory[];
  onCreateTemplate: (template: Omit<FeedbackTemplate, 'id'>) => void;
  onUpdateTemplate: (id: string, template: Partial<FeedbackTemplate>) => void;
  onDeleteTemplate: (id: string) => void;
  onSelectTemplate?: (template: FeedbackTemplate) => void;
  onCreateCategory?: (name: string, color: string) => void;
  mode?: 'manage' | 'select'; // manage=管理模式, select=选择模式
  className?: string;
}

// 预设分类颜色
const categoryColors = [
  '#3b82f6', // blue
  '#22c55e', // green
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#f97316', // orange
];

// 默认模板
export const DEFAULT_TEMPLATES: FeedbackTemplate[] = [
  {
    id: 'default-1',
    name: '代码规范-缩进问题',
    content: '代码缩进不一致，建议使用统一的缩进风格（如4个空格）。良好的代码缩进可以提高代码可读性。',
    category: '代码规范',
    variables: [],
  },
  {
    id: 'default-2',
    name: '代码规范-命名规范',
    content: '变量命名不够清晰，建议使用有意义的变量名。例如将 `a`, `b` 改为 `width`, `height` 等描述性名称。',
    category: '代码规范',
    variables: [],
  },
  {
    id: 'default-3',
    name: '逻辑错误-边界条件',
    content: '未处理边界条件。当输入为空或达到边界值时，程序可能产生错误。建议添加边界检查。',
    category: '逻辑错误',
    variables: [],
  },
  {
    id: 'default-4',
    name: '逻辑错误-循环条件',
    content: '循环条件存在问题，可能导致死循环或提前退出。请检查循环的终止条件是否正确。',
    category: '逻辑错误',
    variables: [],
  },
  {
    id: 'default-5',
    name: '优秀-整体表现',
    content: '代码整体表现优秀！逻辑清晰，结构合理，命名规范。继续保持！',
    category: '表扬鼓励',
    variables: [],
  },
  {
    id: 'default-6',
    name: '鼓励-进步明显',
    content: '相比之前的作业有明显进步！{{studentName}}同学在{{topic}}方面的理解更深入了。继续努力！',
    category: '表扬鼓励',
    variables: ['studentName', 'topic'],
  },
  {
    id: 'default-7',
    name: '建议-添加注释',
    content: '建议在关键代码段添加注释，说明代码的作用和逻辑。这有助于自己回顾和他人理解。',
    category: '改进建议',
    variables: [],
  },
  {
    id: 'default-8',
    name: '建议-代码重构',
    content: '建议将重复的代码提取为函数，提高代码复用性和可维护性。',
    category: '改进建议',
    variables: [],
  },
];

export const FeedbackTemplateManager: React.FC<FeedbackTemplateManagerProps> = ({
  templates,
  categories,
  onCreateTemplate,
  onUpdateTemplate,
  onDeleteTemplate,
  onSelectTemplate,
  onCreateCategory,
  mode = 'manage',
  className = '',
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | 'all'>('all');
  const [isCreating, setIsCreating] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<FeedbackTemplate | null>(null);
  const [showCategoryDialog, setShowCategoryDialog] = useState(false);

  // 过滤模板
  const filteredTemplates = useMemo(() => {
    let result = [...templates];

    // 搜索过滤
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (t) =>
          t.name.toLowerCase().includes(query) ||
          t.content.toLowerCase().includes(query)
      );
    }

    // 分类过滤
    if (selectedCategory !== 'all') {
      result = result.filter((t) => t.category === selectedCategory);
    }

    return result;
  }, [templates, searchQuery, selectedCategory]);

  // 按分类分组
  const groupedTemplates = useMemo(() => {
    const groups: Record<string, FeedbackTemplate[]> = {};
    filteredTemplates.forEach((template) => {
      if (!groups[template.category]) {
        groups[template.category] = [];
      }
      groups[template.category].push(template);
    });
    return groups;
  }, [filteredTemplates]);

  return (
    <div className={`bg-gray-800 rounded-lg ${className}`}>
      {/* 头部 */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-white">
            {mode === 'manage' ? '反馈模板管理' : '选择反馈模板'}
          </h2>
          {mode === 'manage' && (
            <div className="flex items-center gap-2">
              {onCreateCategory && (
                <button
                  onClick={() => setShowCategoryDialog(true)}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
                >
                  <FolderIcon className="w-4 h-4" />
                  新建分类
                </button>
              )}
              <button
                onClick={() => setIsCreating(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm transition-colors"
              >
                <PlusIcon className="w-4 h-4" />
                新建模板
              </button>
            </div>
          )}
        </div>

        {/* 搜索和筛选 */}
        <div className="flex items-center gap-4">
          <div className="relative flex-1 max-w-md">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="搜索模板..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* 分类筛选 */}
          <div className="flex items-center gap-2 overflow-x-auto">
            <CategoryChip
              active={selectedCategory === 'all'}
              onClick={() => setSelectedCategory('all')}
              label="全部"
              count={templates.length}
            />
            {categories.map((cat) => (
              <CategoryChip
                key={cat.id}
                active={selectedCategory === cat.name}
                onClick={() => setSelectedCategory(cat.name)}
                label={cat.name}
                count={cat.templateCount}
                color={cat.color}
              />
            ))}
          </div>
        </div>
      </div>

      {/* 模板列表 */}
      <div className="p-4 max-h-[600px] overflow-auto">
        {Object.keys(groupedTemplates).length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <DocumentTextIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>没有找到匹配的模板</p>
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(groupedTemplates).map(([category, categoryTemplates]) => (
              <div key={category}>
                <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                  <FolderIcon className="w-4 h-4" />
                  {category}
                  <span className="text-gray-500">({categoryTemplates.length})</span>
                </h3>
                <div className="grid gap-3">
                  {categoryTemplates.map((template) => (
                    <TemplateCard
                      key={template.id}
                      template={template}
                      mode={mode}
                      onEdit={() => setEditingTemplate(template)}
                      onDelete={() => onDeleteTemplate(template.id)}
                      onSelect={() => onSelectTemplate?.(template)}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 创建/编辑模板对话框 */}
      {(isCreating || editingTemplate) && (
        <TemplateDialog
          template={editingTemplate}
          categories={categories}
          onSave={(template) => {
            if (editingTemplate) {
              onUpdateTemplate(editingTemplate.id, template);
            } else {
              onCreateTemplate(template);
            }
            setIsCreating(false);
            setEditingTemplate(null);
          }}
          onClose={() => {
            setIsCreating(false);
            setEditingTemplate(null);
          }}
        />
      )}

      {/* 创建分类对话框 */}
      {showCategoryDialog && onCreateCategory && (
        <CategoryDialog
          onSave={(name, color) => {
            onCreateCategory(name, color);
            setShowCategoryDialog(false);
          }}
          onClose={() => setShowCategoryDialog(false)}
        />
      )}
    </div>
  );
};

// 分类标签组件
interface CategoryChipProps {
  active: boolean;
  onClick: () => void;
  label: string;
  count: number;
  color?: string;
}

const CategoryChip: React.FC<CategoryChipProps> = ({ active, onClick, label, count, color }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors ${
      active
        ? 'bg-blue-600 text-white'
        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
    }`}
  >
    {color && (
      <span
        className="w-2 h-2 rounded-full"
        style={{ backgroundColor: color }}
      />
    )}
    {label}
    <span className={`${active ? 'text-blue-200' : 'text-gray-500'}`}>
      ({count})
    </span>
  </button>
);

// 模板卡片组件
interface TemplateCardProps {
  template: FeedbackTemplate;
  mode: 'manage' | 'select';
  onEdit: () => void;
  onDelete: () => void;
  onSelect?: () => void;
}

const TemplateCard: React.FC<TemplateCardProps> = ({
  template,
  mode,
  onEdit,
  onDelete,
  onSelect,
}) => {
  const handleClick = () => {
    if (mode === 'select' && onSelect) {
      onSelect();
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`p-4 bg-gray-700 rounded-lg border border-gray-600 ${
        mode === 'select' ? 'cursor-pointer hover:border-blue-500' : ''
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <DocumentTextIcon className="w-4 h-4 text-gray-400" />
          <span className="font-medium text-white">{template.name}</span>
        </div>
        {mode === 'manage' && (
          <div className="flex items-center gap-1">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onEdit();
              }}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-600 rounded transition-colors"
            >
              <PencilIcon className="w-4 h-4" />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete();
              }}
              className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-gray-600 rounded transition-colors"
            >
              <TrashIcon className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
      <p className="text-gray-300 text-sm line-clamp-2">{template.content}</p>
      {template.variables && template.variables.length > 0 && (
        <div className="mt-2 flex items-center gap-1 flex-wrap">
          <TagIcon className="w-3 h-3 text-gray-500" />
          {template.variables.map((v) => (
            <span
              key={v}
              className="text-xs px-1.5 py-0.5 bg-gray-600 text-gray-300 rounded"
            >
              {`{{${v}}}`}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

// 模板编辑对话框
interface TemplateDialogProps {
  template: FeedbackTemplate | null;
  categories: TemplateCategory[];
  onSave: (template: Omit<FeedbackTemplate, 'id'>) => void;
  onClose: () => void;
}

const TemplateDialog: React.FC<TemplateDialogProps> = ({
  template,
  categories,
  onSave,
  onClose,
}) => {
  const [name, setName] = useState(template?.name || '');
  const [content, setContent] = useState(template?.content || '');
  const [category, setCategory] = useState(template?.category || categories[0]?.name || '');

  // 提取变量
  const extractedVariables = useMemo(() => {
    const matches = content.match(/\{\{(\w+)\}\}/g) || [];
    return [...new Set(matches.map((m) => m.replace(/[{}]/g, '')))];
  }, [content]);

  const handleSave = () => {
    if (!name.trim() || !content.trim()) return;
    onSave({
      name: name.trim(),
      content: content.trim(),
      category,
      variables: extractedVariables,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-gray-800 rounded-lg shadow-xl w-full max-w-lg">
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <h3 className="text-lg font-medium text-white">
            {template ? '编辑模板' : '新建模板'}
          </h3>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">模板名称</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="输入模板名称..."
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">分类</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categories.map((cat) => (
                <option key={cat.id} value={cat.name}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">
              模板内容
              <span className="text-gray-500 ml-2">
                (支持变量: {`{{变量名}}`})
              </span>
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="输入反馈内容..."
              rows={5}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {extractedVariables.length > 0 && (
            <div className="p-3 bg-gray-700/50 rounded-lg">
              <p className="text-sm text-gray-400 mb-2">检测到的变量:</p>
              <div className="flex flex-wrap gap-2">
                {extractedVariables.map((v) => (
                  <span
                    key={v}
                    className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-sm"
                  >
                    {`{{${v}}}`}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3 p-4 border-t border-gray-700">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
          >
            取消
          </button>
          <button
            onClick={handleSave}
            disabled={!name.trim() || !content.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg disabled:opacity-50 transition-colors"
          >
            <CheckIcon className="w-4 h-4" />
            保存
          </button>
        </div>
      </div>
    </div>
  );
};

// 分类创建对话框
interface CategoryDialogProps {
  onSave: (name: string, color: string) => void;
  onClose: () => void;
}

const CategoryDialog: React.FC<CategoryDialogProps> = ({ onSave, onClose }) => {
  const [name, setName] = useState('');
  const [color, setColor] = useState(categoryColors[0]);

  const handleSave = () => {
    if (!name.trim()) return;
    onSave(name.trim(), color);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-gray-800 rounded-lg shadow-xl w-full max-w-sm">
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <h3 className="text-lg font-medium text-white">新建分类</h3>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">分类名称</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="输入分类名称..."
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">分类颜色</label>
            <div className="flex flex-wrap gap-2">
              {categoryColors.map((c) => (
                <button
                  key={c}
                  onClick={() => setColor(c)}
                  className={`w-8 h-8 rounded-full transition-transform ${
                    color === c ? 'ring-2 ring-white ring-offset-2 ring-offset-gray-800 scale-110' : ''
                  }`}
                  style={{ backgroundColor: c }}
                />
              ))}
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 p-4 border-t border-gray-700">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
          >
            取消
          </button>
          <button
            onClick={handleSave}
            disabled={!name.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg disabled:opacity-50 transition-colors"
          >
            <CheckIcon className="w-4 h-4" />
            创建
          </button>
        </div>
      </div>
    </div>
  );
};

export default FeedbackTemplateManager;
