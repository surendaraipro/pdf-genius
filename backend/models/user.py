"""
User model for authentication and subscription management
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship

from ..core.database import Base

class SubscriptionTier:
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    
    # Subscription info
    subscription_tier = Column(
        String, 
        default=SubscriptionTier.FREE,
        nullable=False
    )
    subscription_status = Column(String, default="active")  # active, canceled, expired
    stripe_customer_id = Column(String, unique=True, index=True)
    stripe_subscription_id = Column(String, unique=True, index=True)
    
    # Usage tracking
    conversions_used = Column(Integer, default=0)
    ai_questions_used = Column(Integer, default=0)
    last_reset_date = Column(DateTime, default=datetime.utcnow)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    files = relationship("PDFFile", back_populates="owner")
    api_keys = relationship("APIKey", back_populates="user")
    
    def get_limits(self):
        """Get usage limits based on subscription tier"""
        limits = {
            SubscriptionTier.FREE: {
                "conversions": 10,
                "ai_questions": 5,
                "max_file_size_mb": 10,
                "api_access": False,
                "team_members": 1,
            },
            SubscriptionTier.PRO: {
                "conversions": 100,
                "ai_questions": 50,
                "max_file_size_mb": 50,
                "api_access": True,
                "team_members": 1,
            },
            SubscriptionTier.BUSINESS: {
                "conversions": 500,
                "ai_questions": 250,
                "max_file_size_mb": 100,
                "api_access": True,
                "team_members": 5,
            },
            SubscriptionTier.ENTERPRISE: {
                "conversions": 2000,
                "ai_questions": 1000,
                "max_file_size_mb": 500,
                "api_access": True,
                "team_members": 20,
            }
        }
        return limits.get(self.subscription_tier, limits[SubscriptionTier.FREE])
    
    def can_perform_conversion(self):
        """Check if user can perform a conversion"""
        limits = self.get_limits()
        return self.conversions_used < limits["conversions"]
    
    def can_ask_ai_question(self):
        """Check if user can ask an AI question"""
        limits = self.get_limits()
        return self.ai_questions_used < limits["ai_questions"]
    
    def increment_conversion(self):
        """Increment conversion count"""
        self.conversions_used += 1
    
    def increment_ai_question(self):
        """Increment AI question count"""
        self.ai_questions_used += 1
    
    def reset_usage_if_needed(self):
        """Reset usage counters if it's a new month"""
        now = datetime.utcnow()
        if now.month != self.last_reset_date.month or now.year != self.last_reset_date.year:
            self.conversions_used = 0
            self.ai_questions_used = 0
            self.last_reset_date = now
            return True
        return False

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    user_id = Column(Integer, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

class PDFFile(Base):
    __tablename__ = "pdf_files"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer)  # in bytes
    page_count = Column(Integer)
    storage_path = Column(String, nullable=False)
    
    # Metadata
    title = Column(String)
    author = Column(String)
    subject = Column(String)
    
    # Processing info
    processed_text = Column(String)  # Extracted text for AI chat
    text_hash = Column(String)  # Hash of processed text for caching
    
    # Ownership
    user_id = Column(Integer, index=True, nullable=False)
    is_public = Column(Boolean, default=False)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Relationships
    owner = relationship("User", back_populates="files")
    chat_sessions = relationship("ChatSession", back_populates="pdf_file")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    pdf_file_id = Column(String, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    
    # Chat context
    messages = Column(String)  # JSON string of chat history
    summary = Column(String)
    
    # Usage tracking
    token_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pdf_file = relationship("PDFFile", back_populates="chat_sessions")