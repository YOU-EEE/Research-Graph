"""模块 D：用户认证路由"""
import hashlib
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User
from schemas import UserCreate, UserOut, UserLogin

router = APIRouter()

# 简单的会话存储（开发用，生产应使用 JWT）
_active_sessions: dict[int, str] = {}


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_current_user(
    x_user_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """从请求头提取当前用户。"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        uid = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user id")
    user = db.query(User).filter(User.user_id == uid).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.post("/login", response_model=UserOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """用户登录。"""
    user = db.query(User).filter(User.username == data.username).first()
    if not user or user.password_hash != _hash_password(data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    _active_sessions[user.user_id] = user.username
    return user


@router.post("/register", response_model=UserOut)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """用户注册。"""
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=data.username,
        password_hash=_hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    """列出所有用户。"""
    return db.query(User).order_by(User.username).all()


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息。"""
    return current_user
