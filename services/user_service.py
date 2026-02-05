from app.schemas.user import UserCreate,UserLogin,UserResponse,UserUpdate
from sqlalchemy.orm import Session
from app.models.user import User
from passlib.context import CryptContext
from typing import Optional
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class UserService():
    @staticmethod
    def register_user(db: Session , userdata: UserCreate) -> User:
        existing_email = db.query(User).filter(User.email == userdata.email).first()
        if existing_email:
            raise ValueError("Email Already exists") 
        existing_username = db.query(User).filter(User.username == userdata.username).first()
        if existing_username:
            raise ValueError("Username Already exists")

        hashed_password=pwd_context.hash(userdata.password)
        user_create_dict=userdata.model_dump(exclude={"password"})
        user_create_dict["hashed_password"]=hashed_password
        user = User(**user_create_dict)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def authenticate_user(db:Session , userdata:UserLogin) -> User:
        user = db.query(User).filter(User.email == userdata.email).first()
        if not user:
            raise ValueError("Email or Password Incorrect")
        if not pwd_context.verify(userdata.password,user.hashed_password):
           raise ValueError("Email or Password Incorrect")
        return user
        
    @staticmethod
    def get_user_by_id(db: Session , user_id: int ) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    
    @staticmethod
    def get_user_by_email(db: Session , email: str ) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
        
    @staticmethod
    def update_user(db: Session, user_id: int, updates: UserUpdate):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        update_data = updates.model_dump(exclude_unset=True)

        if "email" in update_data:
            existing = db.query(User).filter(
                User.email == update_data["email"],
                User.id != user_id
            ).first()
            if existing:
                raise ValueError("Email already registered")

        if "username" in update_data:
            existing = db.query(User).filter(
                User.username == update_data["username"],
                User.id != user_id
            ).first()
            if existing:
                raise ValueError("Username already exists")

        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()        # 🔥 THIS is what you were missing
        db.refresh(user)  # optional but good practice

        return user

    
