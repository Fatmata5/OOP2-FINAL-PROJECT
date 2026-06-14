from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    role: str
    created_at: datetime
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str = Field(..., max_length=200)
    content: str

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class PostOut(PostBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    owner: UserOut
    likes_count: int = 0
    comments_count: int = 0
    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentOut(CommentBase):
    id: int
    post_id: int
    author_id: int
    created_at: datetime
    author: UserOut
    class Config:
        from_attributes = True

class LikeOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None