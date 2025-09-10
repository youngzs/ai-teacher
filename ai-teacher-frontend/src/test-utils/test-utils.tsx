/**
 * 测试工具函数
 * 提供自定义渲染函数和测试辅助工具
 */

import React, { ReactElement, ReactNode } from 'react';
import { render, RenderOptions, RenderResult } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Zustand store的mock
import { authStore } from '@/store/auth';
import { uiStore } from '@/store/ui';

// 创建测试用的QueryClient
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      cacheTime: 0,
    },
    mutations: {
      retry: false,
    },
  },
});

// 测试Providers组件
interface AllTheProvidersProps {
  children: ReactNode;
  queryClient?: QueryClient;
  initialRoute?: string;
}

const AllTheProviders: React.FC<AllTheProvidersProps> = ({ 
  children, 
  queryClient = createTestQueryClient(),
  initialRoute = '/'
}) => {
  // 设置初始路由
  if (initialRoute !== '/') {
    window.history.pushState({}, 'Test page', initialRoute);
  }

  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </BrowserRouter>
  );
};

// 自定义渲染函数
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient;
  initialRoute?: string;
  wrapper?: React.ComponentType<any>;
}

const customRender = (
  ui: ReactElement,
  options: CustomRenderOptions = {}
): RenderResult => {
  const { queryClient, initialRoute, wrapper, ...renderOptions } = options;

  const Wrapper = wrapper || AllTheProviders;
  
  return render(ui, {
    wrapper: (props) => (
      <Wrapper {...props} queryClient={queryClient} initialRoute={initialRoute} />
    ),
    ...renderOptions,
  });
};

// 认证相关的渲染函数
export const renderWithAuth = (
  ui: ReactElement,
  options: CustomRenderOptions & { user?: any } = {}
) => {
  const { user = null, ...restOptions } = options;
  
  // 设置认证状态
  if (user) {
    authStore.getState().setUser(user);
    authStore.getState().setAuthenticated(true);
  } else {
    authStore.getState().logout();
  }
  
  return customRender(ui, restOptions);
};

// 用户事件工具
export const createUser = () => userEvent.setup();

// Mock API响应工具
export const createMockApiResponse = <T>(data: T, delay = 0) => {
  return new Promise<T>((resolve) => {
    setTimeout(() => resolve(data), delay);
  });
};

export const createMockApiError = (message: string, status = 500, delay = 0) => {
  return new Promise<never>((_, reject) => {
    setTimeout(() => {
      const error = new Error(message);
      (error as any).status = status;
      reject(error);
    }, delay);
  });
};

// 表单测试辅助函数
export const fillForm = async (fields: Record<string, string>) => {
  const user = createUser();
  
  for (const [fieldName, value] of Object.entries(fields)) {
    const field = screen.getByLabelText(new RegExp(fieldName, 'i')) ||
                   screen.getByPlaceholderText(new RegExp(fieldName, 'i')) ||
                   screen.getByDisplayValue('');
    
    if (field) {
      await user.clear(field);
      await user.type(field, value);
    }
  }
};

// 等待异步操作完成
export const waitForLoadingToFinish = async () => {
  await waitForElementToBeRemoved(
    () => screen.queryByLabelText(/loading/i) || screen.queryByText(/loading/i)
  );
};

// Store状态重置
export const resetStores = () => {
  authStore.getState().logout();
  uiStore.getState().reset?.();
};

// 模拟路由导航
export const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// 模拟window.alert, confirm, prompt
export const mockWindowMethods = () => {
  const originalAlert = window.alert;
  const originalConfirm = window.confirm;
  const originalPrompt = window.prompt;

  window.alert = vi.fn();
  window.confirm = vi.fn(() => true);
  window.prompt = vi.fn(() => 'mocked input');

  return {
    restoreWindowMethods: () => {
      window.alert = originalAlert;
      window.confirm = originalConfirm;
      window.prompt = originalPrompt;
    },
    mockAlert: window.alert as vi.Mock,
    mockConfirm: window.confirm as vi.Mock,
    mockPrompt: window.prompt as vi.Mock,
  };
};

// 测试快照辅助
export const createSnapshot = (component: ReactElement, options?: CustomRenderOptions) => {
  const { container } = customRender(component, options);
  expect(container.firstChild).toMatchSnapshot();
};

// 辅助断言函数
export const expectToBeInDocument = (element: HTMLElement | null) => {
  expect(element).toBeInTheDocument();
};

export const expectNotToBeInDocument = (element: HTMLElement | null) => {
  expect(element).not.toBeInTheDocument();
};

export const expectToHaveClass = (element: HTMLElement, className: string) => {
  expect(element).toHaveClass(className);
};

export const expectToBeDisabled = (element: HTMLElement) => {
  expect(element).toBeDisabled();
};

export const expectToBeEnabled = (element: HTMLElement) => {
  expect(element).toBeEnabled();
};

// 组件交互辅助
export const clickElement = async (element: HTMLElement) => {
  const user = createUser();
  await user.click(element);
};

export const typeInElement = async (element: HTMLElement, text: string) => {
  const user = createUser();
  await user.type(element, text);
};

export const selectOption = async (element: HTMLElement, option: string) => {
  const user = createUser();
  await user.selectOptions(element, option);
};

// 导出所有testing-library的utilities以及自定义的render函数
export * from '@testing-library/react';
export { customRender as render };

// 导出常用的testing library functions
export { screen, waitFor, waitForElementToBeRemoved } from '@testing-library/react';