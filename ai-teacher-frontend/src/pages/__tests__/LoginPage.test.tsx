/**
 * LoginPage页面测试
 * 测试登录页面功能和用户交互流程
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@/test-utils/test-utils';
import userEvent from '@testing-library/user-event';
import { server } from '@/test-utils/mocks/server';
import { rest } from 'msw';

// Mock LoginPage组件
interface LoginPageProps {}

const MockLoginPage: React.FC<LoginPageProps> = () => {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');
  const [showPassword, setShowPassword] = React.useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      
      // 模拟登录成功
      localStorage.setItem('access_token', data.accessToken);
      
      // 触发页面跳转
      window.location.href = '/dashboard';
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page" data-testid="login-page">
      <div className="login-container">
        <h1 data-testid="login-title">AI Teaching Assistant</h1>
        <p data-testid="login-subtitle">Sign in to your account</p>
        
        <form onSubmit={handleSubmit} data-testid="login-form">
          {error && (
            <div 
              className="error-message" 
              data-testid="error-message"
              role="alert"
              aria-live="polite"
            >
              {error}
            </div>
          )}
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              data-testid="email-input"
              required
              aria-describedby={error ? 'error-message' : undefined}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="password-input-container">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                data-testid="password-input"
                required
                aria-describedby={error ? 'error-message' : undefined}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                data-testid="toggle-password"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? '👁️' : '🔒'}
              </button>
            </div>
          </div>
          
          <div className="form-actions">
            <button
              type="submit"
              disabled={loading}
              data-testid="login-button"
              className={loading ? 'loading' : ''}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </div>
          
          <div className="form-footer">
            <a href="/forgot-password" data-testid="forgot-password-link">
              Forgot your password?
            </a>
            <div>
              Don't have an account?{' '}
              <a href="/register" data-testid="register-link">
                Sign up
              </a>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    
    // Mock window.location
    Object.defineProperty(window, 'location', {
      value: {
        href: '',
      },
      writable: true,
    });
  });

  describe('Rendering', () => {
    it('renders login page with all elements', () => {
      render(<MockLoginPage />);
      
      expect(screen.getByTestId('login-page')).toBeInTheDocument();
      expect(screen.getByTestId('login-title')).toHaveTextContent('AI Teaching Assistant');
      expect(screen.getByTestId('login-subtitle')).toHaveTextContent('Sign in to your account');
      expect(screen.getByTestId('login-form')).toBeInTheDocument();
    });

    it('renders form fields with correct labels', () => {
      render(<MockLoginPage />);
      
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByTestId('email-input')).toHaveAttribute('type', 'email');
      expect(screen.getByTestId('password-input')).toHaveAttribute('type', 'password');
    });

    it('renders form elements with correct attributes', () => {
      render(<MockLoginPage />);
      
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');
      
      expect(emailInput).toHaveAttribute('required');
      expect(passwordInput).toHaveAttribute('required');
      expect(emailInput).toHaveAttribute('placeholder', 'Enter your email');
      expect(passwordInput).toHaveAttribute('placeholder', 'Enter your password');
      expect(submitButton).toHaveAttribute('type', 'submit');
    });

    it('renders navigation links', () => {
      render(<MockLoginPage />);
      
      const forgotPasswordLink = screen.getByTestId('forgot-password-link');
      const registerLink = screen.getByTestId('register-link');
      
      expect(forgotPasswordLink).toHaveAttribute('href', '/forgot-password');
      expect(registerLink).toHaveAttribute('href', '/register');
    });
  });

  describe('Form Interactions', () => {
    it('updates email input value when typed', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const emailInput = screen.getByTestId('email-input');
      await user.type(emailInput, 'test@university.edu');
      
      expect(emailInput).toHaveValue('test@university.edu');
    });

    it('updates password input value when typed', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const passwordInput = screen.getByTestId('password-input');
      await user.type(passwordInput, 'password123');
      
      expect(passwordInput).toHaveValue('password123');
    });

    it('toggles password visibility', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const passwordInput = screen.getByTestId('password-input');
      const toggleButton = screen.getByTestId('toggle-password');
      
      // 初始状态应该是密码类型
      expect(passwordInput).toHaveAttribute('type', 'password');
      expect(toggleButton).toHaveAttribute('aria-label', 'Show password');
      
      // 点击切换按钮
      await user.click(toggleButton);
      
      // 现在应该是文本类型
      expect(passwordInput).toHaveAttribute('type', 'text');
      expect(toggleButton).toHaveAttribute('aria-label', 'Hide password');
      
      // 再次点击切换回去
      await user.click(toggleButton);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    it('shows validation error for empty fields', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const submitButton = screen.getByTestId('login-button');
      await user.click(submitButton);
      
      await waitFor(() => {
        const errorMessage = screen.getByTestId('error-message');
        expect(errorMessage).toBeInTheDocument();
        expect(errorMessage).toHaveTextContent('Please fill in all fields');
      });
    });

    it('shows validation error for missing email', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');
      
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);
      
      await waitFor(() => {
        const errorMessage = screen.getByTestId('error-message');
        expect(errorMessage).toHaveTextContent('Please fill in all fields');
      });
    });

    it('shows validation error for missing password', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const emailInput = screen.getByTestId('email-input');
      const submitButton = screen.getByTestId('login-button');
      
      await user.type(emailInput, 'test@university.edu');
      await user.click(submitButton);
      
      await waitFor(() => {
        const errorMessage = screen.getByTestId('error-message');
        expect(errorMessage).toHaveTextContent('Please fill in all fields');
      });
    });
  });

  describe('Login Success', () => {
    it('submits form with valid credentials and redirects', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');
      
      await user.type(emailInput, 'test@university.edu');
      await user.type(passwordInput, 'password123');
      
      await user.click(submitButton);
      
      // 检查加载状态
      expect(submitButton).toBeDisabled();
      expect(submitButton).toHaveTextContent('Signing in...');
      
      // 等待请求完成
      await waitFor(() => {
        expect(localStorage.getItem('access_token')).toBe('mock-access-token');
        expect(window.location.href).toBe('/dashboard');
      });
    });

    it('shows loading state during submission', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');
      
      await user.type(emailInput, 'test@university.edu');
      await user.type(passwordInput, 'password123');
      
      await user.click(submitButton);
      
      // 立即检查加载状态
      expect(submitButton).toBeDisabled();
      expect(submitButton).toHaveTextContent('Signing in...');
      expect(submitButton).toHaveClass('loading');
    });

    it('clears error message on successful submission', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const submitButton = screen.getByTestId('login-button');
      
      // 先触发错误
      await user.click(submitButton);
      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toBeInTheDocument();
      });
      
      // 然后填写正确信息提交
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      
      await user.type(emailInput, 'test@university.edu');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);
      
      // 错误消息应该消失
      await waitFor(() => {
        expect(screen.queryByTestId('error-message')).not.toBeInTheDocument();
      });
    });
  });

  describe('Login Failure', () => {
    it('shows error message for invalid credentials', async () => {
      // Mock 失败的登录响应
      server.use(
        rest.post('/api/v1/auth/login', (req, res, ctx) => {
          return res(
            ctx.status(401),
            ctx.json({ detail: 'Invalid email or password' })
          );
        })
      );

      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');
      
      await user.type(emailInput, 'wrong@university.edu');
      await user.type(passwordInput, 'wrongpassword');
      await user.click(submitButton);
      
      await waitFor(() => {
        const errorMessage = screen.getByTestId('error-message');
        expect(errorMessage).toHaveTextContent('Invalid email or password');
      });
      
      // 表单应该重新启用
      expect(submitButton).not.toBeDisabled();
      expect(submitButton).toHaveTextContent('Sign In');
    });

    it('shows generic error message for network errors', async () => {
      // Mock 网络错误
      server.use(
        rest.post('/api/v1/auth/login', (req, res, ctx) => {
          return res(ctx.status(500));
        })
      );

      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');
      
      await user.type(emailInput, 'test@university.edu');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);
      
      await waitFor(() => {
        const errorMessage = screen.getByTestId('error-message');
        expect(errorMessage).toHaveTextContent('Login failed');
      });
    });

    it('re-enables form after failed submission', async () => {
      server.use(
        rest.post('/api/v1/auth/login', (req, res, ctx) => {
          return res(ctx.status(401), ctx.json({ detail: 'Login failed' }));
        })
      );

      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const submitButton = screen.getByTestId('login-button');
      
      await user.type(emailInput, 'test@university.edu');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);
      
      // 等待错误出现，表单应该重新启用
      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toBeInTheDocument();
        expect(submitButton).not.toBeDisabled();
        expect(submitButton).toHaveTextContent('Sign In');
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA attributes for error handling', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const submitButton = screen.getByTestId('login-button');
      await user.click(submitButton);
      
      await waitFor(() => {
        const errorMessage = screen.getByTestId('error-message');
        expect(errorMessage).toHaveAttribute('role', 'alert');
        expect(errorMessage).toHaveAttribute('aria-live', 'polite');
      });
    });

    it('associates error message with form fields', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const submitButton = screen.getByTestId('login-button');
      await user.click(submitButton);
      
      await waitFor(() => {
        const emailInput = screen.getByTestId('email-input');
        const passwordInput = screen.getByTestId('password-input');
        
        expect(emailInput).toHaveAttribute('aria-describedby', 'error-message');
        expect(passwordInput).toHaveAttribute('aria-describedby', 'error-message');
      });
    });

    it('has proper labels and aria-labels', () => {
      render(<MockLoginPage />);
      
      const toggleButton = screen.getByTestId('toggle-password');
      expect(toggleButton).toHaveAttribute('aria-label', 'Show password');
      
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      
      expect(screen.getByLabelText(/email/i)).toBe(emailInput);
      expect(screen.getByLabelText(/password/i)).toBe(passwordInput);
    });
  });

  describe('Keyboard Navigation', () => {
    it('supports form submission with Enter key', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      
      await user.type(emailInput, 'test@university.edu');
      await user.type(passwordInput, 'password123');
      
      // 在密码字段按Enter
      fireEvent.keyDown(passwordInput, { key: 'Enter', code: 'Enter' });
      
      await waitFor(() => {
        expect(localStorage.getItem('access_token')).toBe('mock-access-token');
      });
    });

    it('supports tab navigation between fields', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      // Tab到邮箱字段
      await user.tab();
      expect(screen.getByTestId('email-input')).toHaveFocus();
      
      // Tab到密码字段
      await user.tab();
      expect(screen.getByTestId('password-input')).toHaveFocus();
      
      // Tab到显示/隐藏密码按钮
      await user.tab();
      expect(screen.getByTestId('toggle-password')).toHaveFocus();
      
      // Tab到提交按钮
      await user.tab();
      expect(screen.getByTestId('login-button')).toHaveFocus();
    });
  });

  describe('Form Validation', () => {
    it('validates email format', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const emailInput = screen.getByTestId('email-input');
      
      await user.type(emailInput, 'invalid-email');
      
      // HTML5验证应该在提交时触发
      const form = screen.getByTestId('login-form');
      fireEvent.submit(form);
      
      expect(emailInput).toBeInvalid();
    });

    it('accepts valid email format', async () => {
      const user = userEvent.setup();
      render(<MockLoginPage />);
      
      const emailInput = screen.getByTestId('email-input');
      
      await user.type(emailInput, 'valid@university.edu');
      
      expect(emailInput).toBeValid();
    });
  });
});