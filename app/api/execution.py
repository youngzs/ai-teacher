"""
AI教学助手系统 - 代码执行API端点 (Sprint 4)
处理代码执行请求、测试用例验证等功能

Author: AI Backend Architecture Expert
Date: Sprint 4
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from ..database.database import get_db
from ..database.models import User
from ..core.dependencies import (
    get_current_active_user,
    rate_limit_check,
)
from ..schemas.common import ResponseModel
from ..utils.logger import get_logger
from ..services.code_execution_service import (
    get_code_execution_service,
    CodeExecutionService,
    ExecutionResult,
    ExecutionStatus,
    ProgrammingLanguage,
    TestCase,
)

logger = get_logger(__name__)
router = APIRouter()


# ============= Pydantic模型定义 =============

class TestCaseRequest(BaseModel):
    """测试用例请求"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    input: str = Field(..., description="测试输入")
    expected_output: str = Field(..., description="期望输出")
    description: str = Field(default="", description="测试描述")
    is_hidden: bool = Field(default=False, description="是否为隐藏测试")
    points: float = Field(default=1.0, ge=0, description="分值")


class CodeExecutionRequest(BaseModel):
    """代码执行请求"""
    code: str = Field(..., min_length=1, max_length=50000, description="源代码")
    language: str = Field(..., description="编程语言: c, cpp, python, java, javascript")
    test_cases: Optional[List[TestCaseRequest]] = Field(default=None, description="测试用例列表")
    stdin_input: Optional[str] = Field(default=None, max_length=10000, description="标准输入")
    timeout: float = Field(default=5.0, ge=1.0, le=30.0, description="超时时间(秒)")


class TestResultResponse(BaseModel):
    """测试结果响应"""
    test_case_id: str
    passed: bool
    actual_output: str
    expected_output: str
    execution_time: float
    error_message: Optional[str] = None


class CodeExecutionResponse(BaseModel):
    """代码执行响应"""
    execution_id: str
    status: str
    output: str
    error: Optional[str] = None
    execution_time: float
    memory_used: int = 0
    compilation_output: Optional[str] = None
    test_results: List[TestResultResponse] = []
    tests_passed: int = 0
    total_tests: int = 0
    score: float = 0.0
    executed_at: datetime = Field(default_factory=datetime.utcnow)


class CancelExecutionRequest(BaseModel):
    """取消执行请求"""
    execution_id: str


# ============= 依赖注入 =============

def get_execution_service() -> CodeExecutionService:
    """获取代码执行服务实例"""
    return get_code_execution_service()


# ============= API端点 =============

@router.post("/run", response_model=ResponseModel[CodeExecutionResponse])
async def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_active_user),
    execution_service: CodeExecutionService = Depends(get_execution_service),
    _: bool = Depends(rate_limit_check),
):
    """
    执行代码

    支持的语言: c, cpp, python, java, javascript
    可以提供测试用例进行自动测试
    """
    try:
        # 解析语言
        try:
            language = ProgrammingLanguage(request.language.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language: {request.language}. Supported: c, cpp, python, java, javascript"
            )

        # 转换测试用例
        test_cases = None
        if request.test_cases:
            test_cases = [
                TestCase(
                    id=tc.id,
                    input=tc.input,
                    expected_output=tc.expected_output,
                    description=tc.description,
                    is_hidden=tc.is_hidden,
                    points=tc.points,
                )
                for tc in request.test_cases
            ]

        logger.info(f"User {current_user.id} executing {language.value} code")

        # 执行代码
        result: ExecutionResult = await execution_service.execute_code(
            code=request.code,
            language=language,
            test_cases=test_cases,
            timeout=request.timeout,
            stdin_input=request.stdin_input,
        )

        # 构建响应
        response = CodeExecutionResponse(
            execution_id=result.execution_id,
            status=result.status.value,
            output=result.output,
            error=result.error,
            execution_time=result.execution_time,
            memory_used=result.memory_used,
            compilation_output=result.compilation_output,
            test_results=[
                TestResultResponse(
                    test_case_id=tr.test_case_id,
                    passed=tr.passed,
                    actual_output=tr.actual_output,
                    expected_output=tr.expected_output,
                    execution_time=tr.execution_time,
                    error_message=tr.error_message,
                )
                for tr in result.test_results
            ],
            tests_passed=result.tests_passed,
            total_tests=result.total_tests,
            score=result.score,
        )

        return ResponseModel(
            success=result.status in [ExecutionStatus.SUCCESS],
            message="Code executed successfully" if result.status == ExecutionStatus.SUCCESS else f"Execution completed with status: {result.status.value}",
            data=response,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Code execution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code execution failed: {str(e)}"
        )


@router.post("/run-quick", response_model=ResponseModel[CodeExecutionResponse])
async def execute_code_quick(
    request: CodeExecutionRequest,
    execution_service: CodeExecutionService = Depends(get_execution_service),
):
    """
    快速执行代码（无需认证，用于练习模式）

    限制:
    - 超时时间最大5秒
    - 无测试用例支持
    - 有更严格的速率限制
    """
    try:
        # 解析语言
        try:
            language = ProgrammingLanguage(request.language.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language: {request.language}"
            )

        # 快速模式限制
        timeout = min(request.timeout, 5.0)

        logger.info(f"Quick execution: {language.value} code")

        # 执行代码（无测试用例）
        result = await execution_service.execute_code(
            code=request.code,
            language=language,
            test_cases=None,
            timeout=timeout,
            stdin_input=request.stdin_input,
        )

        response = CodeExecutionResponse(
            execution_id=result.execution_id,
            status=result.status.value,
            output=result.output,
            error=result.error,
            execution_time=result.execution_time,
            memory_used=result.memory_used,
            compilation_output=result.compilation_output,
        )

        return ResponseModel(
            success=result.status == ExecutionStatus.SUCCESS,
            message="Quick execution completed",
            data=response,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quick execution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution failed: {str(e)}"
        )


@router.post("/cancel", response_model=ResponseModel[Dict[str, Any]])
async def cancel_execution(
    request: CancelExecutionRequest,
    current_user: User = Depends(get_current_active_user),
    execution_service: CodeExecutionService = Depends(get_execution_service),
):
    """取消正在执行的代码"""
    try:
        cancelled = await execution_service.cancel_execution(request.execution_id)

        return ResponseModel(
            success=cancelled,
            message="Execution cancelled" if cancelled else "Execution not found or already completed",
            data={"execution_id": request.execution_id, "cancelled": cancelled},
        )

    except Exception as e:
        logger.error(f"Cancel execution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel execution: {str(e)}"
        )


@router.get("/languages", response_model=ResponseModel[List[Dict[str, Any]]])
async def get_supported_languages():
    """获取支持的编程语言列表"""
    languages = [
        {
            "id": "c",
            "name": "C",
            "extension": ".c",
            "description": "C programming language",
            "compiler": "gcc",
        },
        {
            "id": "cpp",
            "name": "C++",
            "extension": ".cpp",
            "description": "C++ programming language",
            "compiler": "g++",
        },
        {
            "id": "python",
            "name": "Python",
            "extension": ".py",
            "description": "Python 3.x",
            "runtime": "python3",
        },
        {
            "id": "java",
            "name": "Java",
            "extension": ".java",
            "description": "Java programming language",
            "compiler": "javac",
        },
        {
            "id": "javascript",
            "name": "JavaScript",
            "extension": ".js",
            "description": "JavaScript (Node.js)",
            "runtime": "node",
        },
    ]

    return ResponseModel(
        success=True,
        message="Supported languages retrieved",
        data=languages,
    )
