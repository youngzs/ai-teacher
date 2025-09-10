# 📚 项目文档导航

欢迎来到AI教学助手系统的文档中心！本文档库包含了项目的完整设计、开发和管理文档。

## 📋 文档概览

### 🎯 [需求文档](requirements/)
- **[项目需求规格书](requirements/rfq.md)** - 项目的背景分析、核心价值定位、功能需求和技术方案

### 🏗️ [技术架构](architecture/)

#### 🤖 [AI智能体设计](architecture/ai-agents/)
- **[Agent提示语配置](architecture/ai-agents/agents_prompts.md)** - 6个核心Agent的详细提示语定义
- **[Agent工作流程](architecture/ai-agents/agents_workflows.md)** - AI智能体之间的协作工作流程
- **[Agent完整配置](architecture/ai-agents/agents_configuration.md)** - 系统架构和Agent配置的完整文档

#### 🔧 [系统设计](architecture/system-design/) `[待完善]`
- 系统整体架构设计
- 数据库设计文档
- 接口设计规范

#### 📡 [API设计](architecture/apis/) `[待完善]`
- RESTful API规范
- GraphQL接口设计
- 第三方集成接口

### 👥 [项目管理](management/)

#### 🎭 [团队管理](management/team/)
- **[团队角色定义](management/team/project_team_roles.md)** - 8个核心角色的职责、输出和协作方式

#### ⚙️ [流程管理](management/process/)
- **[PDCA项目管理流程](management/process/pdca_project_management.md)** - 基于PDCA循环的项目管理方法论
- **[团队协作工作流程](management/process/team_collaboration_workflows.md)** - 跨角色协作机制和沟通规范

#### 📅 [项目规划](management/planning/)
- **[项目里程碑和交付物](management/planning/project_milestones_deliverables.md)** - 16个月完整项目规划和质量标准

### 📖 [使用指南](guides/) `[待完善]`
- 开发环境搭建指南
- 代码规范和最佳实践
- 测试指南和质量标准
- 部署和运维手册

## 🗺️ 文档使用指南

### 新成员入门路径

#### 1️⃣ 项目理解阶段
1. 📖 首先阅读 [项目需求规格书](requirements/rfq.md) 了解项目背景和目标
2. 🏗️ 查看 [Agent完整配置](architecture/ai-agents/agents_configuration.md) 理解系统架构

#### 2️⃣ 团队协作阶段  
3. 👥 学习 [团队角色定义](management/team/project_team_roles.md) 了解自己的职责
4. 🔄 掌握 [PDCA管理流程](management/process/pdca_project_management.md) 理解工作方法
5. 🤝 熟悉 [协作工作流程](management/process/team_collaboration_workflows.md) 建立协作默契

#### 3️⃣ 技术实现阶段
6. 🤖 研读 [Agent提示语配置](architecture/ai-agents/agents_prompts.md) 理解AI实现
7. ⚡ 掌握 [Agent工作流程](architecture/ai-agents/agents_workflows.md) 了解系统运作
8. 🎯 参考 [项目里程碑](management/planning/project_milestones_deliverables.md) 规划开发任务

### 不同角色的重点文档

#### 🎭 Product Manager
- 📖 [项目需求规格书](requirements/rfq.md) - 产品定位和需求分析
- 📅 [项目里程碑和交付物](management/planning/project_milestones_deliverables.md) - 项目规划管控
- 🔄 [PDCA管理流程](management/process/pdca_project_management.md) - 项目管理方法

#### 🤖 AI Expert  
- 🤖 [Agent提示语配置](architecture/ai-agents/agents_prompts.md) - 核心技术实现
- ⚡ [Agent工作流程](architecture/ai-agents/agents_workflows.md) - 智能体协作设计
- 🏗️ [Agent完整配置](architecture/ai-agents/agents_configuration.md) - 系统架构理解

#### 💻 开发工程师
- 🏗️ [系统设计文档](architecture/system-design/) - 技术架构指导
- 📡 [API设计规范](architecture/apis/) - 接口开发标准
- 🤝 [协作工作流程](management/process/team_collaboration_workflows.md) - 开发协作规范

#### 🧪 QA Engineer
- 📅 [项目里程碑和交付物](management/planning/project_milestones_deliverables.md) - 质量标准参考
- 🏗️ [Agent完整配置](architecture/ai-agents/agents_configuration.md) - 功能测试理解
- 🔄 [PDCA管理流程](management/process/pdca_project_management.md) - 质量管理方法

#### 🎨 UX/UI Designer
- 📖 [项目需求规格书](requirements/rfq.md) - 用户需求理解  
- 👥 [团队角色定义](management/team/project_team_roles.md) - 协作对象了解
- 🤝 [协作工作流程](management/process/team_collaboration_workflows.md) - 设计协作流程

## 📝 文档维护规范

### 文档更新原则
- 📅 **及时性**：重要变更24小时内更新文档
- 🎯 **准确性**：确保文档内容与实际情况一致
- 📖 **可读性**：使用清晰的结构和简洁的语言
- 🔗 **关联性**：维护文档间的交叉引用关系

### 文档版本管理
- 📋 重要文档使用版本号管理（v1.0, v1.1等）
- 📝 记录每次更新的原因和主要变更
- 🗂️ 定期归档历史版本
- 🔍 建立文档变更审查机制

### 贡献指南
1. 📬 **提交Issues**：发现文档问题或改进建议
2. 🔧 **Pull Request**：直接修改文档并提交PR
3. 💬 **讨论区**：参与文档规范和内容讨论
4. 📊 **反馈调研**：定期收集文档使用反馈

## 🔍 快速查找

### 按主题查找
- 🎯 **项目规划** → [management/planning/](management/planning/)
- 🤖 **AI技术** → [architecture/ai-agents/](architecture/ai-agents/)  
- 👥 **团队协作** → [management/team/](management/team/) + [management/process/](management/process/)
- 📋 **需求分析** → [requirements/](requirements/)

### 按角色查找
- 🎭 **管理类角色** → [management/](management/)
- 💻 **技术类角色** → [architecture/](architecture/)
- 🎨 **设计类角色** → [requirements/](requirements/) + [guides/](guides/)
- 📚 **全员必读** → [README.md](../README.md) + [requirements/rfq.md](requirements/rfq.md)

### 按开发阶段查找
- 🚀 **项目启动** → [requirements/](requirements/) + [management/team/](management/team/)
- ⚙️ **开发阶段** → [architecture/](architecture/) + [management/process/](management/process/)
- 🧪 **测试阶段** → [management/planning/](management/planning/) + [guides/](guides/)
- 📦 **发布阶段** → [guides/](guides/) + [management/process/](management/process/)

---

<div align="center">

📚 **持续完善文档，助力项目成功！** 📚

如有疑问，请联系项目管理团队 📧

</div>