/**
 * Frontend Performance Utilities (Sprint 5)
 * 前端性能优化工具
 *
 * Features:
 * - 组件懒加载
 * - 图片懒加载
 * - 虚拟滚动支持
 * - 性能监控
 */

import { lazy, ComponentType, LazyExoticComponent } from 'react';

// ============= 懒加载工具 =============

/**
 * 带重试的懒加载组件
 */
export function lazyWithRetry<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  retries: number = 3,
  delay: number = 1000
): LazyExoticComponent<T> {
  return lazy(async () => {
    let lastError: Error | undefined;

    for (let i = 0; i < retries; i++) {
      try {
        return await importFn();
      } catch (error) {
        lastError = error as Error;
        if (i < retries - 1) {
          await new Promise((resolve) => setTimeout(resolve, delay * (i + 1)));
        }
      }
    }

    throw lastError;
  });
}

/**
 * 预加载组件
 */
export function preloadComponent<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>
): void {
  importFn().catch(() => {
    // 忽略预加载错误
  });
}

// ============= 懒加载的重型组件 =============

export const LazyMonacoEditor = lazyWithRetry(
  () => import('../components/editor/MonacoCodeEditor')
);

export const LazyCharts = lazyWithRetry(() => import('../components/charts'));

export const LazyBatchGrading = lazyWithRetry(
  () => import('../components/teacher/BatchGradingPanel')
);

export const LazyFeedbackManager = lazyWithRetry(
  () => import('../components/teacher/FeedbackTemplateManager')
);

// ============= 性能监控 =============

interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private maxMetrics: number = 1000;

  /**
   * 记录性能指标
   */
  record(name: string, value: number): void {
    this.metrics.push({
      name,
      value,
      timestamp: Date.now(),
    });

    // 限制存储的指标数量
    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics);
    }
  }

  /**
   * 测量函数执行时间
   */
  async measure<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const start = performance.now();
    try {
      return await fn();
    } finally {
      const duration = performance.now() - start;
      this.record(name, duration);
    }
  }

  /**
   * 测量同步函数执行时间
   */
  measureSync<T>(name: string, fn: () => T): T {
    const start = performance.now();
    try {
      return fn();
    } finally {
      const duration = performance.now() - start;
      this.record(name, duration);
    }
  }

  /**
   * 获取指标统计
   */
  getStats(name?: string): {
    count: number;
    avg: number;
    min: number;
    max: number;
    p95: number;
  } | null {
    const filtered = name
      ? this.metrics.filter((m) => m.name === name)
      : this.metrics;

    if (filtered.length === 0) {
      return null;
    }

    const values = filtered.map((m) => m.value).sort((a, b) => a - b);
    const sum = values.reduce((a, b) => a + b, 0);

    return {
      count: values.length,
      avg: sum / values.length,
      min: values[0],
      max: values[values.length - 1],
      p95: values[Math.floor(values.length * 0.95)],
    };
  }

  /**
   * 获取所有指标
   */
  getAllMetrics(): PerformanceMetric[] {
    return [...this.metrics];
  }

  /**
   * 清除指标
   */
  clear(): void {
    this.metrics = [];
  }

  /**
   * 记录Web Vitals
   */
  recordWebVitals(): void {
    if (typeof window === 'undefined') return;

    // First Contentful Paint
    const paintEntries = performance.getEntriesByType('paint');
    const fcp = paintEntries.find((entry) => entry.name === 'first-contentful-paint');
    if (fcp) {
      this.record('fcp', fcp.startTime);
    }

    // Largest Contentful Paint
    if ('PerformanceObserver' in window) {
      try {
        const lcpObserver = new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          const lastEntry = entries[entries.length - 1];
          this.record('lcp', lastEntry.startTime);
        });
        lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });

        // First Input Delay
        const fidObserver = new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          entries.forEach((entry) => {
            const fidEntry = entry as PerformanceEventTiming;
            this.record('fid', fidEntry.processingStart - fidEntry.startTime);
          });
        });
        fidObserver.observe({ type: 'first-input', buffered: true });

        // Cumulative Layout Shift
        const clsObserver = new PerformanceObserver((entryList) => {
          let cls = 0;
          entryList.getEntries().forEach((entry) => {
            const layoutShift = entry as LayoutShift;
            if (!layoutShift.hadRecentInput) {
              cls += layoutShift.value;
            }
          });
          this.record('cls', cls);
        });
        clsObserver.observe({ type: 'layout-shift', buffered: true });
      } catch (e) {
        console.warn('PerformanceObserver not fully supported');
      }
    }
  }
}

// 全局性能监控实例
export const performanceMonitor = new PerformanceMonitor();

// ============= 虚拟滚动配置 =============

export interface VirtualScrollConfig {
  itemHeight: number;
  overscan: number;
  containerHeight: number;
}

/**
 * 计算虚拟滚动可见范围
 */
export function calculateVisibleRange(
  scrollTop: number,
  config: VirtualScrollConfig,
  totalItems: number
): { start: number; end: number; offsetY: number } {
  const { itemHeight, overscan, containerHeight } = config;

  const visibleCount = Math.ceil(containerHeight / itemHeight);
  const start = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const end = Math.min(totalItems, start + visibleCount + overscan * 2);
  const offsetY = start * itemHeight;

  return { start, end, offsetY };
}

// ============= 图片优化 =============

/**
 * 生成响应式图片srcset
 */
export function generateSrcSet(
  baseUrl: string,
  sizes: number[] = [320, 640, 1024, 1920]
): string {
  return sizes
    .map((size) => {
      const url = baseUrl.replace(/(\.[^.]+)$/, `_${size}$1`);
      return `${url} ${size}w`;
    })
    .join(', ');
}

/**
 * 检测WebP支持
 */
export async function supportsWebP(): Promise<boolean> {
  if (typeof window === 'undefined') return false;

  const elem = document.createElement('canvas');
  if (elem.getContext && elem.getContext('2d')) {
    return elem.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  }
  return false;
}

// ============= 防抖和节流 =============

/**
 * 防抖函数
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

/**
 * 节流函数
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle = false;

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

// ============= 内存管理 =============

/**
 * 检测内存使用情况
 */
export function getMemoryUsage(): {
  usedJSHeapSize?: number;
  totalJSHeapSize?: number;
  jsHeapSizeLimit?: number;
} | null {
  if (typeof window === 'undefined') return null;

  const memory = (performance as any).memory;
  if (!memory) return null;

  return {
    usedJSHeapSize: memory.usedJSHeapSize,
    totalJSHeapSize: memory.totalJSHeapSize,
    jsHeapSizeLimit: memory.jsHeapSizeLimit,
  };
}

// ============= 类型定义 =============

interface PerformanceEventTiming extends PerformanceEntry {
  processingStart: number;
}

interface LayoutShift extends PerformanceEntry {
  value: number;
  hadRecentInput: boolean;
}

export default {
  lazyWithRetry,
  preloadComponent,
  performanceMonitor,
  calculateVisibleRange,
  debounce,
  throttle,
  getMemoryUsage,
};
