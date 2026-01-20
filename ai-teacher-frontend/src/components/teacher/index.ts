/**
 * Teacher Components Index
 * 教师端组件导出
 */

// Batch Grading Panel - 批量批改面板
export {
  BatchGradingPanel,
  type StudentSubmission,
  type SubmissionStatus,
} from './BatchGradingPanel';
export { default as BatchGradingPanelDefault } from './BatchGradingPanel';

// Submission Detail Modal - 作业详情模态框
export {
  SubmissionDetailModal,
  type FeedbackTemplate as ModalFeedbackTemplate,
} from './SubmissionDetailModal';
export { default as SubmissionDetailModalDefault } from './SubmissionDetailModal';

// Feedback Template Manager - 反馈模板管理
export {
  FeedbackTemplateManager,
  type FeedbackTemplate,
  type TemplateCategory,
  DEFAULT_TEMPLATES,
} from './FeedbackTemplateManager';
export { default as FeedbackTemplateManagerDefault } from './FeedbackTemplateManager';
