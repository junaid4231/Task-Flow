from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Organization(BaseModel):
    """Organization/Workspace model"""
    __tablename__ = "organizations"
    
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    plan = Column(String(20), default="free", nullable=False)
    settings = Column(JSON, nullable=True, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    members = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan"
    )