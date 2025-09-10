"""
AI教学助手系统 - 邮件服务
提供异步邮件发送功能

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from ..core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM or settings.SMTP_USERNAME
        
        # 设置Jinja2模板环境
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        发送邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML内容
            text_content: 纯文本内容
            attachments: 附件列表
            
        Returns:
            bool: 是否发送成功
        """
        if not self.smtp_server or not self.username or not self.password:
            logger.warning("Email configuration is incomplete. Skipping email sending.")
            return False
        
        try:
            # 创建邮件消息
            message = MIMEMultipart('alternative')
            message['From'] = self.from_email
            message['To'] = to_email
            message['Subject'] = subject
            
            # 添加文本内容
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                message.attach(text_part)
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)
            
            # 添加附件（如果有）
            if attachments:
                for attachment in attachments:
                    # 这里可以添加附件处理逻辑
                    pass
            
            # 发送邮件
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=True,
                username=self.username,
                password=self.password,
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def render_template(self, template_name: str, **kwargs) -> str:
        """
        渲染邮件模板
        
        Args:
            template_name: 模板文件名
            **kwargs: 模板变量
            
        Returns:
            str: 渲染后的HTML内容
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            logger.error(f"Failed to render email template {template_name}: {str(e)}")
            return ""


# 全局邮件服务实例
email_service = EmailService()


async def send_password_reset_email(email: str, name: str, reset_token: str) -> bool:
    """
    发送密码重置邮件
    
    Args:
        email: 用户邮箱
        name: 用户姓名
        reset_token: 重置令牌
        
    Returns:
        bool: 是否发送成功
    """
    try:
        # 构建重置链接
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        
        # 渲染邮件模板
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>密码重置</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-bottom: 20px;">AI教学助手 - 密码重置</h2>
                
                <p style="color: #666; line-height: 1.6;">
                    您好 {name}，
                </p>
                
                <p style="color: #666; line-height: 1.6;">
                    您收到这封邮件是因为您（或其他人）请求重置您的AI教学助手账户密码。
                </p>
                
                <p style="color: #666; line-height: 1.6;">
                    请点击下面的链接重置您的密码：
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">重置密码</a>
                </div>
                
                <p style="color: #666; line-height: 1.6; font-size: 14px;">
                    如果按钮无法点击，请复制以下链接到浏览器地址栏：<br>
                    <a href="{reset_link}" style="color: #007bff;">{reset_link}</a>
                </p>
                
                <p style="color: #666; line-height: 1.6; font-size: 14px;">
                    此链接将在1小时后过期。如果您没有请求重置密码，请忽略此邮件。
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    此邮件由AI教学助手系统自动发送，请勿回复。
                </p>
            </div>
        </body>
        </html>
        """
        
        # 纯文本版本
        text_content = f"""
        AI教学助手 - 密码重置
        
        您好 {name}，
        
        您收到这封邮件是因为您（或其他人）请求重置您的AI教学助手账户密码。
        
        请访问以下链接重置您的密码：
        {reset_link}
        
        此链接将在1小时后过期。如果您没有请求重置密码，请忽略此邮件。
        
        此邮件由AI教学助手系统自动发送，请勿回复。
        """
        
        # 发送邮件
        return await email_service.send_email(
            to_email=email,
            subject="AI教学助手 - 密码重置",
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        return False


async def send_welcome_email(email: str, name: str, username: str) -> bool:
    """
    发送欢迎邮件
    
    Args:
        email: 用户邮箱
        name: 用户姓名
        username: 用户名
        
    Returns:
        bool: 是否发送成功
    """
    try:
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>欢迎使用AI教学助手</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-bottom: 20px;">欢迎使用AI教学助手！</h2>
                
                <p style="color: #666; line-height: 1.6;">
                    您好 {name}，
                </p>
                
                <p style="color: #666; line-height: 1.6;">
                    欢迎加入AI教学助手平台！您的账户已成功创建。
                </p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0; color: #666;">
                        <strong>您的账户信息：</strong><br>
                        用户名：{username}<br>
                        邮箱：{email}
                    </p>
                </div>
                
                <p style="color: #666; line-height: 1.6;">
                    您现在可以开始使用AI教学助手来提升编程学习体验。我们的AI系统将为您提供：
                </p>
                
                <ul style="color: #666; line-height: 1.6;">
                    <li>智能代码分析和反馈</li>
                    <li>个性化学习建议</li>
                    <li>调试指导和提示</li>
                    <li>学习进度跟踪</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/login" style="background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">立即开始学习</a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    此邮件由AI教学助手系统自动发送，请勿回复。
                </p>
            </div>
        </body>
        </html>
        """
        
        return await email_service.send_email(
            to_email=email,
            subject="欢迎使用AI教学助手",
            html_content=html_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {str(e)}")
        return False


async def send_feedback_notification_email(
    teacher_email: str, 
    teacher_name: str, 
    student_name: str, 
    assignment_title: str,
    overall_score: float
) -> bool:
    """
    发送反馈通知邮件给教师
    
    Args:
        teacher_email: 教师邮箱
        teacher_name: 教师姓名
        student_name: 学生姓名
        assignment_title: 作业标题
        overall_score: 总体评分
        
    Returns:
        bool: 是否发送成功
    """
    try:
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>AI反馈已生成</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-bottom: 20px;">AI教学反馈通知</h2>
                
                <p style="color: #666; line-height: 1.6;">
                    您好 {teacher_name}，
                </p>
                
                <p style="color: #666; line-height: 1.6;">
                    AI教学助手已为学生提交的作业生成了详细的反馈：
                </p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0; color: #666;">
                        <strong>学生：</strong> {student_name}<br>
                        <strong>作业：</strong> {assignment_title}<br>
                        <strong>AI评分：</strong> {overall_score:.1f}/100
                    </p>
                </div>
                
                <p style="color: #666; line-height: 1.6;">
                    您可以登录系统查看完整的AI分析报告和反馈内容。
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/dashboard" style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">查看反馈</a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    此邮件由AI教学助手系统自动发送，请勿回复。
                </p>
            </div>
        </body>
        </html>
        """
        
        return await email_service.send_email(
            to_email=teacher_email,
            subject=f"AI反馈已生成 - {student_name} 的 {assignment_title}",
            html_content=html_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send feedback notification email to {teacher_email}: {str(e)}")
        return False


# 导出
__all__ = [
    "EmailService",
    "email_service",
    "send_password_reset_email",
    "send_welcome_email", 
    "send_feedback_notification_email"
]