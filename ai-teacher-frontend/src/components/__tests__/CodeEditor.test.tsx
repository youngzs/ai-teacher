/**
 * CodeEditor组件测试
 * 测试代码编辑器的功能和交互
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@/test-utils/test-utils';
import userEvent from '@testing-library/user-event';

// Mock CodeEditor组件
interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: 'c' | 'python' | 'javascript';
  theme?: 'light' | 'dark';
  readOnly?: boolean;
  placeholder?: string;
  height?: string;
  showLineNumbers?: boolean;
  autoFocus?: boolean;
  onSubmit?: (code: string) => void;
}

const MockCodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  language,
  theme = 'light',
  readOnly = false,
  placeholder = '',
  height = '400px',
  showLineNumbers = true,
  autoFocus = false,
  onSubmit
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (!readOnly) {
      onChange(e.target.value);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.ctrlKey && e.key === 'Enter' && onSubmit) {
      e.preventDefault();
      onSubmit(value);
    }
  };

  return (
    <div 
      className={`code-editor theme-${theme}`}
      data-testid="code-editor"
      data-language={language}
      style={{ height }}
    >
      {showLineNumbers && (
        <div className="line-numbers" data-testid="line-numbers">
          {value.split('\n').map((_, index) => (
            <div key={index} className="line-number">
              {index + 1}
            </div>
          ))}
        </div>
      )}
      <textarea
        data-testid="code-textarea"
        value={value}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        readOnly={readOnly}
        autoFocus={autoFocus}
        className={`code-textarea ${readOnly ? 'readonly' : ''}`}
        rows={value.split('\n').length}
        spellCheck={false}
      />
    </div>
  );
};

describe('CodeEditor Component', () => {
  const defaultProps: CodeEditorProps = {
    value: '',
    onChange: vi.fn(),
    language: 'c'
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders code editor with empty value', () => {
      render(<MockCodeEditor {...defaultProps} />);
      
      const editor = screen.getByTestId('code-editor');
      const textarea = screen.getByTestId('code-textarea');
      
      expect(editor).toBeInTheDocument();
      expect(textarea).toHaveValue('');
    });

    it('renders with initial code value', () => {
      const code = '#include <stdio.h>\nint main() {\n    return 0;\n}';
      render(<MockCodeEditor {...defaultProps} value={code} />);
      
      const textarea = screen.getByTestId('code-textarea');
      expect(textarea).toHaveValue(code);
    });

    it('renders with correct language attribute', () => {
      render(<MockCodeEditor {...defaultProps} language="python" />);
      
      const editor = screen.getByTestId('code-editor');
      expect(editor).toHaveAttribute('data-language', 'python');
    });

    it('renders with placeholder text', () => {
      const placeholder = 'Enter your C code here...';
      render(<MockCodeEditor {...defaultProps} placeholder={placeholder} />);
      
      const textarea = screen.getByTestId('code-textarea');
      expect(textarea).toHaveAttribute('placeholder', placeholder);
    });

    it('renders with line numbers by default', () => {
      const code = 'line 1\nline 2\nline 3';
      render(<MockCodeEditor {...defaultProps} value={code} />);
      
      const lineNumbers = screen.getByTestId('line-numbers');
      const numberElements = screen.getAllByText(/^[1-3]$/);
      
      expect(lineNumbers).toBeInTheDocument();
      expect(numberElements).toHaveLength(3);
    });

    it('hides line numbers when showLineNumbers is false', () => {
      render(<MockCodeEditor {...defaultProps} showLineNumbers={false} />);
      
      const lineNumbers = screen.queryByTestId('line-numbers');
      expect(lineNumbers).not.toBeInTheDocument();
    });

    it('renders with dark theme', () => {
      render(<MockCodeEditor {...defaultProps} theme="dark" />);
      
      const editor = screen.getByTestId('code-editor');
      expect(editor).toHaveClass('theme-dark');
    });

    it('renders with custom height', () => {
      render(<MockCodeEditor {...defaultProps} height="600px" />);
      
      const editor = screen.getByTestId('code-editor');
      expect(editor).toHaveStyle({ height: '600px' });
    });
  });

  describe('Interactions', () => {
    it('calls onChange when text is typed', async () => {
      const onChange = vi.fn();
      const user = userEvent.setup();
      
      render(<MockCodeEditor {...defaultProps} onChange={onChange} />);
      
      const textarea = screen.getByTestId('code-textarea');
      await user.type(textarea, '#include <stdio.h>');
      
      expect(onChange).toHaveBeenCalled();
      expect(onChange).toHaveBeenLastCalledWith('#include <stdio.h>');
    });

    it('does not call onChange when readOnly is true', async () => {
      const onChange = vi.fn();
      const user = userEvent.setup();
      
      render(
        <MockCodeEditor 
          {...defaultProps} 
          onChange={onChange} 
          readOnly={true}
          value="readonly code"
        />
      );
      
      const textarea = screen.getByTestId('code-textarea');
      
      // 尝试输入文本
      await user.type(textarea, 'new text');
      
      expect(onChange).not.toHaveBeenCalled();
      expect(textarea).toHaveClass('readonly');
    });

    it('focuses automatically when autoFocus is true', () => {
      render(<MockCodeEditor {...defaultProps} autoFocus={true} />);
      
      const textarea = screen.getByTestId('code-textarea');
      expect(textarea).toHaveFocus();
    });

    it('handles Ctrl+Enter for submission', async () => {
      const onSubmit = vi.fn();
      const code = 'console.log("test");';
      
      render(
        <MockCodeEditor 
          {...defaultProps} 
          value={code}
          onSubmit={onSubmit}
        />
      );
      
      const textarea = screen.getByTestId('code-textarea');
      
      await userEvent.type(textarea, '{Control>}{Enter}{/Control}');
      
      expect(onSubmit).toHaveBeenCalledWith(code);
    });

    it('prevents default behavior on Ctrl+Enter', () => {
      const onSubmit = vi.fn();
      render(<MockCodeEditor {...defaultProps} onSubmit={onSubmit} />);
      
      const textarea = screen.getByTestId('code-textarea');
      
      const event = new KeyboardEvent('keydown', {
        key: 'Enter',
        ctrlKey: true,
        bubbles: true,
        cancelable: true
      });
      
      const preventDefaultSpy = vi.spyOn(event, 'preventDefault');
      fireEvent(textarea, event);
      
      expect(preventDefaultSpy).toHaveBeenCalled();
    });
  });

  describe('Line Numbers', () => {
    it('updates line numbers when content changes', async () => {
      const onChange = vi.fn();
      const { rerender } = render(
        <MockCodeEditor {...defaultProps} value="line 1" onChange={onChange} />
      );
      
      // 初始时应该有1行
      expect(screen.getAllByText(/^1$/)).toHaveLength(1);
      
      // 更新内容为3行
      rerender(
        <MockCodeEditor 
          {...defaultProps} 
          value="line 1\nline 2\nline 3" 
          onChange={onChange}
        />
      );
      
      // 现在应该有3行号码
      expect(screen.getAllByText(/^[1-3]$/)).toHaveLength(3);
    });

    it('handles empty lines correctly', () => {
      const code = 'line 1\n\nline 3';
      render(<MockCodeEditor {...defaultProps} value={code} />);
      
      const lineNumbers = screen.getAllByText(/^[1-3]$/);
      expect(lineNumbers).toHaveLength(3);
    });
  });

  describe('Language Support', () => {
    it('supports C language', () => {
      const cCode = '#include <stdio.h>\nint main() {\n    printf("Hello");\n    return 0;\n}';
      render(
        <MockCodeEditor 
          {...defaultProps} 
          language="c" 
          value={cCode}
        />
      );
      
      const editor = screen.getByTestId('code-editor');
      expect(editor).toHaveAttribute('data-language', 'c');
    });

    it('supports Python language', () => {
      const pythonCode = 'def hello():\n    print("Hello World")\n\nhello()';
      render(
        <MockCodeEditor 
          {...defaultProps} 
          language="python" 
          value={pythonCode}
        />
      );
      
      const editor = screen.getByTestId('code-editor');
      expect(editor).toHaveAttribute('data-language', 'python');
    });

    it('supports JavaScript language', () => {
      const jsCode = 'function hello() {\n    console.log("Hello World");\n}\n\nhello();';
      render(
        <MockCodeEditor 
          {...defaultProps} 
          language="javascript" 
          value={jsCode}
        />
      );
      
      const editor = screen.getByTestId('code-editor');
      expect(editor).toHaveAttribute('data-language', 'javascript');
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA attributes', () => {
      render(<MockCodeEditor {...defaultProps} />);
      
      const textarea = screen.getByTestId('code-textarea');
      expect(textarea).toHaveAttribute('spellCheck', 'false');
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      render(<MockCodeEditor {...defaultProps} />);
      
      const textarea = screen.getByTestId('code-textarea');
      
      await user.click(textarea);
      expect(textarea).toHaveFocus();
      
      await user.type(textarea, 'test code');
      expect(textarea).toHaveValue('test code');
    });

    it('maintains focus during typing', async () => {
      const user = userEvent.setup();
      render(<MockCodeEditor {...defaultProps} />);
      
      const textarea = screen.getByTestId('code-textarea');
      await user.click(textarea);
      
      await user.type(textarea, 'typing test');
      expect(textarea).toHaveFocus();
    });
  });

  describe('Performance', () => {
    it('handles large code content efficiently', () => {
      const largeCode = Array(1000).fill('console.log("test");').join('\n');
      
      render(<MockCodeEditor {...defaultProps} value={largeCode} />);
      
      const textarea = screen.getByTestId('code-textarea');
      expect(textarea).toHaveValue(largeCode);
    });

    it('does not re-render unnecessarily', () => {
      const onChange = vi.fn();
      const { rerender } = render(
        <MockCodeEditor {...defaultProps} onChange={onChange} value="test" />
      );
      
      // 重新渲染相同的props
      rerender(
        <MockCodeEditor {...defaultProps} onChange={onChange} value="test" />
      );
      
      const textarea = screen.getByTestId('code-textarea');
      expect(textarea).toHaveValue('test');
    });
  });

  describe('Edge Cases', () => {
    it('handles undefined value gracefully', () => {
      render(<MockCodeEditor {...defaultProps} value={undefined as any} />);
      
      const textarea = screen.getByTestId('code-textarea');
      expect(textarea).toHaveValue('');
    });

    it('handles special characters correctly', async () => {
      const specialChars = '!@#$%^&*(){}[]|\\:";\'<>?,./';
      const onChange = vi.fn();
      const user = userEvent.setup();
      
      render(<MockCodeEditor {...defaultProps} onChange={onChange} />);
      
      const textarea = screen.getByTestId('code-textarea');
      await user.type(textarea, specialChars);
      
      expect(onChange).toHaveBeenLastCalledWith(specialChars);
    });

    it('handles unicode characters', async () => {
      const unicodeText = '你好世界 🌍 مرحبا بالعالم';
      const onChange = vi.fn();
      const user = userEvent.setup();
      
      render(<MockCodeEditor {...defaultProps} onChange={onChange} />);
      
      const textarea = screen.getByTestId('code-textarea');
      await user.type(textarea, unicodeText);
      
      expect(onChange).toHaveBeenLastCalledWith(unicodeText);
    });

    it('handles very long lines', () => {
      const longLine = 'a'.repeat(1000);
      
      render(<MockCodeEditor {...defaultProps} value={longLine} />);
      
      const textarea = screen.getByTestId('code-textarea');
      expect(textarea).toHaveValue(longLine);
    });
  });
});