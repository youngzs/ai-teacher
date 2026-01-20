"""
AI教学助手系统 - 智能出题系统 (Sprint 5)
基于AI的编程题目自动生成系统

Author: AI Backend Architecture Expert
Date: Sprint 5
"""

import random
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from ..utils.structured_logging import get_structured_logger

logger = get_structured_logger(__name__)


class DifficultyLevel(Enum):
    """难度等级"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class QuestionType(Enum):
    """题目类型"""
    CODING = "coding"  # 编程题
    MULTIPLE_CHOICE = "multiple_choice"  # 选择题
    FILL_BLANK = "fill_blank"  # 填空题
    TRUE_FALSE = "true_false"  # 判断题
    CODE_ANALYSIS = "code_analysis"  # 代码分析题
    DEBUG = "debug"  # 调试题


class ProgrammingLanguage(Enum):
    """编程语言"""
    C = "c"
    PYTHON = "python"
    CPP = "cpp"


@dataclass
class TestCase:
    """测试用例"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    input: str = ""
    expected_output: str = ""
    description: str = ""
    is_hidden: bool = False
    points: float = 1.0


@dataclass
class Question:
    """题目"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    question_type: QuestionType = QuestionType.CODING
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    language: ProgrammingLanguage = ProgrammingLanguage.C
    topic: str = ""
    knowledge_points: List[str] = field(default_factory=list)
    starter_code: str = ""
    solution_code: str = ""
    test_cases: List[TestCase] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    time_limit_seconds: int = 5
    memory_limit_mb: int = 256
    created_at: datetime = field(default_factory=datetime.utcnow)
    # 选择题专用
    options: List[str] = field(default_factory=list)
    correct_answer: Optional[str] = None


# ============= 题目模板 =============

# C语言题目模板
C_QUESTION_TEMPLATES = {
    "basic_io": {
        "topics": ["输入输出", "printf", "scanf"],
        "difficulty": DifficultyLevel.BEGINNER,
        "templates": [
            {
                "title": "打印问候语",
                "description": "编写一个C程序，读取用户姓名并打印问候语。\n\n输入：一行字符串，表示用户姓名（不超过50个字符）\n输出：Hello, [姓名]!",
                "starter_code": '#include <stdio.h>\n\nint main() {\n    // 在这里编写代码\n    \n    return 0;\n}',
                "solution_code": '#include <stdio.h>\n\nint main() {\n    char name[51];\n    scanf("%s", name);\n    printf("Hello, %s!\\n", name);\n    return 0;\n}',
                "test_cases": [
                    {"input": "Alice", "expected_output": "Hello, Alice!", "description": "基本测试"},
                    {"input": "Bob", "expected_output": "Hello, Bob!", "description": "基本测试2"},
                ],
                "hints": ["使用scanf读取字符串", "使用printf输出格式化字符串"],
            },
            {
                "title": "计算两数之和",
                "description": "编写一个C程序，读取两个整数并输出它们的和。\n\n输入：两个整数，用空格分隔\n输出：两数之和",
                "starter_code": '#include <stdio.h>\n\nint main() {\n    // 在这里编写代码\n    \n    return 0;\n}',
                "solution_code": '#include <stdio.h>\n\nint main() {\n    int a, b;\n    scanf("%d %d", &a, &b);\n    printf("%d\\n", a + b);\n    return 0;\n}',
                "test_cases": [
                    {"input": "1 2", "expected_output": "3", "description": "正数相加"},
                    {"input": "-5 10", "expected_output": "5", "description": "负数相加"},
                    {"input": "0 0", "expected_output": "0", "description": "零相加"},
                ],
                "hints": ["使用scanf读取两个整数", "注意格式化输出"],
            },
        ],
    },
    "loops": {
        "topics": ["循环", "for", "while"],
        "difficulty": DifficultyLevel.BEGINNER,
        "templates": [
            {
                "title": "打印数字序列",
                "description": "编写一个C程序，输入一个正整数n，输出从1到n的所有数字，每个数字占一行。\n\n输入：一个正整数n (1 ≤ n ≤ 100)\n输出：从1到n的数字，每行一个",
                "starter_code": '#include <stdio.h>\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    // 在这里编写循环\n    \n    return 0;\n}',
                "solution_code": '#include <stdio.h>\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    for (int i = 1; i <= n; i++) {\n        printf("%d\\n", i);\n    }\n    return 0;\n}',
                "test_cases": [
                    {"input": "5", "expected_output": "1\n2\n3\n4\n5", "description": "打印1到5"},
                    {"input": "1", "expected_output": "1", "description": "边界情况"},
                ],
                "hints": ["使用for循环", "循环变量从1开始，到n结束"],
            },
            {
                "title": "计算阶乘",
                "description": "编写一个C程序，计算输入数字n的阶乘。\n\n输入：一个非负整数n (0 ≤ n ≤ 12)\n输出：n的阶乘",
                "starter_code": '#include <stdio.h>\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    // 计算阶乘\n    \n    return 0;\n}',
                "solution_code": '#include <stdio.h>\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    long long result = 1;\n    for (int i = 1; i <= n; i++) {\n        result *= i;\n    }\n    printf("%lld\\n", result);\n    return 0;\n}',
                "test_cases": [
                    {"input": "5", "expected_output": "120", "description": "5的阶乘"},
                    {"input": "0", "expected_output": "1", "description": "0的阶乘"},
                    {"input": "10", "expected_output": "3628800", "description": "10的阶乘"},
                ],
                "hints": ["阶乘定义：n! = 1 × 2 × 3 × ... × n", "0的阶乘是1"],
            },
        ],
    },
    "arrays": {
        "topics": ["数组", "array"],
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "templates": [
            {
                "title": "数组求和",
                "description": "编写一个C程序，读取n个整数并输出它们的和。\n\n输入：\n第一行：整数n (1 ≤ n ≤ 100)\n第二行：n个整数，用空格分隔\n\n输出：n个整数的和",
                "starter_code": '#include <stdio.h>\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    int arr[100];\n    // 读取数组并计算和\n    \n    return 0;\n}',
                "solution_code": '#include <stdio.h>\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    int arr[100];\n    int sum = 0;\n    for (int i = 0; i < n; i++) {\n        scanf("%d", &arr[i]);\n        sum += arr[i];\n    }\n    printf("%d\\n", sum);\n    return 0;\n}',
                "test_cases": [
                    {"input": "5\n1 2 3 4 5", "expected_output": "15", "description": "基本测试"},
                    {"input": "3\n-1 0 1", "expected_output": "0", "description": "包含负数"},
                ],
                "hints": ["使用循环读取数组元素", "在读取的同时累加求和"],
            },
            {
                "title": "找最大值",
                "description": "编写一个C程序，找出数组中的最大值。\n\n输入：\n第一行：整数n (1 ≤ n ≤ 100)\n第二行：n个整数\n\n输出：最大值",
                "starter_code": '#include <stdio.h>\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    int arr[100];\n    // 找最大值\n    \n    return 0;\n}',
                "solution_code": '#include <stdio.h>\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    int arr[100];\n    for (int i = 0; i < n; i++) {\n        scanf("%d", &arr[i]);\n    }\n    int max = arr[0];\n    for (int i = 1; i < n; i++) {\n        if (arr[i] > max) max = arr[i];\n    }\n    printf("%d\\n", max);\n    return 0;\n}',
                "test_cases": [
                    {"input": "5\n3 1 4 1 5", "expected_output": "5", "description": "基本测试"},
                    {"input": "3\n-1 -5 -2", "expected_output": "-1", "description": "全负数"},
                ],
                "hints": ["假设第一个元素是最大值", "遍历数组更新最大值"],
            },
        ],
    },
    "functions": {
        "topics": ["函数", "function"],
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "templates": [
            {
                "title": "判断素数",
                "description": "编写一个函数isPrime(n)，判断n是否为素数。\n\n输入：一个正整数n (2 ≤ n ≤ 10000)\n输出：如果是素数输出Yes，否则输出No",
                "starter_code": '#include <stdio.h>\n\n// 在这里实现isPrime函数\nint isPrime(int n) {\n    // TODO\n    return 0;\n}\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    if (isPrime(n)) {\n        printf("Yes\\n");\n    } else {\n        printf("No\\n");\n    }\n    return 0;\n}',
                "solution_code": '#include <stdio.h>\n\nint isPrime(int n) {\n    if (n < 2) return 0;\n    for (int i = 2; i * i <= n; i++) {\n        if (n % i == 0) return 0;\n    }\n    return 1;\n}\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    if (isPrime(n)) {\n        printf("Yes\\n");\n    } else {\n        printf("No\\n");\n    }\n    return 0;\n}',
                "test_cases": [
                    {"input": "7", "expected_output": "Yes", "description": "素数"},
                    {"input": "4", "expected_output": "No", "description": "非素数"},
                    {"input": "2", "expected_output": "Yes", "description": "最小素数"},
                ],
                "hints": ["素数只能被1和自身整除", "只需要检查到sqrt(n)"],
            },
        ],
    },
}

# Python题目模板
PYTHON_QUESTION_TEMPLATES = {
    "basic_io": {
        "topics": ["输入输出", "print", "input"],
        "difficulty": DifficultyLevel.BEGINNER,
        "templates": [
            {
                "title": "打印问候语",
                "description": "编写一个Python程序，读取用户姓名并打印问候语。\n\n输入：用户姓名\n输出：Hello, [姓名]!",
                "starter_code": "# 在这里编写代码\n",
                "solution_code": "name = input()\nprint(f'Hello, {name}!')",
                "test_cases": [
                    {"input": "Alice", "expected_output": "Hello, Alice!", "description": "基本测试"},
                    {"input": "Bob", "expected_output": "Hello, Bob!", "description": "基本测试2"},
                ],
                "hints": ["使用input()读取输入", "使用f-string格式化输出"],
            },
        ],
    },
    "loops": {
        "topics": ["循环", "for", "while"],
        "difficulty": DifficultyLevel.BEGINNER,
        "templates": [
            {
                "title": "计算列表和",
                "description": "编写一个Python程序，计算输入列表的元素之和。\n\n输入：\n第一行：整数n\n第二行：n个整数，用空格分隔\n\n输出：所有整数的和",
                "starter_code": "n = int(input())\nnums = list(map(int, input().split()))\n# 计算和\n",
                "solution_code": "n = int(input())\nnums = list(map(int, input().split()))\nprint(sum(nums))",
                "test_cases": [
                    {"input": "5\n1 2 3 4 5", "expected_output": "15", "description": "基本测试"},
                ],
                "hints": ["可以使用sum()函数", "也可以使用循环累加"],
            },
        ],
    },
}


class QuestionGenerator:
    """
    智能出题生成器

    根据主题、难度和语言生成编程题目
    """

    def __init__(self):
        self.templates = {
            ProgrammingLanguage.C: C_QUESTION_TEMPLATES,
            ProgrammingLanguage.PYTHON: PYTHON_QUESTION_TEMPLATES,
        }

    def generate_question(
        self,
        language: ProgrammingLanguage,
        topic: Optional[str] = None,
        difficulty: Optional[DifficultyLevel] = None,
        question_type: QuestionType = QuestionType.CODING,
    ) -> Optional[Question]:
        """
        生成题目

        Args:
            language: 编程语言
            topic: 主题（如"循环"、"数组"）
            difficulty: 难度级别
            question_type: 题目类型

        Returns:
            生成的题目
        """
        templates = self.templates.get(language, {})

        if not templates:
            logger.warning(f"No templates for language: {language}")
            return None

        # 筛选匹配的模板类别
        matching_categories = []
        for category, data in templates.items():
            # 检查难度
            if difficulty and data.get("difficulty") != difficulty:
                continue

            # 检查主题
            if topic:
                topics = data.get("topics", [])
                if not any(topic.lower() in t.lower() for t in topics):
                    continue

            matching_categories.append((category, data))

        if not matching_categories:
            # 如果没有精确匹配，随机选择
            matching_categories = list(templates.items())

        # 随机选择一个类别
        category, data = random.choice(matching_categories)

        # 从类别中随机选择一个模板
        template = random.choice(data["templates"])

        # 构建题目
        question = Question(
            title=template["title"],
            description=template["description"],
            question_type=question_type,
            difficulty=data.get("difficulty", DifficultyLevel.BEGINNER),
            language=language,
            topic=category,
            knowledge_points=data.get("topics", []),
            starter_code=template.get("starter_code", ""),
            solution_code=template.get("solution_code", ""),
            test_cases=[
                TestCase(
                    input=tc["input"],
                    expected_output=tc["expected_output"],
                    description=tc.get("description", ""),
                )
                for tc in template.get("test_cases", [])
            ],
            hints=template.get("hints", []),
        )

        logger.info(
            f"Generated question: {question.title}",
            language=language.value,
            topic=category,
            difficulty=question.difficulty.value,
        )

        return question

    def generate_question_set(
        self,
        language: ProgrammingLanguage,
        count: int = 5,
        topics: Optional[List[str]] = None,
        difficulty_distribution: Optional[Dict[DifficultyLevel, int]] = None,
    ) -> List[Question]:
        """
        生成题目集

        Args:
            language: 编程语言
            count: 题目数量
            topics: 主题列表
            difficulty_distribution: 难度分布

        Returns:
            题目列表
        """
        questions = []

        if difficulty_distribution:
            # 按难度分布生成
            for difficulty, num in difficulty_distribution.items():
                for _ in range(num):
                    topic = random.choice(topics) if topics else None
                    q = self.generate_question(language, topic, difficulty)
                    if q:
                        questions.append(q)
        else:
            # 平均分布
            for _ in range(count):
                topic = random.choice(topics) if topics else None
                difficulty = random.choice(list(DifficultyLevel))
                q = self.generate_question(language, topic, difficulty)
                if q:
                    questions.append(q)

        return questions

    def get_available_topics(self, language: ProgrammingLanguage) -> List[str]:
        """获取可用的主题列表"""
        templates = self.templates.get(language, {})
        topics = set()
        for data in templates.values():
            topics.update(data.get("topics", []))
        return list(topics)

    def add_template(
        self,
        language: ProgrammingLanguage,
        category: str,
        template: Dict[str, Any]
    ) -> bool:
        """添加自定义模板"""
        if language not in self.templates:
            self.templates[language] = {}

        if category not in self.templates[language]:
            self.templates[language][category] = {
                "topics": [],
                "difficulty": DifficultyLevel.BEGINNER,
                "templates": [],
            }

        self.templates[language][category]["templates"].append(template)
        logger.info(f"Added template to {language.value}/{category}")
        return True


# 全局出题器实例
question_generator = QuestionGenerator()


def get_question_generator() -> QuestionGenerator:
    """获取出题器实例"""
    return question_generator
