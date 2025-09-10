-- AI Teaching Assistant System Database Initialization Script
-- PostgreSQL初始化脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- 创建开发数据库（如果不存在）
SELECT 'CREATE DATABASE ai_teacher_dev'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ai_teacher_dev')\gexec

-- 创建测试数据库（如果不存在）
SELECT 'CREATE DATABASE ai_teacher_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ai_teacher_test')\gexec

-- 创建数据库用户（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'ai_teacher') THEN
        CREATE USER ai_teacher WITH PASSWORD 'dev_password_123';
    END IF;
END
$$;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE ai_teacher_dev TO ai_teacher;
GRANT ALL PRIVILEGES ON DATABASE ai_teacher_test TO ai_teacher;

-- 连接到开发数据库
\c ai_teacher_dev;

-- 授予schema权限
GRANT ALL ON SCHEMA public TO ai_teacher;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ai_teacher;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ai_teacher;

-- 设置默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ai_teacher;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ai_teacher;

-- 创建基础表结构（如果使用SQLAlchemy，这些会被覆盖）
-- 但提供基础结构作为参考

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_teacher BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 课程表
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    language VARCHAR(50) NOT NULL, -- 'python', 'c', etc.
    difficulty_level VARCHAR(20) DEFAULT 'beginner',
    teacher_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 代码提交表
CREATE TABLE IF NOT EXISTS code_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES users(id),
    course_id UUID REFERENCES courses(id),
    assignment_id UUID,
    code_content TEXT NOT NULL,
    language VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI反馈表
CREATE TABLE IF NOT EXISTS ai_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    submission_id UUID REFERENCES code_submissions(id),
    feedback_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX IF NOT EXISTS idx_code_submissions_student_id ON code_submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_code_submissions_course_id ON code_submissions(course_id);
CREATE INDEX IF NOT EXISTS idx_ai_feedback_submission_id ON ai_feedback(submission_id);

-- 创建触发器更新updated_at字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为相关表创建触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_code_submissions_updated_at BEFORE UPDATE ON code_submissions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入初始数据
INSERT INTO users (email, username, full_name, hashed_password, is_teacher, is_superuser) 
VALUES ('admin@aiteacher.local', 'admin', 'System Administrator', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', TRUE, TRUE)
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (email, username, full_name, hashed_password, is_teacher) 
VALUES ('teacher@aiteacher.local', 'teacher', 'Demo Teacher', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', TRUE)
ON CONFLICT (email) DO NOTHING;

INSERT INTO users (email, username, full_name, hashed_password, is_teacher) 
VALUES ('student@aiteacher.local', 'student', 'Demo Student', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', FALSE)
ON CONFLICT (email) DO NOTHING;

-- 创建示例课程
INSERT INTO courses (name, description, language, teacher_id)
SELECT 
    'Python基础编程',
    'Python编程语言基础课程，适合初学者',
    'python',
    u.id
FROM users u 
WHERE u.username = 'teacher'
AND NOT EXISTS (SELECT 1 FROM courses WHERE name = 'Python基础编程');

INSERT INTO courses (name, description, language, teacher_id)
SELECT 
    'C语言程序设计',
    'C语言编程基础，包括语法、数据结构等',
    'c',
    u.id
FROM users u 
WHERE u.username = 'teacher'
AND NOT EXISTS (SELECT 1 FROM courses WHERE name = 'C语言程序设计');

-- 确保权限正确设置
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ai_teacher;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ai_teacher;

COMMIT;