from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Organization Name")
    description: Optional[str] = Field(None, max_length=500, description="OPtional Description")

class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    plan: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    member_count: Optional[int] = None
    current_user_role: Optional[str] = None

    class Config:
        from_attributes = True
# the schema for update organization
class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    settings: Optional[dict] = None

class MemberADD(BaseModel):
    email: EmailStr = Field(..., description="Email of user to add")
    role: str = Field(default="member", description="Role in organization")


class MemberResponse(BaseModel):
    """
    Schema for returning organization member data.
    """
    user_id: int
    username: str
    email: str
    role: str
    joined_at: datetime
    invited_by: Optional[str] = None  # Username of inviter
    
    class Config:
        from_attributes = True

class MemberUpdate(BaseModel):
    """
    Schema for updating member role.
    """
    role: str = Field(..., description="New role for member")

