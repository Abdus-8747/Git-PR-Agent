import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database.db import Base

class CommitAnalysis(Base):
    __tablename__ = "commit_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repo_name = Column(String(255), nullable=False)
    commit_sha = Column(String(255), nullable=False, unique=True)
    commit_message = Column(Text, nullable=False)
    
    files_changed = Column(JSONB, default=list)
    patches = Column(JSONB, default=list) # Optional: Can store patches if needed, or leave empty if too large
    
    final_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    developer_analysis = relationship("DeveloperAnalysisModel", back_populates="commit_analysis", uselist=False, cascade="all, delete-orphan")
    orchestrator_decision = relationship("OrchestratorDecisionModel", back_populates="commit_analysis", uselist=False, cascade="all, delete-orphan")
    security_review = relationship("SecurityReviewModel", back_populates="commit_analysis", uselist=False, cascade="all, delete-orphan")
    architecture_review = relationship("ArchitectureReviewModel", back_populates="commit_analysis", uselist=False, cascade="all, delete-orphan")
    better_approach_review = relationship("BetterApproachReviewModel", back_populates="commit_analysis", uselist=False, cascade="all, delete-orphan")
    principal_review = relationship("PrincipalReviewModel", back_populates="commit_analysis", uselist=False, cascade="all, delete-orphan")

class DeveloperAnalysisModel(Base):
    __tablename__ = "developer_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commit_analysis_id = Column(UUID(as_uuid=True), ForeignKey("commit_analyses.id"), nullable=False, unique=True)
    
    feature_type = Column(String(255))
    implementation_summary = Column(Text)
    complexity = Column(String(50))
    files_touched = Column(JSONB, default=list)
    potential_issues = Column(JSONB, default=list)

    commit_analysis = relationship("CommitAnalysis", back_populates="developer_analysis")

class OrchestratorDecisionModel(Base):
    __tablename__ = "orchestrator_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commit_analysis_id = Column(UUID(as_uuid=True), ForeignKey("commit_analyses.id"), nullable=False, unique=True)
    
    run_security_review = Column(Boolean, default=False)
    run_architecture_review = Column(Boolean, default=False)
    run_better_approach_review = Column(Boolean, default=False)
    review_depth = Column(String(50))
    reasoning = Column(Text)

    commit_analysis = relationship("CommitAnalysis", back_populates="orchestrator_decision")

class SecurityReviewModel(Base):
    __tablename__ = "security_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commit_analysis_id = Column(UUID(as_uuid=True), ForeignKey("commit_analyses.id"), nullable=False, unique=True)
    
    is_secure = Column(Boolean, default=True)
    vulnerabilities = Column(JSONB, default=list)
    recommendations = Column(JSONB, default=list)
    risk_level = Column(String(50))

    commit_analysis = relationship("CommitAnalysis", back_populates="security_review")

class ArchitectureReviewModel(Base):
    __tablename__ = "architecture_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commit_analysis_id = Column(UUID(as_uuid=True), ForeignKey("commit_analyses.id"), nullable=False, unique=True)
    
    is_solid = Column(Boolean, default=True)
    strengths = Column(JSONB, default=list)
    weaknesses = Column(JSONB, default=list)
    recommendations = Column(JSONB, default=list)

    commit_analysis = relationship("CommitAnalysis", back_populates="architecture_review")

class BetterApproachReviewModel(Base):
    __tablename__ = "better_approach_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commit_analysis_id = Column(UUID(as_uuid=True), ForeignKey("commit_analyses.id"), nullable=False, unique=True)
    
    has_better_approach = Column(Boolean, default=False)
    current_implementation = Column(Text)
    suggested_implementation = Column(Text)
    reasoning = Column(Text)

    commit_analysis = relationship("CommitAnalysis", back_populates="better_approach_review")

class PrincipalReviewModel(Base):
    __tablename__ = "principal_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commit_analysis_id = Column(UUID(as_uuid=True), ForeignKey("commit_analyses.id"), nullable=False, unique=True)
    
    overall_score = Column(Float)
    verdict = Column(Text)
    approval_status = Column(String(50))
    priority_fixes = Column(JSONB, default=list)

    commit_analysis = relationship("CommitAnalysis", back_populates="principal_review")

class DetectedVulnerability(Base):
    __tablename__ = "detected_vulnerabilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commit_analysis_id = Column(UUID(as_uuid=True), ForeignKey("commit_analyses.id"), nullable=False)
    
    description = Column(Text, nullable=False)
    severity = Column(String(50))
    status = Column(String(50), default="Open")

    commit_analysis = relationship("CommitAnalysis", backref="detected_vulnerabilities")

class PriorityFix(Base):
    __tablename__ = "priority_fixes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commit_analysis_id = Column(UUID(as_uuid=True), ForeignKey("commit_analyses.id"), nullable=False)
    
    description = Column(Text, nullable=False)
    status = Column(String(50), default="Pending")

    commit_analysis = relationship("CommitAnalysis", backref="priority_fixes")

class LLMUsageLog(Base):
    __tablename__ = "llm_usage_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commit_analysis_id = Column(UUID(as_uuid=True), ForeignKey("commit_analyses.id"), nullable=False)
    
    agent_name = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)

    commit_analysis = relationship("CommitAnalysis", backref="llm_usage_logs")
