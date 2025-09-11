"""
AI教学助手系统 - 独立后端启动器
集成AI agents的完整后端服务

Author: AI Teaching System Architecture  
Date: 2025-09-11
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import uvicorn
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入AI组件
import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.agents.teaching_agents import MultiAgentTeachingSystem
from src.workflows.teaching_workflows_simple import WorkflowManager, WorkflowType
from src.models.teaching_models import (
    SubmissionData, ProgrammingLanguage, DifficultyLevel, 
    create_sample_submission, TeachingFeedback, FeedbackContent, AnalysisResult
)

# 创建FastAPI应用
app = FastAPI(
    title="AI Teaching Assistant System",
    description="AI-powered teaching assistant for programming education",
    version="1.0.0"
)

# 全局AI系统实例
teaching_system = None
workflow_manager = None


# Pydantic模型
class CodeSubmissionRequest(BaseModel):
    student_id: str
    assignment_id: str
    code: str
    language: str = "python"  # python, c, java
    difficulty: str = "beginner"  # beginner, intermediate, advanced


class TeachingFeedbackResponse(BaseModel):
    success: bool
    feedback: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


@app.on_event("startup")
async def startup_event():
    """启动时初始化AI系统"""
    global teaching_system, workflow_manager
    
    logger.info("Initializing AI Teaching System...")
    
    try:
        # 初始化教学系统
        teaching_system = MultiAgentTeachingSystem("python_basics")
        workflow_manager = WorkflowManager(teaching_system)
        
        logger.info("AI Teaching System initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize AI system: {e}")
        raise


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI Teaching Assistant System",
        "status": "running",
        "agents": 6,
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查AI系统状态
        system_ready = teaching_system is not None
        workflow_ready = workflow_manager is not None
        
        return {
            "status": "healthy" if system_ready and workflow_ready else "unhealthy",
            "ai_system": "ready" if system_ready else "not_ready",
            "workflow_manager": "ready" if workflow_ready else "not_ready",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/analyze", response_model=TeachingFeedbackResponse)
async def analyze_code_submission(request: CodeSubmissionRequest):
    """分析代码提交"""
    if not teaching_system or not workflow_manager:
        raise HTTPException(status_code=503, detail="AI system not initialized")
    
    start_time = datetime.now()
    
    try:
        logger.info(f"Processing code submission from student {request.student_id}")
        
        # 转换请求为SubmissionData
        submission_data = SubmissionData(
            student_id=request.student_id,
            assignment_id=request.assignment_id,
            assignment_description="Code analysis request",
            code=request.code,
            language=ProgrammingLanguage(request.language.lower()),
            submitted_at=datetime.now(),
            student_history={"difficulty": request.difficulty}
        )
        
        # 执行分析工作流
        result = await workflow_manager.execute_assignment_analysis(submission_data)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if result.feedback:
            return TeachingFeedbackResponse(
                success=True,
                feedback=result.feedback.to_dict(),
                processing_time=processing_time
            )
        else:
            return TeachingFeedbackResponse(
                success=False,
                error=result.error_message,
                processing_time=processing_time
            )
            
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"Code analysis failed: {e}")
        
        return TeachingFeedbackResponse(
            success=False,
            error=str(e),
            processing_time=processing_time
        )


@app.post("/debug", response_model=TeachingFeedbackResponse)
async def debug_guidance(request: CodeSubmissionRequest):
    """调试指导"""
    if not teaching_system or not workflow_manager:
        raise HTTPException(status_code=503, detail="AI system not initialized")
    
    start_time = datetime.now()
    
    try:
        logger.info(f"Starting debug guidance for student {request.student_id}")
        
        # 转换请求为SubmissionData
        submission_data = SubmissionData(
            student_id=request.student_id,
            assignment_id=request.assignment_id,
            assignment_description="Code analysis request",
            code=request.code,
            language=ProgrammingLanguage(request.language.lower()),
            submitted_at=datetime.now(),
            student_history={"difficulty": request.difficulty}
        )
        
        # 执行调试指导工作流
        result = await workflow_manager.execute_debugging_guidance(submission_data)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if result.feedback:
            return TeachingFeedbackResponse(
                success=True,
                feedback=result.feedback.to_dict(),
                processing_time=processing_time
            )
        else:
            return TeachingFeedbackResponse(
                success=False,
                error=result.error_message,
                processing_time=processing_time
            )
            
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"Debug guidance failed: {e}")
        
        return TeachingFeedbackResponse(
            success=False,
            error=str(e),
            processing_time=processing_time
        )


@app.get("/demo/sample")
async def sample_feedback():
    """获取示例反馈"""
    try:
        # 创建示例数据
        sample_submission = create_sample_submission()
        
        # 创建示例反馈
        sample_response = TeachingFeedback(
            session_id=f"sample_{int(datetime.now().timestamp())}",
            student_id=sample_submission.student_id,
            overall_score=85.0,
            code_analysis={"syntax_score": 90, "logic_score": 80, "suggestions": ["Good structure"]},
            student_profile={"competency_level": "advanced_beginner"},
            teaching_strategy="HINT",
            feedback_content={"recognition": "Good work!", "reflection": "Think about edge cases"},
            recommendations={"next_steps": ["Try more complex problems"]},
            quality_score=88,
            next_steps=["Practice more algorithms", "Review error handling"],
            estimated_completion_time="20分钟",
            created_at=datetime.now()
        )
        
        return {
            "success": True,
            "submission": sample_submission.to_dict(),
            "feedback": sample_response.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Sample generation failed: {e}")
        return {"success": False, "error": str(e)}


@app.get("/agents/status")
async def agents_status():
    """获取AI agents状态"""
    if not teaching_system:
        raise HTTPException(status_code=503, detail="AI system not initialized")
    
    try:
        agents_info = {}
        for agent_name, agent in teaching_system.agents.items():
            agents_info[agent_name] = {
                "name": agent.name if hasattr(agent, 'name') else agent_name,
                "status": "active",
                "type": "assistant_agent"
            }
        
        return {
            "total_agents": len(agents_info),
            "agents": agents_info,
            "system_status": "operational"
        }
        
    except Exception as e:
        logger.error(f"Agent status check failed: {e}")
        return {
            "total_agents": 0,
            "agents": {},
            "system_status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    # 启动服务器
    uvicorn.run(
        "run_ai_backend:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )