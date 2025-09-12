"""
AI教学助手系统 - 课程管理API端点
处理课程、班级、作业管理等功能

Author: AI Backend Architecture Expert
Date: 2025-09-11
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database.database import get_db
from ..database.models import User, Class, ClassMembership, Assignment
from ..core.dependencies import (
    get_current_active_user, require_teacher_or_admin, require_teacher,
    get_pagination_params, check_ownership_or_teacher
)
from ..schemas.courses import (
    ClassCreate, ClassUpdate, ClassResponse, ClassListResponse,
    AssignmentCreate, AssignmentUpdate, AssignmentResponse, AssignmentListResponse,
    ClassMemberAdd, ClassMemberResponse, ClassStats
)
from ..schemas.common import ResponseModel, PaginatedResponse
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# 班级管理端点
@router.get("/classes", response_model=ResponseModel[PaginatedResponse[ClassListResponse]])
async def get_classes(
    current_user: User = Depends(get_current_active_user),
    pagination: Dict[str, Any] = Depends(get_pagination_params),
    semester: Optional[str] = Query(None, description="学期筛选"),
    academic_year: Optional[str] = Query(None, description="学年筛选"),
    is_active: Optional[bool] = Query(None, description="是否激活筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取班级列表
    教师：获取自己的班级
    学生：获取自己参与的班级
    管理员：获取所有班级
    """
    try:
        # 构建查询条件
        conditions = []
        
        if current_user.role == "student":
            # 学生只能看到自己参与的班级
            conditions.append(
                Class.id.in_(
                    select(ClassMembership.class_id)
                    .where(ClassMembership.student_id == current_user.id)
                    .where(ClassMembership.is_active == True)
                )
            )
        elif current_user.role == "teacher":
            # 教师只能看到自己的班级
            conditions.append(Class.teacher_id == current_user.id)
        # 管理员可以看到所有班级，无需额外条件
        
        # 添加筛选条件
        if semester:
            conditions.append(Class.semester == semester)
        if academic_year:
            conditions.append(Class.academic_year == academic_year)
        if is_active is not None:
            conditions.append(Class.is_active == is_active)
        
        # 获取总数
        count_query = select(func.count(Class.id)).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 获取分页数据
        query = (
            select(Class, User.full_name.label("teacher_name"))
            .join(User, Class.teacher_id == User.id)
            .where(and_(*conditions))
            .order_by(Class.created_at.desc())
            .offset(pagination["offset"])
            .limit(pagination["limit"])
        )
        
        result = await db.execute(query)
        classes_data = result.all()
        
        # 构建响应数据
        classes = []
        for class_obj, teacher_name in classes_data:
            # 获取学生数量
            student_count_query = select(func.count(ClassMembership.id)).where(
                and_(
                    ClassMembership.class_id == class_obj.id,
                    ClassMembership.is_active == True
                )
            )
            student_count_result = await db.execute(student_count_query)
            student_count = student_count_result.scalar()
            
            classes.append(ClassListResponse(
                id=str(class_obj.id),
                name=class_obj.name,
                course_code=class_obj.course_code,
                semester=class_obj.semester,
                teacher_name=teacher_name,
                student_count=student_count,
                is_active=class_obj.is_active,
                created_at=class_obj.created_at
            ))
        
        return ResponseModel(
            success=True,
            data=PaginatedResponse(
                items=classes,
                total=total,
                page=pagination["page"],
                size=pagination["size"],
                pages=(total + pagination["size"] - 1) // pagination["size"]
            ),
            message="Classes retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving classes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve classes"
        )


@router.post("/classes", response_model=ResponseModel[ClassResponse])
async def create_class(
    class_data: ClassCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    创建班级（教师和管理员）
    """
    try:
        # 检查班级名称是否重复（同一教师）
        existing_class_result = await db.execute(
            select(Class).where(
                and_(
                    Class.name == class_data.name,
                    Class.teacher_id == current_user.id,
                    Class.is_active == True
                )
            )
        )
        
        if existing_class_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A class with this name already exists"
            )
        
        # 创建新班级
        new_class = Class(
            name=class_data.name,
            description=class_data.description,
            teacher_id=current_user.id,
            course_code=class_data.course_code,
            semester=class_data.semester,
            academic_year=class_data.academic_year,
            settings=class_data.settings or {},
            is_active=True
        )
        
        db.add(new_class)
        await db.commit()
        await db.refresh(new_class)
        
        logger.info(f"Class created: {new_class.name} by {current_user.username}")
        
        return ResponseModel(
            success=True,
            data=ClassResponse(
                id=str(new_class.id),
                name=new_class.name,
                description=new_class.description,
                teacher_id=str(new_class.teacher_id),
                teacher_name=current_user.full_name,
                course_code=new_class.course_code,
                semester=new_class.semester,
                academic_year=new_class.academic_year,
                settings=new_class.settings,
                is_active=new_class.is_active,
                student_count=0,
                assignment_count=0,
                created_at=new_class.created_at,
                updated_at=new_class.updated_at
            ),
            message="Class created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating class: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create class"
        )


@router.get("/classes/{class_id}", response_model=ResponseModel[ClassResponse])
async def get_class_detail(
    class_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取班级详情
    """
    try:
        # 获取班级信息
        class_query = select(Class, User.full_name.label("teacher_name")).join(
            User, Class.teacher_id == User.id
        ).where(Class.id == class_id)
        
        result = await db.execute(class_query)
        class_data = result.first()
        
        if not class_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
        
        class_obj, teacher_name = class_data
        
        # 权限检查
        if current_user.role == "student":
            # 学生只能查看自己参与的班级
            membership_result = await db.execute(
                select(ClassMembership).where(
                    and_(
                        ClassMembership.class_id == class_id,
                        ClassMembership.student_id == current_user.id,
                        ClassMembership.is_active == True
                    )
                )
            )
            if not membership_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        elif current_user.role == "teacher" and str(class_obj.teacher_id) != str(current_user.id):
            # 教师只能查看自己的班级
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # 获取统计信息
        student_count_query = select(func.count(ClassMembership.id)).where(
            and_(
                ClassMembership.class_id == class_id,
                ClassMembership.is_active == True
            )
        )
        student_count_result = await db.execute(student_count_query)
        student_count = student_count_result.scalar()
        
        assignment_count_query = select(func.count(Assignment.id)).where(
            Assignment.class_id == class_id
        )
        assignment_count_result = await db.execute(assignment_count_query)
        assignment_count = assignment_count_result.scalar()
        
        return ResponseModel(
            success=True,
            data=ClassResponse(
                id=str(class_obj.id),
                name=class_obj.name,
                description=class_obj.description,
                teacher_id=str(class_obj.teacher_id),
                teacher_name=teacher_name,
                course_code=class_obj.course_code,
                semester=class_obj.semester,
                academic_year=class_obj.academic_year,
                settings=class_obj.settings,
                is_active=class_obj.is_active,
                student_count=student_count,
                assignment_count=assignment_count,
                created_at=class_obj.created_at,
                updated_at=class_obj.updated_at
            ),
            message="Class details retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving class detail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve class details"
        )


@router.put("/classes/{class_id}", response_model=ResponseModel[ClassResponse])
async def update_class(
    class_id: str,
    class_data: ClassUpdate,
    current_user: User = Depends(require_teacher_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    更新班级信息（教师和管理员）
    """
    try:
        # 获取班级
        class_result = await db.execute(
            select(Class).where(Class.id == class_id)
        )
        class_obj = class_result.scalar_one_or_none()
        
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
        
        # 权限检查（教师只能修改自己的班级）
        if current_user.role == "teacher" and str(class_obj.teacher_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # 更新字段
        update_data = class_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(class_obj, field, value)
        
        await db.commit()
        await db.refresh(class_obj)
        
        # 获取教师信息
        teacher_result = await db.execute(
            select(User).where(User.id == class_obj.teacher_id)
        )
        teacher = teacher_result.scalar_one()
        
        # 获取统计信息
        student_count_query = select(func.count(ClassMembership.id)).where(
            and_(
                ClassMembership.class_id == class_id,
                ClassMembership.is_active == True
            )
        )
        student_count_result = await db.execute(student_count_query)
        student_count = student_count_result.scalar()
        
        assignment_count_query = select(func.count(Assignment.id)).where(
            Assignment.class_id == class_id
        )
        assignment_count_result = await db.execute(assignment_count_query)
        assignment_count = assignment_count_result.scalar()
        
        logger.info(f"Class updated: {class_obj.name} by {current_user.username}")
        
        return ResponseModel(
            success=True,
            data=ClassResponse(
                id=str(class_obj.id),
                name=class_obj.name,
                description=class_obj.description,
                teacher_id=str(class_obj.teacher_id),
                teacher_name=teacher.full_name,
                course_code=class_obj.course_code,
                semester=class_obj.semester,
                academic_year=class_obj.academic_year,
                settings=class_obj.settings,
                is_active=class_obj.is_active,
                student_count=student_count,
                assignment_count=assignment_count,
                created_at=class_obj.created_at,
                updated_at=class_obj.updated_at
            ),
            message="Class updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating class: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update class"
        )


# 作业管理端点
@router.get("/classes/{class_id}/assignments", response_model=ResponseModel[PaginatedResponse[AssignmentListResponse]])
async def get_class_assignments(
    class_id: str,
    current_user: User = Depends(get_current_active_user),
    pagination: Dict[str, Any] = Depends(get_pagination_params),
    language: Optional[str] = Query(None, description="编程语言筛选"),
    is_active: Optional[bool] = Query(None, description="是否激活筛选"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取班级作业列表
    """
    try:
        # 权限检查 - 确保用户可以访问该班级
        class_result = await db.execute(select(Class).where(Class.id == class_id))
        class_obj = class_result.scalar_one_or_none()
        
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
        
        # 学生权限检查
        if current_user.role == "student":
            membership_result = await db.execute(
                select(ClassMembership).where(
                    and_(
                        ClassMembership.class_id == class_id,
                        ClassMembership.student_id == current_user.id,
                        ClassMembership.is_active == True
                    )
                )
            )
            if not membership_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        elif current_user.role == "teacher" and str(class_obj.teacher_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # 构建查询条件
        conditions = [Assignment.class_id == class_id]
        
        if language:
            conditions.append(Assignment.language == language)
        if is_active is not None:
            conditions.append(Assignment.is_active == is_active)
        
        # 获取总数
        count_query = select(func.count(Assignment.id)).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 获取分页数据
        query = (
            select(Assignment)
            .where(and_(*conditions))
            .order_by(Assignment.created_at.desc())
            .offset(pagination["offset"])
            .limit(pagination["limit"])
        )
        
        result = await db.execute(query)
        assignments = result.scalars().all()
        
        # 构建响应数据
        assignment_responses = []
        for assignment in assignments:
            # 获取提交数量（这里可以后续优化）
            submission_count = 0  # 暂时设为0，后续添加提交统计
            
            assignment_responses.append(AssignmentListResponse(
                id=str(assignment.id),
                title=assignment.title,
                language=assignment.language,
                difficulty_level=assignment.difficulty_level,
                due_date=assignment.due_date,
                is_active=assignment.is_active,
                submission_count=submission_count,
                created_at=assignment.created_at
            ))
        
        return ResponseModel(
            success=True,
            data=PaginatedResponse(
                items=assignment_responses,
                total=total,
                page=pagination["page"],
                size=pagination["size"],
                pages=(total + pagination["size"] - 1) // pagination["size"]
            ),
            message="Assignments retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve assignments"
        )


@router.post("/classes/{class_id}/assignments", response_model=ResponseModel[AssignmentResponse])
async def create_assignment(
    class_id: str,
    assignment_data: AssignmentCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    创建作业（教师和管理员）
    """
    try:
        # 检查班级是否存在且有权限
        class_result = await db.execute(select(Class).where(Class.id == class_id))
        class_obj = class_result.scalar_one_or_none()
        
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found"
            )
        
        # 教师权限检查
        if current_user.role == "teacher" and str(class_obj.teacher_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # 创建作业
        new_assignment = Assignment(
            class_id=class_id,
            title=assignment_data.title,
            description=assignment_data.description,
            language=assignment_data.language,
            difficulty_level=assignment_data.difficulty_level.value if assignment_data.difficulty_level else None,
            estimated_time=assignment_data.estimated_time,
            due_date=assignment_data.due_date,
            requirements=assignment_data.requirements or {},
            test_cases=assignment_data.test_cases or [],
            grading_rubric=assignment_data.grading_rubric or {},
            is_active=True
        )
        
        db.add(new_assignment)
        await db.commit()
        await db.refresh(new_assignment)
        
        logger.info(f"Assignment created: {new_assignment.title} by {current_user.username}")
        
        return ResponseModel(
            success=True,
            data=AssignmentResponse(
                id=str(new_assignment.id),
                class_id=str(new_assignment.class_id),
                class_name=class_obj.name,
                title=new_assignment.title,
                description=new_assignment.description,
                language=new_assignment.language,
                difficulty_level=new_assignment.difficulty_level,
                estimated_time=new_assignment.estimated_time,
                due_date=new_assignment.due_date,
                requirements=new_assignment.requirements,
                test_cases=new_assignment.test_cases,
                grading_rubric=new_assignment.grading_rubric,
                is_active=new_assignment.is_active,
                submission_count=0,
                created_at=new_assignment.created_at,
                updated_at=new_assignment.updated_at
            ),
            message="Assignment created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating assignment: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create assignment"
        )


@router.get("/assignments/{assignment_id}", response_model=ResponseModel[AssignmentResponse])
async def get_assignment_detail(
    assignment_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取作业详情
    """
    try:
        # 获取作业和班级信息
        assignment_query = select(Assignment, Class.name.label("class_name")).join(
            Class, Assignment.class_id == Class.id
        ).where(Assignment.id == assignment_id)
        
        result = await db.execute(assignment_query)
        assignment_data = result.first()
        
        if not assignment_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )
        
        assignment, class_name = assignment_data
        
        # 权限检查
        if current_user.role == "student":
            # 学生需要是班级成员
            membership_result = await db.execute(
                select(ClassMembership).where(
                    and_(
                        ClassMembership.class_id == assignment.class_id,
                        ClassMembership.student_id == current_user.id,
                        ClassMembership.is_active == True
                    )
                )
            )
            if not membership_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        elif current_user.role == "teacher":
            # 教师需要是班级的教师
            class_result = await db.execute(
                select(Class).where(
                    and_(
                        Class.id == assignment.class_id,
                        Class.teacher_id == current_user.id
                    )
                )
            )
            if not class_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        # 获取提交数量统计
        submission_count = 0  # 暂时设为0，后续添加
        
        return ResponseModel(
            success=True,
            data=AssignmentResponse(
                id=str(assignment.id),
                class_id=str(assignment.class_id),
                class_name=class_name,
                title=assignment.title,
                description=assignment.description,
                language=assignment.language,
                difficulty_level=assignment.difficulty_level,
                estimated_time=assignment.estimated_time,
                due_date=assignment.due_date,
                requirements=assignment.requirements,
                test_cases=assignment.test_cases,
                grading_rubric=assignment.grading_rubric,
                is_active=assignment.is_active,
                submission_count=submission_count,
                created_at=assignment.created_at,
                updated_at=assignment.updated_at
            ),
            message="Assignment details retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving assignment detail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve assignment details"
        )