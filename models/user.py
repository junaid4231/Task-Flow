from app.models.base import BaseModel
from sqlalchemy import Column,Integer,String,Boolean
from sqlalchemy.orm import relationship
class User(BaseModel):
    __tablename__ = "users"
    full_name = Column(String(100), nullable=True)
    username = Column(String(50), nullable=False,index=True, unique=True)
    email = Column(String(100), nullable=False, index=True,unique=True)
    hashed_password = Column(String(255),nullable=False)
    is_active = Column(Boolean , default = True)
    is_superuser = Column(Boolean , default = False)

    organization_memberships = relationship("OrganzationMembers",foreign_keys="OrganizationMember.user_id", back_populates="user", cascade="all, delete-orphan")

