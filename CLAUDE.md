# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains an AI Teaching Assistant System design document (`rfq.md`) for developing an AI-powered educational tool specifically targeting university-level programming courses. The project focuses on creating a comprehensive system to assist teachers with programming course instruction, particularly for C language and Python programming basics.

## Project Architecture

### Core Concept
The system is designed around a multi-agent architecture using Microsoft's AutoGen framework, with specialized AI agents for different aspects of programming education:

- **CodeAnalyzer**: Syntax and logic analysis
- **PedagogyExpert**: Teaching methodology and feedback strategies  
- **StudentProfiler**: Learning pattern analysis and personalization
- **FeedbackGenerator**: Structured educational feedback generation
- **QualityController**: Output validation and quality assurance
- **DebuggingMentor**: Debugging skills instruction

### Target Audience
- **Primary Users**: University computer science instructors teaching programming fundamentals
- **Students**: 18-22 year old university students learning C/Python programming
- **Course Focus**: C Programming, Python Basics, Data Structures & Algorithms

### Key Features Outlined
1. Intelligent code analysis and error detection
2. Personalized, progressive feedback generation
3. Course progress tracking aligned with curriculum standards
4. Multi-language support (C, Python)
5. Teacher dashboard for review and intervention
6. Automated testing and assessment engine

## Technology Stack (Proposed)

- **Backend**: Python + FastAPI + Redis + PostgreSQL
- **AI Framework**: AutoGen + OpenAI API/Local models
- **Frontend**: React + TypeScript + Tailwind CSS
- **Deployment**: Docker + Kubernetes

## Development Phases

1. **Phase 1 MVP** (3-4 months): Single language support, basic feedback system
2. **Phase 2 Enhancement** (2-3 months): Multi-language support, class management
3. **Phase 3 Advanced** (3-4 months): Deep personalization, learning path recommendations

## Document Structure

The main document (`rfq.md`) contains:
- Detailed requirements analysis
- UI/UX design frameworks
- Technical architecture specifications
- AutoGen-based multi-agent system design
- Implementation roadmap with specific code examples
- Performance optimization strategies
- Commercial deployment considerations

This is a design/planning document for an educational technology project rather than an active codebase with runnable code.