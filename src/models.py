"""SQLAlchemy ORM models"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    JSONB,
    ARRAY,
    ForeignKey,
    Index,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.database import Base


class Organization(Base):
    """Enterprise organization"""
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    subscription_plan = Column(String(50), default="free")
    subscription_status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSONB, default={})
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="organization", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="organization", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="organization", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="organization", cascade="all, delete-orphan")
    finetuning_jobs = relationship("FineTuningJob", back_populates="organization", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="organization", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("length(name) >= 3", name="name_length_check"),
        CheckConstraint("slug ~ '^[a-z0-9-]+$'", name="slug_format_check"),
    )


class User(Base):
    """Platform user with RBAC"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="member")
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("org_id", "email", name="unique_org_email"),
        UniqueConstraint("org_id", "username", name="unique_org_username"),
        CheckConstraint("role IN ('admin', 'member', 'viewer', 'api_only')", name="valid_role_check"),
        Index("idx_users_org_id", "org_id"),
        Index("idx_users_email", "email"),
    )


class APIKey(Base):
    """API key for programmatic access"""
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    permissions = Column(ARRAY(String), default=[])
    rate_limit = Column(Integer, default=1000)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="api_keys")
    user = relationship("User", back_populates="api_keys")
    
    __table_args__ = (
        CheckConstraint("rate_limit > 0", name="positive_rate_limit_check"),
        Index("idx_api_keys_org_id", "org_id"),
        Index("idx_api_keys_key_hash", "key_hash"),
    )


class Subscription(Base):
    """Subscription plan and billing"""
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    plan_id = Column(String(50), nullable=False)
    status = Column(String(50), default="active")
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    stripe_subscription_id = Column(String(255), unique=True)
    stripe_customer_id = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="subscriptions")
    invoices = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("current_period_end > current_period_start", name="valid_period_check"),
        Index("idx_subscriptions_org_id", "org_id"),
        Index("idx_subscriptions_stripe_id", "stripe_subscription_id"),
    )


class UsageRecord(Base):
    """Metered usage for billing"""
    __tablename__ = "usage_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(String(50), nullable=False)
    quantity = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    billing_period = Column(String(7), nullable=False, index=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="usage_records")
    
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="non_negative_quantity_check"),
        Index("idx_usage_records_org_id", "org_id"),
        Index("idx_usage_records_billing_period", "billing_period"),
        Index("idx_usage_records_timestamp", "timestamp"),
    )


class Invoice(Base):
    """Generated invoice"""
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    status = Column(String(50), default="draft", index=True)
    subtotal = Column(Float, nullable=False)
    tax = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    line_items = Column(JSONB, default=[])
    stripe_invoice_id = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    due_date = Column(DateTime, nullable=False)
    paid_at = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", back_populates="invoices")
    subscription = relationship("Subscription", back_populates="invoices")
    
    __table_args__ = (
        CheckConstraint("subtotal >= 0 AND tax >= 0 AND total >= 0", name="valid_amounts_check"),
        CheckConstraint("period_end > period_start AND due_date > created_at", name="valid_dates_check"),
        Index("idx_invoices_org_id", "org_id"),
        Index("idx_invoices_status", "status"),
        Index("idx_invoices_stripe_id", "stripe_invoice_id"),
    )


class AuditLog(Base):
    """Security and compliance audit trail"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    event_type = Column(String(100), nullable=False)
    resource = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)
    result = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text)
    metadata = Column(JSONB, default={})
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        Index("idx_audit_logs_org_id", "org_id"),
        Index("idx_audit_logs_timestamp", "timestamp"),
        Index("idx_audit_logs_event_type", "event_type"),
    )


class Conversation(Base):
    """AI conversation with analytics"""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255))
    model_used = Column(String(50), nullable=False)
    messages = Column(JSONB, default=[])
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    sentiment = Column(String(50))
    topics = Column(ARRAY(String), default=[])
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    
    __table_args__ = (
        CheckConstraint("tokens_used >= 0", name="non_negative_tokens_check"),
        CheckConstraint("cost >= 0", name="non_negative_cost_check"),
        Index("idx_conversations_org_id", "org_id"),
        Index("idx_conversations_user_id", "user_id"),
        Index("idx_conversations_created_at", "created_at"),
    )


class FineTuningJob(Base):
    """Fine-tuning job for custom models"""
    __tablename__ = "finetuning_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    model_base = Column(String(100), nullable=False)
    status = Column(String(50), default="queued", index=True)
    training_file_id = Column(String(255), nullable=False)
    validation_file_id = Column(String(255))
    hyperparameters = Column(JSONB, default={})
    result_model_id = Column(String(255))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", back_populates="finetuning_jobs")
    
    __table_args__ = (
        Index("idx_finetuning_jobs_org_id", "org_id"),
        Index("idx_finetuning_jobs_status", "status"),
    )


class Webhook(Base):
    """Webhook registration for events"""
    __tablename__ = "webhooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    webhook_url = Column(String(2048), nullable=False)
    secret = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_triggered_at = Column(DateTime)
    failed_attempts = Column(Integer, default=0)
    
    # Relationships
    organization = relationship("Organization", back_populates="webhooks")
    
    __table_args__ = (
        CheckConstraint("failed_attempts >= 0", name="positive_failed_attempts_check"),
        Index("idx_webhooks_org_id", "org_id"),
        Index("idx_webhooks_event_type", "event_type"),
    )
