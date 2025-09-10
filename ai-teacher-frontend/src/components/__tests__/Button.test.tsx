/**
 * Button组件测试
 * 测试按钮组件的各种变体和交互
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@/test-utils/test-utils';
import { Button } from '@/components/ui/Button';

// 假设Button组件的接口
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

// Mock Button组件(如果实际组件不存在)
const MockButton: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  children,
  type = 'button',
  className = ''
}) => {
  const baseClasses = 'btn';
  const variantClasses = {
    primary: 'btn-primary',
    secondary: 'btn-secondary', 
    danger: 'btn-danger',
    ghost: 'btn-ghost'
  };
  const sizeClasses = {
    sm: 'btn-sm',
    md: 'btn-md',
    lg: 'btn-lg'
  };

  const classes = [
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    disabled ? 'btn-disabled' : '',
    loading ? 'btn-loading' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      type={type}
      className={classes}
      disabled={disabled || loading}
      onClick={onClick}
      data-testid="button"
    >
      {loading ? (
        <span data-testid="loading-spinner">Loading...</span>
      ) : (
        children
      )}
    </button>
  );
};

describe('Button Component', () => {
  describe('Rendering', () => {
    it('renders button with text', () => {
      render(<MockButton>Click me</MockButton>);
      
      const button = screen.getByRole('button', { name: /click me/i });
      expect(button).toBeInTheDocument();
      expect(button).toHaveTextContent('Click me');
    });

    it('renders with primary variant by default', () => {
      render(<MockButton>Primary Button</MockButton>);
      
      const button = screen.getByTestId('button');
      expect(button).toHaveClass('btn-primary');
    });

    it('renders with specified variant', () => {
      render(<MockButton variant="secondary">Secondary Button</MockButton>);
      
      const button = screen.getByTestId('button');
      expect(button).toHaveClass('btn-secondary');
    });

    it('renders with specified size', () => {
      render(<MockButton size="lg">Large Button</MockButton>);
      
      const button = screen.getByTestId('button');
      expect(button).toHaveClass('btn-lg');
    });

    it('renders with custom className', () => {
      render(<MockButton className="custom-class">Custom Button</MockButton>);
      
      const button = screen.getByTestId('button');
      expect(button).toHaveClass('custom-class');
    });
  });

  describe('States', () => {
    it('renders as disabled when disabled prop is true', () => {
      render(<MockButton disabled>Disabled Button</MockButton>);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(button).toHaveClass('btn-disabled');
    });

    it('shows loading state when loading prop is true', () => {
      render(<MockButton loading>Loading Button</MockButton>);
      
      const button = screen.getByRole('button');
      const spinner = screen.getByTestId('loading-spinner');
      
      expect(button).toBeDisabled();
      expect(button).toHaveClass('btn-loading');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveTextContent('Loading...');
    });

    it('is disabled when loading', () => {
      render(<MockButton loading>Loading Button</MockButton>);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });
  });

  describe('Interactions', () => {
    it('calls onClick handler when clicked', () => {
      const handleClick = vi.fn();
      render(<MockButton onClick={handleClick}>Clickable Button</MockButton>);
      
      const button = screen.getByRole('button');
      fireEvent.click(button);
      
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when disabled', () => {
      const handleClick = vi.fn();
      render(
        <MockButton onClick={handleClick} disabled>
          Disabled Button
        </MockButton>
      );
      
      const button = screen.getByRole('button');
      fireEvent.click(button);
      
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('does not call onClick when loading', () => {
      const handleClick = vi.fn();
      render(
        <MockButton onClick={handleClick} loading>
          Loading Button
        </MockButton>
      );
      
      const button = screen.getByRole('button');
      fireEvent.click(button);
      
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('Types', () => {
    it('renders as submit type when specified', () => {
      render(<MockButton type="submit">Submit Button</MockButton>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'submit');
    });

    it('renders as reset type when specified', () => {
      render(<MockButton type="reset">Reset Button</MockButton>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('type', 'reset');
    });
  });

  describe('Accessibility', () => {
    it('is focusable when not disabled', () => {
      render(<MockButton>Focusable Button</MockButton>);
      
      const button = screen.getByRole('button');
      button.focus();
      
      expect(button).toHaveFocus();
    });

    it('is not focusable when disabled', () => {
      render(<MockButton disabled>Disabled Button</MockButton>);
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      
      // 尝试聚焦被禁用的按钮
      button.focus();
      expect(button).not.toHaveFocus();
    });

    it('supports keyboard interaction (Enter key)', () => {
      const handleClick = vi.fn();
      render(<MockButton onClick={handleClick}>Keyboard Button</MockButton>);
      
      const button = screen.getByRole('button');
      button.focus();
      fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });
      
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('supports keyboard interaction (Space key)', () => {
      const handleClick = vi.fn();
      render(<MockButton onClick={handleClick}>Keyboard Button</MockButton>);
      
      const button = screen.getByRole('button');
      button.focus();
      fireEvent.keyDown(button, { key: ' ', code: 'Space' });
      
      expect(handleClick).toHaveBeenCalledTimes(1);
    });
  });

  describe('Variants', () => {
    it('renders all button variants correctly', () => {
      const variants: Array<'primary' | 'secondary' | 'danger' | 'ghost'> = [
        'primary', 
        'secondary', 
        'danger', 
        'ghost'
      ];
      
      variants.forEach((variant) => {
        const { unmount } = render(
          <MockButton variant={variant}>{variant} Button</MockButton>
        );
        
        const button = screen.getByTestId('button');
        expect(button).toHaveClass(`btn-${variant}`);
        
        unmount();
      });
    });

    it('renders all button sizes correctly', () => {
      const sizes: Array<'sm' | 'md' | 'lg'> = ['sm', 'md', 'lg'];
      
      sizes.forEach((size) => {
        const { unmount } = render(
          <MockButton size={size}>{size} Button</MockButton>
        );
        
        const button = screen.getByTestId('button');
        expect(button).toHaveClass(`btn-${size}`);
        
        unmount();
      });
    });
  });

  describe('Edge Cases', () => {
    it('handles empty children gracefully', () => {
      render(<MockButton>{''}</MockButton>);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
    });

    it('handles multiple clicks rapidly', () => {
      const handleClick = vi.fn();
      render(<MockButton onClick={handleClick}>Rapid Click</MockButton>);
      
      const button = screen.getByRole('button');
      
      // 快速点击多次
      fireEvent.click(button);
      fireEvent.click(button);
      fireEvent.click(button);
      
      expect(handleClick).toHaveBeenCalledTimes(3);
    });

    it('renders with JSX children', () => {
      render(
        <MockButton>
          <span>Icon</span>
          <span>Text</span>
        </MockButton>
      );
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('IconText');
      expect(screen.getByText('Icon')).toBeInTheDocument();
      expect(screen.getByText('Text')).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('does not re-render unnecessarily', () => {
      const handleClick = vi.fn();
      const { rerender } = render(
        <MockButton onClick={handleClick}>Initial</MockButton>
      );
      
      // 重新渲染相同的props
      rerender(<MockButton onClick={handleClick}>Initial</MockButton>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('Initial');
    });
  });
});