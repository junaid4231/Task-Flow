import re
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from app.models.oragization import Organization
from app.models.organizationmember import OrganizationMember
from app.models.user import User
from app.schemas.organizations import OrganizationCreate, OrganizationUpdate
from app.utils import slugify



class OrganizationService:
    """Business logic for organization management"""
    
    @staticmethod
    def create_organization(
        db: Session,
        org_data: OrganizationCreate,
        owner_id: int
    ) -> Organization:
        """
        Create a new organization and add creator as owner.
        
        Args:
            db: Database session
            org_data: Organization data from client
            owner_id: User ID of creator (becomes owner)
            
        Returns:
            Created organization
            
        Raises:
            ValueError: If organization creation fails
        """
        # Generate unique slug
        slug = slugify(org_data.name, db)
        
        # Create organization
        org = Organization(
            name=org_data.name,
            slug=slug,
            description=org_data.description
        )
        
        db.add(org)
        db.flush()  # Get org.id without committing
        
        # Add creator as owner
        member = OrganizationMember(
            user_id=owner_id,
            organization_id=org.id,
            role="owner",
            invited_by_id=None
        )
        
        db.add(member)
        db.commit()
        db.refresh(org)
        
        return org
    
    @staticmethod
    def get_user_organizations(
        db: Session,
        user_id: int
    ) -> List[Tuple[Organization, str]]:
        """
        Get all organizations a user belongs to.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of tuples: (Organization, role)
        """
        results = db.query(
            Organization,
            OrganizationMember.role
        ).join(
            OrganizationMember,
            Organization.id == OrganizationMember.organization_id
        ).filter(
            OrganizationMember.user_id == user_id,
            Organization.is_active == True
        ).all()
        
        return results
    
    @staticmethod
    def get_organization_by_slug(
        db: Session,
        slug: str
    ) -> Optional[Organization]:
        """
        Get organization by slug.
        
        Args:
            db: Database session
            slug: Organization slug
            
        Returns:
            Organization or None if not found
        """
        return db.query(Organization).filter(
            Organization.slug == slug,
            Organization.is_active == True
        ).first()
    
    @staticmethod
    def get_user_role_in_org(
        db: Session,
        user_id: int,
        org_id: int
    ) -> Optional[str]:
        """
        Get user's role in organization.
        
        Args:
            db: Database session
            user_id: User ID
            org_id: Organization ID
            
        Returns:
            Role string or None if not a member
        """
        membership = db.query(OrganizationMember).filter(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == org_id
        ).first()
        
        return membership.role if membership else None
    
    @staticmethod
    def update_organization(
        db: Session,
        org_id: int,
        updates: OrganizationUpdate
    ) -> Organization:
        """
        Update organization fields.
        
        Args:
            db: Database session
            org_id: Organization ID
            updates: Fields to update
            
        Returns:
            Updated organization
            
        Raises:
            ValueError: If organization not found
        """
        # Get organization
        org = db.query(Organization).filter(
            Organization.id == org_id
        ).first()
        
        if not org:
            raise ValueError(f"Organization with id {org_id} not found")
        
        # Get only provided fields
        update_data = updates.model_dump(exclude_unset=True)
        
        # Update each field
        for key, value in update_data.items():
            setattr(org, key, value)
        
        # Save changes
        db.commit()
        db.refresh(org)
        
        return org
    
    @staticmethod
    def delete_organization(
        db: Session,
        org_id: int
    ) -> bool:
        """
        Delete organization (soft delete - set is_active=False).
        
        Args:
            db: Database session
            org_id: Organization ID
            
        Returns:
            True if deleted
            
        Raises:
            ValueError: If organization not found
        """
        org = db.query(Organization).filter(
            Organization.id == org_id
        ).first()
        
        if not org:
            raise ValueError(f"Organization with id {org_id} not found")
        
        # Soft delete
        org.is_active = False
        db.commit()
        
        return True
    
    @staticmethod
    def add_member(
        db: Session,
        org_id: int,
        email: str,
        role: str,
        invited_by_id: int
    ) -> OrganizationMember:
        """
        Add a member to organization.
        
        Args:
            db: Database session
            org_id: Organization ID
            email: Email of user to add
            role: Role for user
            invited_by_id: User ID of inviter
            
        Returns:
            Created membership
            
        Raises:
            ValueError: If user not found, already member, or invalid role
        """
        # Validate role
        valid_roles = ["owner", "admin", "member", "guest"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        # Find user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError(f"User with email {email} not found")
        
        # Check not already member
        existing = db.query(OrganizationMember).filter(
            OrganizationMember.user_id == user.id,
            OrganizationMember.organization_id == org_id
        ).first()
        
        if existing:
            raise ValueError(f"{email} is already a member of this organization")
        
        # Create membership
        member = OrganizationMember(
            user_id=user.id,
            organization_id=org_id,
            role=role,
            invited_by_id=invited_by_id
        )
        
        db.add(member)
        db.commit()
        db.refresh(member)
        
        return member
    
    @staticmethod
    def remove_member(
        db: Session,
        org_id: int,
        user_id: int
    ) -> bool:
        """
        Remove a member from organization.
        
        Args:
            db: Database session
            org_id: Organization ID
            user_id: User ID to remove
            
        Returns:
            True if removed
            
        Raises:
            ValueError: If not a member or trying to remove owner
        """
        # Find the membership
        membership = db.query(OrganizationMember).filter(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == org_id
        ).first()
        
        if not membership:
            raise ValueError("User is not a member of this organization")
        
        # Check if owner
        if membership.role == "owner":
            raise ValueError("Cannot remove organization owner. Transfer ownership first.")
        
        # Delete membership
        db.delete(membership)
        db.commit()
        
        return True
    
    @staticmethod
    def update_member_role(
        db: Session,
        org_id: int,
        user_id: int,
        new_role: str
    ) -> OrganizationMember:
        """
        Update member's role in organization.
        
        Args:
            db: Database session
            org_id: Organization ID
            user_id: User ID
            new_role: New role for user
            
        Returns:
            Updated membership
            
        Raises:
            ValueError: If not a member or invalid role
        """
        # Validate role
        valid_roles = ["owner", "admin", "member", "guest"]
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        # Find membership
        membership = db.query(OrganizationMember).filter(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == org_id
        ).first()
        
        if not membership:
            raise ValueError("User is not a member of this organization")
        
        # Update role
        membership.role = new_role
        db.commit()
        db.refresh(membership)
        
        return membership
    
    @staticmethod
    def get_organization_members(
        db: Session,
        org_id: int
    ) -> List[Tuple[User, OrganizationMember]]:
        """
        Get all members of an organization.
        
        Args:
            db: Database session
            org_id: Organization ID
            
        Returns:
            List of tuples: (User, OrganizationMember)
        """
        results = db.query(User, OrganizationMember).join(
            OrganizationMember,
            User.id == OrganizationMember.user_id
        ).filter(
            OrganizationMember.organization_id == org_id
        ).order_by(
            OrganizationMember.joined_at.desc()
        ).all()
        
        return results
    
    @staticmethod
    def get_member_count(db: Session, org_id: int) -> int:
        """
        Get count of members in organization.
        
        Args:
            db: Database session
            org_id: Organization ID
            
        Returns:
            Member count
        """
        return db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == org_id
        ).count()