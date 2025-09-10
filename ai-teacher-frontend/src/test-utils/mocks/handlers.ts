/**
 * MSW请求处理器
 * 定义各种API端点的mock响应
 */

import { rest } from 'msw';
import { TEST_DATA } from '../setup';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const handlers = [
  // 认证相关API
  rest.post(`${API_BASE_URL}/auth/register`, (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: '1',
        email: 'test@university.edu',
        fullName: 'Test User',
        role: 'student',
        university: 'Test University',
        department: 'Computer Science'
      })
    );
  }),

  rest.post(`${API_BASE_URL}/auth/login`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        accessToken: 'mock-access-token',
        tokenType: 'bearer',
        user: TEST_DATA.STUDENT
      })
    );
  }),

  rest.get(`${API_BASE_URL}/auth/me`, (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(ctx.status(401), ctx.json({ detail: 'Unauthorized' }));
    }

    return res(ctx.status(200), ctx.json(TEST_DATA.STUDENT));
  }),

  rest.post(`${API_BASE_URL}/auth/logout`, (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({ message: 'Logged out successfully' }));
  }),

  // 用户管理API
  rest.get(`${API_BASE_URL}/users/:id`, (req, res, ctx) => {
    const { id } = req.params;
    
    if (id === '1') {
      return res(ctx.status(200), ctx.json(TEST_DATA.TEACHER));
    } else if (id === '2') {
      return res(ctx.status(200), ctx.json(TEST_DATA.STUDENT));
    }
    
    return res(ctx.status(404), ctx.json({ detail: 'User not found' }));
  }),

  rest.put(`${API_BASE_URL}/users/:id`, (req, res, ctx) => {
    const { id } = req.params;
    const updatedData = req.body as any;
    
    return res(
      ctx.status(200),
      ctx.json({
        ...TEST_DATA.STUDENT,
        ...updatedData,
        id
      })
    );
  }),

  rest.get(`${API_BASE_URL}/users/`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        items: [TEST_DATA.TEACHER, TEST_DATA.STUDENT],
        total: 2,
        page: 1,
        size: 10
      })
    );
  }),

  // 代码提交API
  rest.post(`${API_BASE_URL}/submissions/`, (req, res, ctx) => {
    const submissionData = req.body as any;
    
    return res(
      ctx.status(201),
      ctx.json({
        id: 'submission-1',
        code: submissionData.code,
        language: submissionData.language,
        assignmentId: submissionData.assignmentId,
        status: 'pending',
        createdAt: new Date().toISOString(),
        userId: TEST_DATA.STUDENT.id
      })
    );
  }),

  rest.get(`${API_BASE_URL}/submissions/:id`, (req, res, ctx) => {
    const { id } = req.params;
    
    return res(
      ctx.status(200),
      ctx.json({
        id,
        code: TEST_DATA.C_CODE,
        language: 'c',
        assignmentId: 'basic-loops',
        status: 'completed',
        createdAt: '2024-01-01T10:00:00Z',
        userId: TEST_DATA.STUDENT.id,
        analysis: TEST_DATA.AI_FEEDBACK.analysis,
        feedback: TEST_DATA.AI_FEEDBACK.feedback
      })
    );
  }),

  rest.get(`${API_BASE_URL}/submissions/`, (req, res, ctx) => {
    const submissions = [
      {
        id: 'submission-1',
        code: TEST_DATA.C_CODE,
        language: 'c',
        assignmentId: 'basic-loops',
        status: 'completed',
        createdAt: '2024-01-01T10:00:00Z'
      },
      {
        id: 'submission-2',
        code: TEST_DATA.PYTHON_CODE,
        language: 'python',
        assignmentId: 'hello-world',
        status: 'pending',
        createdAt: '2024-01-01T11:00:00Z'
      }
    ];

    return res(
      ctx.status(200),
      ctx.json({
        items: submissions,
        total: 2,
        page: 1,
        size: 10
      })
    );
  }),

  rest.post(`${API_BASE_URL}/submissions/:id/analyze`, (req, res, ctx) => {
    const { id } = req.params;
    
    // 模拟AI分析延迟
    return res(
      ctx.delay(1000),
      ctx.status(200),
      ctx.json({
        id,
        status: 'completed',
        analysis: TEST_DATA.AI_FEEDBACK.analysis,
        feedback: TEST_DATA.AI_FEEDBACK.feedback
      })
    );
  }),

  // AI分析API
  rest.post(`${API_BASE_URL}/analysis/analyze`, (req, res, ctx) => {
    const { code, language } = req.body as any;
    
    if (!code || !language) {
      return res(
        ctx.status(422),
        ctx.json({ detail: 'Code and language are required' })
      );
    }

    return res(
      ctx.delay(800), // 模拟AI处理时间
      ctx.status(200),
      ctx.json({
        analysis: {
          ...TEST_DATA.AI_FEEDBACK.analysis,
          code,
          language
        },
        feedback: TEST_DATA.AI_FEEDBACK.feedback,
        pedagogicalAdvice: {
          teachingStrategy: 'positive_reinforcement',
          focusAreas: ['code_structure'],
          estimatedMastery: 0.8
        }
      })
    );
  }),

  rest.post(`${API_BASE_URL}/analysis/feedback`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        feedback: {
          ...TEST_DATA.AI_FEEDBACK.feedback,
          personalization: {
            learningStyle: 'visual',
            confidenceBoost: 'Great progress! Keep it up!',
            challengeLevel: 'ready_for_next_level'
          }
        }
      })
    );
  }),

  // 仪表板API
  rest.get(`${API_BASE_URL}/dashboard/teacher`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        totalStudents: 25,
        totalAssignments: 8,
        pendingReviews: 5,
        avgClassScore: 85.2,
        recentSubmissions: [
          {
            id: 'sub1',
            studentName: 'Alice Johnson',
            assignmentTitle: 'Basic Loops',
            submittedAt: '2024-01-01T10:00:00Z',
            score: 92
          }
        ],
        classPerformance: {
          excellent: 8,
          good: 12,
          needsImprovement: 5
        }
      })
    );
  }),

  rest.get(`${API_BASE_URL}/dashboard/student`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        totalSubmissions: 12,
        averageScore: 87.5,
        completedAssignments: 8,
        pendingAssignments: 3,
        recentFeedback: [
          {
            assignmentTitle: 'Array Processing',
            score: 88,
            feedbackSummary: 'Good implementation with room for optimization',
            receivedAt: '2024-01-01T15:00:00Z'
          }
        ],
        learningProgress: {
          currentLevel: 'intermediate',
          mastery: 0.75,
          strongAreas: ['syntax', 'logic'],
          improvementAreas: ['optimization', 'error_handling']
        }
      })
    );
  }),

  // 错误处理示例
  rest.get(`${API_BASE_URL}/error-test`, (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({ detail: 'Internal server error' }));
  }),

  rest.get(`${API_BASE_URL}/timeout-test`, (req, res, ctx) => {
    return res(ctx.delay(10000), ctx.status(200), ctx.json({ message: 'This will timeout' }));
  }),

  // 权限测试
  rest.get(`${API_BASE_URL}/admin-only`, (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization');
    
    if (!authHeader) {
      return res(ctx.status(401), ctx.json({ detail: 'Unauthorized' }));
    }

    // 模拟权限检查
    return res(ctx.status(403), ctx.json({ detail: 'Insufficient permissions' }));
  })
];

// 导出特定场景的handlers
export const authHandlers = handlers.filter(handler => 
  handler.info.path.includes('/auth/')
);

export const submissionHandlers = handlers.filter(handler =>
  handler.info.path.includes('/submissions/')
);

export const userHandlers = handlers.filter(handler =>
  handler.info.path.includes('/users/')
);

export const analysisHandlers = handlers.filter(handler =>
  handler.info.path.includes('/analysis/')
);

// 错误场景handlers
export const errorHandlers = [
  rest.post(`${API_BASE_URL}/auth/login`, (req, res, ctx) => {
    return res(ctx.status(401), ctx.json({ detail: 'Invalid credentials' }));
  }),
  
  rest.post(`${API_BASE_URL}/submissions/`, (req, res, ctx) => {
    return res(ctx.status(422), ctx.json({ detail: 'Validation error' }));
  }),
  
  rest.post(`${API_BASE_URL}/analysis/analyze`, (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({ detail: 'AI service unavailable' }));
  })
];