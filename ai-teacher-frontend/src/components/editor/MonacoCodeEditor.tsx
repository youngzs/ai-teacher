/**
 * Monaco Code Editor Component
 * 专业级代码编辑器，基于Monaco Editor
 *
 * Features:
 * - 语法高亮 (C, Python, Java, JavaScript)
 * - 代码自动补全
 * - 代码折叠
 * - 错误标记显示
 * - 主题切换
 * - 快捷键支持
 */

import React, { useRef, useCallback, useEffect, useState } from 'react';
import Editor, { Monaco, OnMount, OnChange } from '@monaco-editor/react';
import type { editor } from 'monaco-editor';

// 代码错误类型
export interface CodeError {
  line: number;
  column: number;
  endLine?: number;
  endColumn?: number;
  message: string;
  severity: 'error' | 'warning' | 'info' | 'hint';
}

// 编辑器属性
export interface MonacoCodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: 'c' | 'cpp' | 'python' | 'java' | 'javascript' | 'typescript';
  theme?: 'vs-dark' | 'vs-light' | 'hc-black';
  readOnly?: boolean;
  height?: string | number;
  errors?: CodeError[];
  onSave?: () => void;
  onRun?: () => void;
  showMinimap?: boolean;
  fontSize?: number;
  tabSize?: number;
  wordWrap?: 'on' | 'off' | 'wordWrapColumn' | 'bounded';
  lineNumbers?: 'on' | 'off' | 'relative' | 'interval';
  placeholder?: string;
  className?: string;
}

// 语言映射
const languageMap: Record<string, string> = {
  c: 'c',
  cpp: 'cpp',
  python: 'python',
  java: 'java',
  javascript: 'javascript',
  typescript: 'typescript',
};

// 严重性映射
const severityMap = (monaco: Monaco) => ({
  error: monaco.MarkerSeverity.Error,
  warning: monaco.MarkerSeverity.Warning,
  info: monaco.MarkerSeverity.Info,
  hint: monaco.MarkerSeverity.Hint,
});

export const MonacoCodeEditor: React.FC<MonacoCodeEditorProps> = ({
  value,
  onChange,
  language,
  theme = 'vs-dark',
  readOnly = false,
  height = '500px',
  errors = [],
  onSave,
  onRun,
  showMinimap = true,
  fontSize = 14,
  tabSize = 4,
  wordWrap = 'on',
  lineNumbers = 'on',
  placeholder,
  className = '',
}) => {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<Monaco | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 编辑器挂载回调
  const handleEditorMount: OnMount = useCallback(
    (editor, monaco) => {
      editorRef.current = editor;
      monacoRef.current = monaco;
      setIsLoading(false);

      // 配置快捷键
      // Ctrl/Cmd + S: 保存
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
        onSave?.();
      });

      // Ctrl/Cmd + Enter: 运行
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
        onRun?.();
      });

      // F5: 运行
      editor.addCommand(monaco.KeyCode.F5, () => {
        onRun?.();
      });

      // 自动聚焦
      editor.focus();

      // 配置C语言代码补全
      if (language === 'c' || language === 'cpp') {
        monaco.languages.registerCompletionItemProvider('c', {
          provideCompletionItems: (model, position) => {
            const suggestions = getCSnippets(monaco);
            return { suggestions };
          },
        });
      }

      // 配置Python代码补全
      if (language === 'python') {
        monaco.languages.registerCompletionItemProvider('python', {
          provideCompletionItems: (model, position) => {
            const suggestions = getPythonSnippets(monaco);
            return { suggestions };
          },
        });
      }
    },
    [onSave, onRun, language]
  );

  // 内容变化回调
  const handleChange: OnChange = useCallback(
    (newValue) => {
      onChange(newValue || '');
    },
    [onChange]
  );

  // 更新错误标记
  useEffect(() => {
    if (editorRef.current && monacoRef.current) {
      const model = editorRef.current.getModel();
      if (model) {
        const monaco = monacoRef.current;
        const severities = severityMap(monaco);

        const markers = errors.map((err) => ({
          startLineNumber: err.line,
          startColumn: err.column,
          endLineNumber: err.endLine || err.line,
          endColumn: err.endColumn || err.column + 10,
          message: err.message,
          severity: severities[err.severity],
        }));

        monaco.editor.setModelMarkers(model, 'code-errors', markers);
      }
    }
  }, [errors]);

  // 编辑器配置选项
  const editorOptions: editor.IStandaloneEditorConstructionOptions = {
    minimap: { enabled: showMinimap },
    fontSize,
    tabSize,
    lineNumbers,
    wordWrap,
    automaticLayout: true,
    readOnly,
    scrollBeyondLastLine: false,
    folding: true,
    foldingStrategy: 'indentation',
    renderLineHighlight: 'all',
    selectOnLineNumbers: true,
    roundedSelection: true,
    cursorBlinking: 'smooth',
    cursorSmoothCaretAnimation: 'on',
    smoothScrolling: true,
    contextmenu: true,
    formatOnPaste: true,
    formatOnType: true,
    suggestOnTriggerCharacters: true,
    acceptSuggestionOnEnter: 'on',
    quickSuggestions: {
      other: true,
      comments: false,
      strings: false,
    },
    parameterHints: {
      enabled: true,
    },
    bracketPairColorization: {
      enabled: true,
    },
    guides: {
      bracketPairs: true,
      indentation: true,
    },
  };

  return (
    <div className={`relative ${className}`}>
      {/* 加载状态 */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
          <div className="flex flex-col items-center gap-2">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-gray-400 text-sm">Loading Editor...</span>
          </div>
        </div>
      )}

      {/* 占位符 */}
      {!value && placeholder && !isLoading && (
        <div className="absolute top-4 left-16 text-gray-500 pointer-events-none z-5">
          {placeholder}
        </div>
      )}

      {/* Monaco Editor */}
      <Editor
        height={height}
        language={languageMap[language] || language}
        theme={theme}
        value={value}
        onChange={handleChange}
        onMount={handleEditorMount}
        options={editorOptions}
        loading={
          <div className="flex items-center justify-center h-full bg-gray-900">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        }
      />
    </div>
  );
};

// C语言代码片段
function getCSnippets(monaco: Monaco): editor.languages.CompletionItem[] {
  return [
    {
      label: 'printf',
      kind: monaco.languages.CompletionItemKind.Function,
      insertText: 'printf("${1:format}", ${2:args});',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Print formatted output to stdout',
    },
    {
      label: 'scanf',
      kind: monaco.languages.CompletionItemKind.Function,
      insertText: 'scanf("${1:format}", ${2:&var});',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Read formatted input from stdin',
    },
    {
      label: 'for',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: 'for (int ${1:i} = 0; ${1:i} < ${2:n}; ${1:i}++) {\n\t${3:// code}\n}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'For loop',
    },
    {
      label: 'while',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: 'while (${1:condition}) {\n\t${2:// code}\n}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'While loop',
    },
    {
      label: 'if',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: 'if (${1:condition}) {\n\t${2:// code}\n}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'If statement',
    },
    {
      label: 'ifelse',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: 'if (${1:condition}) {\n\t${2:// code}\n} else {\n\t${3:// code}\n}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'If-else statement',
    },
    {
      label: 'main',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: '#include <stdio.h>\n\nint main() {\n\t${1:// code}\n\treturn 0;\n}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Main function template',
    },
    {
      label: 'function',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: '${1:void} ${2:functionName}(${3:params}) {\n\t${4:// code}\n}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Function definition',
    },
    {
      label: 'struct',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: 'struct ${1:StructName} {\n\t${2:int member;}\n};',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Struct definition',
    },
    {
      label: 'malloc',
      kind: monaco.languages.CompletionItemKind.Function,
      insertText: '(${1:type}*)malloc(${2:size} * sizeof(${1:type}))',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Dynamic memory allocation',
    },
  ] as editor.languages.CompletionItem[];
}

// Python代码片段
function getPythonSnippets(monaco: Monaco): editor.languages.CompletionItem[] {
  return [
    {
      label: 'print',
      kind: monaco.languages.CompletionItemKind.Function,
      insertText: 'print(${1:message})',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Print to stdout',
    },
    {
      label: 'input',
      kind: monaco.languages.CompletionItemKind.Function,
      insertText: 'input(${1:prompt})',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Read input from stdin',
    },
    {
      label: 'for',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: 'for ${1:item} in ${2:iterable}:\n\t${3:pass}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'For loop',
    },
    {
      label: 'forrange',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: 'for ${1:i} in range(${2:n}):\n\t${3:pass}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'For loop with range',
    },
    {
      label: 'while',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: 'while ${1:condition}:\n\t${2:pass}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'While loop',
    },
    {
      label: 'if',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: 'if ${1:condition}:\n\t${2:pass}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'If statement',
    },
    {
      label: 'ifelse',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: 'if ${1:condition}:\n\t${2:pass}\nelse:\n\t${3:pass}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'If-else statement',
    },
    {
      label: 'def',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: 'def ${1:function_name}(${2:params}):\n\t${3:pass}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Function definition',
    },
    {
      label: 'class',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText:
        'class ${1:ClassName}:\n\tdef __init__(self${2:, params}):\n\t\t${3:pass}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Class definition',
    },
    {
      label: 'try',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText:
        'try:\n\t${1:pass}\nexcept ${2:Exception} as e:\n\t${3:print(e)}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Try-except block',
    },
    {
      label: 'with',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: 'with ${1:expression} as ${2:variable}:\n\t${3:pass}',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'With statement',
    },
    {
      label: 'main',
      kind: monaco.languages.CompletionItemKind.Snippet,
      insertText: 'def main():\n\t${1:pass}\n\n\nif __name__ == "__main__":\n\tmain()',
      insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
      documentation: 'Main function template',
    },
  ] as editor.languages.CompletionItem[];
}

export default MonacoCodeEditor;
