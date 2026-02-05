from fastapi import APIRouter,Depends,HTTPException
from app.core.security import get_current_user
from app.schemas.user import UserResponse,UserUpdate
from app.models.user import User
from app.services.user_service import UserService
from sqlalchemy.orm import Session 
from app.dependencies import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me" , response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)) :
    return current_user

@router.patch("/me", response_model=UserResponse)
def update_my_profile(updates:UserUpdate ,
                      current_user:User = Depends(get_current_user), 
                      db: Session = Depends(get_db)) :
    try:
        updated_user = UserService.update_user(db, current_user.id, updates)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{user_id}", response_model=UserResponse)
def get_user_profile(user_id : int , db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user