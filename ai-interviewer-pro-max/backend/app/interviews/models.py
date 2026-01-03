"""
Interview Models

SQLAlchemy models for interview-related database tables.
Covers the complete interview lifecycle from setup to report.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Enum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.base import Base


# ===========================================
# ENUMS
# ===========================================


class SessionType(str, enum.Enum):
    """Interview session types."""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    MIXED = "mixed"
    HR = "hr"
    CASE_STUDY = "case_study"
    SYSTEM_DESIGN = "system_design"


class DifficultyLevel(str, enum.Enum):
    """Interview difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class SessionStatus(str, enum.Enum):
    """Interview session status."""
    SCHEDULED = "scheduled"
    CONFIGURING = "configuring"
    PLANNING = "planning"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETING = "completing"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class QuestionType(str, enum.Enum):
    """Interview question types."""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    FOLLOW_UP = "follow_up"
    SYSTEM_DESIGN = "system_design"


# ===========================================
# MODELS
# ===========================================


class Resume(Base):
    """
    Resume model - Stores uploaded resumes and extracted content.
    """
    
    __tablename__ = "resumes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    # TODO: Add ForeignKey: user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, docx
    file_size_bytes = Column(Integer, nullable=False)
    
    extracted_text = Column(Text, nullable=True)
    is_primary = Column(Boolean, default=False)
    upload_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Resume(id={self.id}, file_name={self.file_name})>"


class ResumeAnalysis(Base):
    """
    Resume analysis model - Stores Gemini-generated semantic analysis.
    """
    
    __tablename__ = "resume_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    skills_extracted = Column(JSON, nullable=False, default=list)
    experience_years = Column(String(10), nullable=True)
    education_level = Column(String(50), nullable=True)
    education_details = Column(JSON, nullable=True)
    work_history = Column(JSON, nullable=True)
    certifications = Column(JSON, nullable=True)
    languages = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    strengths = Column(JSON, nullable=True)
    gaps = Column(JSON, nullable=True)
    
    analysis_version = Column(String(20), nullable=False, default="1.0")
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ResumeAnalysis(resume_id={self.resume_id})>"


class ATSScore(Base):
    """
    ATS Score model - Stores ATS compatibility scoring per resume.
    """
    
    __tablename__ = "ats_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    job_role_id = Column(UUID(as_uuid=True), nullable=True)
    
    overall_score = Column(Integer, nullable=False)  # 0-100
    keyword_match_score = Column(Integer, nullable=True)
    format_score = Column(Integer, nullable=True)
    experience_match_score = Column(Integer, nullable=True)
    skills_match_score = Column(Integer, nullable=True)
    education_match_score = Column(Integer, nullable=True)
    
    recommendations = Column(JSON, nullable=True)
    scored_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ATSScore(resume_id={self.resume_id}, score={self.overall_score})>"


class JobRole(Base):
    """
    Job Role model - Defines interview target roles with requirements.
    """
    
    __tablename__ = "job_roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # NULL = system role
    
    title = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # engineering, design, product, etc.
    seniority_level = Column(String(20), nullable=False)  # intern, junior, mid, senior, lead
    industry = Column(String(100), nullable=True)
    required_skills = Column(JSON, nullable=False, default=list)
    description = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<JobRole(title={self.title})>"


class InterviewSession(Base):
    """
    Interview Session model - Core interview instance tracking lifecycle.
    """
    
    __tablename__ = "interview_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    resume_id = Column(UUID(as_uuid=True), nullable=True)
    job_role_id = Column(UUID(as_uuid=True), nullable=True)
    
    session_type = Column(String(20), nullable=False, default="mixed")
    difficulty_level = Column(String(20), nullable=False, default="medium")
    status = Column(String(20), nullable=False, default="configuring")
    
    total_questions = Column(Integer, nullable=False, default=10)
    questions_answered = Column(Integer, default=0)
    time_limit_minutes = Column(Integer, nullable=True)
    actual_duration_seconds = Column(Integer, nullable=True)
    
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<InterviewSession(id={self.id}, status={self.status})>"


class InterviewQuestion(Base):
    """
    Interview Question model - Stores generated questions per session.
    """
    
    __tablename__ = "interview_questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    question_order = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)
    category = Column(String(100), nullable=True)
    difficulty = Column(String(20), nullable=False)
    
    expected_topics = Column(JSON, nullable=True)
    max_score = Column(Integer, default=10)
    time_limit_seconds = Column(Integer, nullable=True)
    
    is_follow_up = Column(Boolean, default=False)
    parent_question_id = Column(UUID(as_uuid=True), nullable=True)
    generated_by = Column(String(20), nullable=False, default="gemini")  # gemini or groq
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<InterviewQuestion(id={self.id}, order={self.question_order})>"


class InterviewAnswer(Base):
    """
    Interview Answer model - Stores user responses to interview questions.
    """
    
    __tablename__ = "interview_answers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    answer_text = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    response_time_seconds = Column(Integer, nullable=True)
    
    is_skipped = Column(Boolean, default=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<InterviewAnswer(question_id={self.question_id})>"


class AnswerEvaluation(Base):
    """
    Answer Evaluation model - Stores AI evaluation of each answer.
    """
    
    __tablename__ = "answer_evaluations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    answer_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Core dimensions (0-10)
    relevance_score = Column(Integer, nullable=False)
    depth_score = Column(Integer, nullable=False)
    clarity_score = Column(Integer, nullable=False)
    confidence_score = Column(Integer, nullable=False)
    
    # Extended dimensions (0-10, nullable)
    technical_accuracy_score = Column(Integer, nullable=True)
    problem_solving_score = Column(Integer, nullable=True)
    
    total_score = Column(Integer, nullable=False)
    max_possible_score = Column(Integer, nullable=False)
    
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    feedback_text = Column(Text, nullable=True)
    
    quick_eval_by = Column(String(20), default="groq")
    deep_eval_by = Column(String(20), default="gemini")
    evaluated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<AnswerEvaluation(answer_id={self.answer_id}, score={self.total_score})>"


class InterviewScore(Base):
    """
    Interview Score model - Aggregate scoring per interview session.
    """
    
    __tablename__ = "interview_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Dimension scores (0-100)
    technical_score = Column(Integer, nullable=True)
    behavioral_score = Column(Integer, nullable=True)
    communication_score = Column(Integer, nullable=False)
    problem_solving_score = Column(Integer, nullable=False)
    confidence_score = Column(Integer, nullable=False)
    engagement_score = Column(Integer, nullable=False)
    
    # Aggregate
    overall_score = Column(Integer, nullable=False)
    percentile_rank = Column(Integer, nullable=True)
    grade = Column(String(5), nullable=False)  # A+, A, B+, etc.
    pass_status = Column(Boolean, nullable=False)
    
    scoring_weights = Column(JSON, nullable=False)
    raw_points_earned = Column(Integer, nullable=False)
    raw_points_possible = Column(Integer, nullable=False)
    
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<InterviewScore(session_id={self.session_id}, overall={self.overall_score})>"


class InterviewReport(Base):
    """
    Interview Report model - Stores comprehensive Gemini-generated report.
    """
    
    __tablename__ = "interview_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    score_id = Column(UUID(as_uuid=True), nullable=False)
    
    report_title = Column(String(255), nullable=False)
    executive_summary = Column(Text, nullable=False)
    performance_breakdown = Column(JSON, nullable=False)
    question_wise_feedback = Column(JSON, nullable=False)
    strengths_summary = Column(JSON, nullable=False)
    improvement_areas = Column(JSON, nullable=False)
    recommended_resources = Column(JSON, nullable=True)
    interview_comparison = Column(JSON, nullable=True)
    
    hiring_recommendation = Column(String(20), nullable=False)  # strong_hire, hire, maybe, no_hire
    next_steps = Column(Text, nullable=True)
    
    report_format_version = Column(String(10), nullable=False, default="1.0")
    generated_by = Column(String(20), default="gemini")
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    is_downloadable = Column(Boolean, default=True)
    pdf_path = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<InterviewReport(session_id={self.session_id})>"


# ===========================================
# TODO: Additional models
# ===========================================

# TODO: TextualSignalAnalysis model for simulated features
# TODO: FeatureSimulation model
# TODO: SessionLog model for audit trail
# TODO: CareerRoadmap model
