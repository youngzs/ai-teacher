"""
AI教学助手系统 - 代码执行服务 (Sprint 4)
安全的代码执行环境，支持C、Python等语言

Author: AI Backend Architecture Expert
Date: Sprint 4
"""

import asyncio
import subprocess
import tempfile
import os
import shutil
import uuid
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..core.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    COMPILATION_ERROR = "compilation_error"
    RUNTIME_ERROR = "runtime_error"


class ProgrammingLanguage(Enum):
    """支持的编程语言"""
    C = "c"
    CPP = "cpp"
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"


@dataclass
class TestCase:
    """测试用例"""
    id: str
    input: str
    expected_output: str
    description: str = ""
    is_hidden: bool = False
    points: float = 1.0


@dataclass
class TestResult:
    """测试结果"""
    test_case_id: str
    passed: bool
    actual_output: str
    expected_output: str
    execution_time: float  # 毫秒
    error_message: Optional[str] = None


@dataclass
class ExecutionResult:
    """代码执行结果"""
    execution_id: str
    status: ExecutionStatus
    output: str
    error: Optional[str] = None
    execution_time: float = 0  # 毫秒
    memory_used: int = 0  # 字节
    compilation_output: Optional[str] = None
    test_results: List[TestResult] = field(default_factory=list)
    tests_passed: int = 0
    total_tests: int = 0
    score: float = 0.0


class CodeExecutionService:
    """
    代码执行服务

    提供安全的代码编译和执行环境
    支持多语言、测试用例验证、资源限制
    """

    # 语言配置
    LANGUAGE_CONFIG = {
        ProgrammingLanguage.C: {
            "extension": ".c",
            "compile_cmd": ["gcc", "-o", "{output}", "{source}", "-lm", "-Wall"],
            "run_cmd": ["./{executable}"],
            "needs_compilation": True,
        },
        ProgrammingLanguage.CPP: {
            "extension": ".cpp",
            "compile_cmd": ["g++", "-o", "{output}", "{source}", "-std=c++17", "-Wall"],
            "run_cmd": ["./{executable}"],
            "needs_compilation": True,
        },
        ProgrammingLanguage.PYTHON: {
            "extension": ".py",
            "compile_cmd": None,
            "run_cmd": ["python3", "{source}"],
            "needs_compilation": False,
        },
        ProgrammingLanguage.JAVA: {
            "extension": ".java",
            "compile_cmd": ["javac", "{source}"],
            "run_cmd": ["java", "-cp", "{dir}", "Main"],
            "needs_compilation": True,
            "class_name": "Main",
        },
        ProgrammingLanguage.JAVASCRIPT: {
            "extension": ".js",
            "compile_cmd": None,
            "run_cmd": ["node", "{source}"],
            "needs_compilation": False,
        },
    }

    # 资源限制
    DEFAULT_TIMEOUT = 5  # 秒
    DEFAULT_MEMORY_LIMIT = 256 * 1024 * 1024  # 256MB
    MAX_OUTPUT_SIZE = 10 * 1024  # 10KB

    def __init__(self):
        self.temp_base_dir = Path(tempfile.gettempdir()) / "ai_teacher_code_execution"
        self.temp_base_dir.mkdir(parents=True, exist_ok=True)
        self.active_executions: Dict[str, asyncio.subprocess.Process] = {}
        logger.info(f"CodeExecutionService initialized, temp dir: {self.temp_base_dir}")

    async def execute_code(
        self,
        code: str,
        language: ProgrammingLanguage,
        test_cases: Optional[List[TestCase]] = None,
        timeout: float = DEFAULT_TIMEOUT,
        stdin_input: Optional[str] = None,
    ) -> ExecutionResult:
        """
        执行代码

        Args:
            code: 源代码
            language: 编程语言
            test_cases: 测试用例列表
            timeout: 超时时间（秒）
            stdin_input: 标准输入（当没有测试用例时使用）

        Returns:
            ExecutionResult: 执行结果
        """
        execution_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        # 创建临时工作目录
        work_dir = self.temp_base_dir / execution_id
        work_dir.mkdir(parents=True, exist_ok=True)

        try:
            config = self.LANGUAGE_CONFIG.get(language)
            if not config:
                return ExecutionResult(
                    execution_id=execution_id,
                    status=ExecutionStatus.ERROR,
                    output="",
                    error=f"Unsupported language: {language.value}",
                )

            # 保存源代码文件
            if language == ProgrammingLanguage.JAVA:
                source_file = work_dir / f"{config.get('class_name', 'Main')}{config['extension']}"
            else:
                source_file = work_dir / f"code{config['extension']}"

            source_file.write_text(code, encoding='utf-8')
            logger.info(f"[{execution_id}] Source file saved: {source_file}")

            # 编译（如果需要）
            executable = None
            if config["needs_compilation"]:
                compile_result = await self._compile_code(
                    source_file, work_dir, config, execution_id
                )
                if compile_result["status"] != "success":
                    return ExecutionResult(
                        execution_id=execution_id,
                        status=ExecutionStatus.COMPILATION_ERROR,
                        output="",
                        error=compile_result.get("error", "Compilation failed"),
                        compilation_output=compile_result.get("output", ""),
                    )
                executable = compile_result.get("executable")

            # 执行测试用例或单次运行
            if test_cases:
                result = await self._run_with_tests(
                    source_file, executable, work_dir, config, test_cases, timeout, execution_id
                )
            else:
                result = await self._run_once(
                    source_file, executable, work_dir, config, stdin_input or "", timeout, execution_id
                )

            # 计算执行时间
            result.execution_time = (time.time() - start_time) * 1000

            return result

        except Exception as e:
            logger.error(f"[{execution_id}] Execution error: {e}")
            return ExecutionResult(
                execution_id=execution_id,
                status=ExecutionStatus.ERROR,
                output="",
                error=str(e),
                execution_time=(time.time() - start_time) * 1000,
            )

        finally:
            # 清理临时目录
            try:
                shutil.rmtree(work_dir, ignore_errors=True)
            except Exception as e:
                logger.warning(f"[{execution_id}] Failed to cleanup: {e}")

    async def _compile_code(
        self,
        source_file: Path,
        work_dir: Path,
        config: Dict,
        execution_id: str,
    ) -> Dict[str, Any]:
        """编译代码"""
        try:
            executable = work_dir / "program"

            compile_cmd = [
                c.format(
                    source=str(source_file),
                    output=str(executable),
                    dir=str(work_dir),
                )
                for c in config["compile_cmd"]
            ]

            logger.info(f"[{execution_id}] Compiling: {' '.join(compile_cmd)}")

            process = await asyncio.create_subprocess_exec(
                *compile_cmd,
                cwd=str(work_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "status": "error",
                    "error": "Compilation timeout",
                    "output": "",
                }

            if process.returncode != 0:
                error_output = stderr.decode('utf-8', errors='replace')
                return {
                    "status": "error",
                    "error": error_output or "Compilation failed",
                    "output": stdout.decode('utf-8', errors='replace'),
                }

            return {
                "status": "success",
                "executable": executable,
                "output": stdout.decode('utf-8', errors='replace'),
            }

        except Exception as e:
            logger.error(f"[{execution_id}] Compilation error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "output": "",
            }

    async def _run_once(
        self,
        source_file: Path,
        executable: Optional[Path],
        work_dir: Path,
        config: Dict,
        stdin_input: str,
        timeout: float,
        execution_id: str,
    ) -> ExecutionResult:
        """单次运行代码"""
        try:
            run_cmd = self._build_run_command(source_file, executable, work_dir, config)
            logger.info(f"[{execution_id}] Running: {' '.join(run_cmd)}")

            run_start = time.time()

            process = await asyncio.create_subprocess_exec(
                *run_cmd,
                cwd=str(work_dir),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.active_executions[execution_id] = process

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=stdin_input.encode('utf-8')),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                return ExecutionResult(
                    execution_id=execution_id,
                    status=ExecutionStatus.TIMEOUT,
                    output="",
                    error=f"Execution timeout ({timeout}s)",
                )
            finally:
                self.active_executions.pop(execution_id, None)

            run_time = (time.time() - run_start) * 1000

            output = stdout.decode('utf-8', errors='replace')
            error = stderr.decode('utf-8', errors='replace')

            # 截断过长输出
            if len(output) > self.MAX_OUTPUT_SIZE:
                output = output[:self.MAX_OUTPUT_SIZE] + "\n... (output truncated)"

            if process.returncode != 0:
                return ExecutionResult(
                    execution_id=execution_id,
                    status=ExecutionStatus.RUNTIME_ERROR,
                    output=output,
                    error=error or f"Process exited with code {process.returncode}",
                    execution_time=run_time,
                )

            return ExecutionResult(
                execution_id=execution_id,
                status=ExecutionStatus.SUCCESS,
                output=output,
                error=error if error else None,
                execution_time=run_time,
            )

        except Exception as e:
            logger.error(f"[{execution_id}] Run error: {e}")
            return ExecutionResult(
                execution_id=execution_id,
                status=ExecutionStatus.ERROR,
                output="",
                error=str(e),
            )

    async def _run_with_tests(
        self,
        source_file: Path,
        executable: Optional[Path],
        work_dir: Path,
        config: Dict,
        test_cases: List[TestCase],
        timeout: float,
        execution_id: str,
    ) -> ExecutionResult:
        """运行测试用例"""
        test_results: List[TestResult] = []
        total_score = 0.0
        max_score = sum(tc.points for tc in test_cases)

        for test_case in test_cases:
            tc_start = time.time()

            try:
                run_cmd = self._build_run_command(source_file, executable, work_dir, config)

                process = await asyncio.create_subprocess_exec(
                    *run_cmd,
                    cwd=str(work_dir),
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(input=test_case.input.encode('utf-8')),
                        timeout=timeout,
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    test_results.append(TestResult(
                        test_case_id=test_case.id,
                        passed=False,
                        actual_output="",
                        expected_output=test_case.expected_output,
                        execution_time=(time.time() - tc_start) * 1000,
                        error_message=f"Timeout ({timeout}s)",
                    ))
                    continue

                actual_output = stdout.decode('utf-8', errors='replace').strip()
                expected_output = test_case.expected_output.strip()

                # 比较输出（忽略尾随空白）
                passed = self._compare_output(actual_output, expected_output)

                if passed:
                    total_score += test_case.points

                test_results.append(TestResult(
                    test_case_id=test_case.id,
                    passed=passed,
                    actual_output=actual_output,
                    expected_output=expected_output,
                    execution_time=(time.time() - tc_start) * 1000,
                    error_message=stderr.decode('utf-8', errors='replace') if stderr else None,
                ))

            except Exception as e:
                test_results.append(TestResult(
                    test_case_id=test_case.id,
                    passed=False,
                    actual_output="",
                    expected_output=test_case.expected_output,
                    execution_time=(time.time() - tc_start) * 1000,
                    error_message=str(e),
                ))

        tests_passed = sum(1 for r in test_results if r.passed)
        final_score = (total_score / max_score * 100) if max_score > 0 else 0

        return ExecutionResult(
            execution_id=execution_id,
            status=ExecutionStatus.SUCCESS if tests_passed == len(test_cases) else ExecutionStatus.ERROR,
            output="\n".join(f"Test {i+1}: {'✓' if r.passed else '✗'}" for i, r in enumerate(test_results)),
            test_results=test_results,
            tests_passed=tests_passed,
            total_tests=len(test_cases),
            score=final_score,
        )

    def _build_run_command(
        self,
        source_file: Path,
        executable: Optional[Path],
        work_dir: Path,
        config: Dict,
    ) -> List[str]:
        """构建运行命令"""
        return [
            c.format(
                source=str(source_file),
                executable=str(executable.name) if executable else "",
                dir=str(work_dir),
            )
            for c in config["run_cmd"]
        ]

    def _compare_output(self, actual: str, expected: str) -> bool:
        """比较输出（智能比较，忽略尾随空白和换行差异）"""
        actual_lines = [line.rstrip() for line in actual.split('\n')]
        expected_lines = [line.rstrip() for line in expected.split('\n')]

        # 移除尾部空行
        while actual_lines and not actual_lines[-1]:
            actual_lines.pop()
        while expected_lines and not expected_lines[-1]:
            expected_lines.pop()

        return actual_lines == expected_lines

    async def cancel_execution(self, execution_id: str) -> bool:
        """取消执行"""
        process = self.active_executions.get(execution_id)
        if process:
            process.kill()
            self.active_executions.pop(execution_id, None)
            logger.info(f"[{execution_id}] Execution cancelled")
            return True
        return False

    def cleanup(self):
        """清理所有临时文件"""
        try:
            shutil.rmtree(self.temp_base_dir, ignore_errors=True)
            self.temp_base_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# 全局服务实例
_code_execution_service: Optional[CodeExecutionService] = None


def get_code_execution_service() -> CodeExecutionService:
    """获取代码执行服务实例"""
    global _code_execution_service
    if _code_execution_service is None:
        _code_execution_service = CodeExecutionService()
    return _code_execution_service
