# AI教学助手系统

> 基于多智能体协作的大学编程基础课AI教学辅助平台

## 🎯 项目概览

AI教学助手系统是一个专注于大学编程基础课程（C语言、Python）的智能教学辅助平台，通过AutoGen框架实现的多智能体协作，为学生提供个性化、渐进式的编程学习反馈，帮助教师提高教学效率和教学质量。

## 🏗️ 系统架构

基于**6个核心AI Agent**的协作架构：
- **CodeAnalyzer**：代码技术分析专家
- **PedagogyExpert**：教学策略专家  
- **StudentProfiler**：学生画像分析师
- **FeedbackGenerator**：反馈内容生成器
- **QualityController**：质量控制器
- **DebuggingMentor**：调试导师

## 📁 项目结构

```
02.AI-teacher/
├── 📋 README.md                    # 项目总览
├── 📋 CLAUDE.md                    # Claude Code配置
├── 📁 docs/                        # 项目文档
│   ├── 📁 requirements/            # 需求文档
│   │   └── rfq.md                  # 项目需求规格书
│   ├── 📁 architecture/            # 技术架构
│   │   ├── 📁 ai-agents/           # AI智能体设计
│   │   │   ├── agents_prompts.md         # Agent提示语配置
│   │   │   ├── agents_workflows.md       # Agent工作流程
│   │   │   └── agents_configuration.md   # Agent完整配置
│   │   ├── 📁 system-design/       # 系统设计（待创建）
│   │   └── 📁 apis/               # API设计（待创建）
│   ├── 📁 management/              # 项目管理
│   │   ├── 📁 team/               # 团队管理
│   │   │   └── project_team_roles.md     # 团队角色定义
│   │   ├── 📁 process/            # 流程管理
│   │   │   ├── pdca_project_management.md        # PDCA管理流程
│   │   │   └── team_collaboration_workflows.md   # 团队协作流程
│   │   └── 📁 planning/           # 项目规划
│   │       └── project_milestones_deliverables.md # 里程碑和交付物
│   └── 📁 guides/                 # 使用指南（待创建）
└── 📁 templates/                  # 文档模板（待创建）
```

## 🚀 快速开始

### 1. 项目理解
- 📖 [项目需求规格书](docs/requirements/rfq.md) - 了解项目背景、目标和核心价值
- 🏗️ [AI Agent配置](docs/architecture/ai-agents/agents_configuration.md) - 理解系统架构设计

### 2. 团队协作
- 👥 [团队角色定义](docs/management/team/project_team_roles.md) - 了解团队结构和职责分工
- 🔄 [PDCA管理流程](docs/management/process/pdca_project_management.md) - 掌握项目管理方法
- 🤝 [协作工作流程](docs/management/process/team_collaboration_workflows.md) - 理解团队协作机制

### 3. 项目规划
- 🎯 [项目里程碑](docs/management/planning/project_milestones_deliverables.md) - 查看项目规划和交付计划

### 4. 技术实现
- 🤖 [Agent提示语](docs/architecture/ai-agents/agents_prompts.md) - 核心AI提示语配置
- ⚡ [Agent工作流](docs/architecture/ai-agents/agents_workflows.md) - 智能体协作流程

## 🎨 核心特性

### 🧠 智能化教学反馈
- **多维度分析**：语法、逻辑、质量、性能全方位代码分析
- **个性化适配**：基于学生能力水平和学习风格定制反馈
- **渐进式指导**：从情感支持到技能训练的分层反馈体系

### 🎯 教学法驱动
- **建构主义学习**：基于学生已有知识构建新理解
- **最近发展区理论**：提供适合学生当前水平的挑战
- **苏格拉底式引导**：通过问题引导学生独立思考

### 🔧 高质量工程
- **多层质量控制**：从技术准确性到教学效果的全链路质量保障
- **持续优化**：基于PDCA循环的持续改进机制
- **数据驱动**：基于用户行为和学习效果的智能优化

## 🎯 目标用户

### 👨‍🏫 大学教师
- **减轻批改负担**：自动化处理重复性作业批改工作
- **提升教学质量**：获得专业的教学策略和反馈建议
- **数据驱动教学**：基于学生学习数据调整教学策略

### 👨‍🎓 大学生
- **即时反馈**：提交代码后立即获得详细的学习指导
- **个性化学习**：根据个人学习风格和能力定制学习路径
- **技能提升**：系统性培养编程思维和调试能力

## 📊 预期成果

### 量化目标
- 🎯 **AI反馈准确率** > 85%
- ⚡ **系统响应时间** < 3秒  
- 👥 **并发用户支持** > 500
- 📈 **学习效果提升** > 20%
- 😊 **用户满意度** > 4.0/5.0

### 商业价值
- 🏫 **试点学校** ≥ 5所
- 💰 **商业化转化率** > 30%
- 🌍 **市场覆盖** 大学编程基础课程领域
- 🚀 **技术创新** 多智能体教学应用领域的突破

## 🛣️ 项目路线图

### Phase 1: MVP开发 (4个月)
- 🔧 基础平台搭建
- 🤖 核心AI功能实现
- 💻 基础前后端开发
- 🧪 系统集成测试

### Phase 2: 功能增强 (3个月)  
- 🌐 多编程语言支持
- 👥 班级管理功能
- 🧠 高级AI功能
- 📊 数据分析能力

### Phase 3: 商业化准备 (4个月)
- 💼 商业化功能开发
- 🧪 大规模测试优化
- 🎯 试点部署验证
- 📈 效果评估分析

### Phase 4: 规模化部署 (4个月)
- 🚀 产品正式发布
- 📢 市场推广展开
- 🌟 平台生态建设
- 🌍 国际化规划

## 🤝 参与贡献

我们欢迎各种形式的贡献！请查看相关文档了解如何参与：

- 📖 阅读[项目文档](docs/)了解项目详情
- 🐛 提交Issue报告问题或建议
- 💡 参与功能设计和技术讨论
- 🔧 贡献代码和文档改进

## 📞 联系我们

- 📧 **项目邮箱**：ai-teacher@example.com
- 📋 **项目看板**：[Jira看板链接]
- 💬 **技术讨论**：[Slack群组链接]
- 📚 **知识库**：[Confluence空间链接]

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

<div align="center">

**🌟 让AI助力教育，让学习更加高效！🌟**

Built with ❤️ by AI教学助手团队

</div>