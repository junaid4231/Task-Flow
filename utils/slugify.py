import re
from sqlalchemy.orm import Session
from app.models.oragization import Organization

def generate_slug(name: str, db: Session) -> str:
    """
    Generate unique slug from organization name.
    
    Args:
        name: Organization name
        db: Database session
        
    Returns:
        Unique URL-safe slug
        
    Examples:
        "My Startup" → "my-startup"
        "Google Inc!" → "google-inc"
        "My Startup" (exists) → "my-startup-2"
    """
    # Step 1: Create base slug
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
    slug = re.sub(r'[\s]+', '-', slug)     # Replace spaces with hyphens
    slug = slug.strip('-')                  # Remove leading/trailing hyphens
    
    # Step 2: Ensure uniqueness
    original_slug = slug
    counter = 2
    
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{original_slug}-{counter}"
        counter += 1
    
    return slug