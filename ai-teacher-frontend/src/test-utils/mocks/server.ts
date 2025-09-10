/**
 * Mock Service Worker (MSW) 服务器设置
 * 用于拦截和模拟API请求
 */

import { setupServer } from 'msw/node';
import { handlers } from './handlers';

// 设置mock服务器
export const server = setupServer(...handlers);

// 导出用于测试的工具函数
export { server };
export * from './handlers';