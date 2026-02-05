from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class OrganizationMember(BaseModel):
    """Junction table for User-Organization many-to-many"""
    __tablename__ = "organization_members"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), default="member", nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    invited_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="organization_memberships")
    organization = relationship("Organization", back_populates="members")
    invited_by = relationship("User", foreign_keys=[invited_by_id])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'organization_id', name='unique_user_org'),
    )