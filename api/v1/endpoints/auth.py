from fastapi import APIRouter,Depends,HTTPException
from app.dependencies import get_db
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate,UserResponse,UserLogin,LoginResponse
from app.services.user_service import UserService
from app.core.security import create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/auth" ,
    tags=["Authentication"]
)

@router.post("/register" , response_model=UserResponse , status_code=201)
def register(user_data: UserCreate,db : Session = Depends(get_db)):
    try:
        user = UserService.register_user(db=db,userdata=user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/login", response_model=LoginResponse , status_code= 200)
def login(user_data: UserLogin ,db : Session = Depends(get_db)):
    try:
        user=UserService.authenticate_user(db=db,userdata=user_data)
        token=create_access_token({"sub": str(user.id)})
        return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# ✅ NEW: OAuth2-compatible endpoint - accepts form data
@router.post("/token", response_model=LoginResponse, status_code=200)
def token_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2-compatible login (for Swagger UI authorization)"""
    try:
        # Convert form data to UserLogin schema
        user_login = UserLogin(
            email=form_data.username,  # OAuth2 uses 'username' field
            password=form_data.password
        )
        
        user = UserService.authenticate_user(db=db, userdata=user_login)
        token = create_access_token({"sub": str(user.id)})
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))