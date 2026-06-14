from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from contextlib import asynccontextmanager

from database import engine, Base, get_db
from models import User, Post, Comment, Like
from schemas import (
    UserCreate, UserOut, Token,
    PostCreate, PostUpdate, PostOut,
    CommentCreate, CommentOut,
    LikeOut
)
from auth import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_active_user, get_current_admin_user
)
from dependencies import get_post_or_404, check_post_owner
from crud import get_post_likes_count, get_post_comments_count
from utils import external_async_task

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Social Media API",
    description="Industry-standard FastAPI for social media posts with JWT auth, async DB, and SDG 8 alignment.",
    version="1.0.0",
    lifespan=lifespan
)

# ---------- ROOT ENDPOINT (welcome message) ----------
@app.get("/")
async def root():
    return {
        "message": "Welcome to Social Media API",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": [
            "/register",
            "/token",
            "/users/me",
            "/posts",
            "/posts/{id}",
            "/posts/{id}/like",
            "/posts/{id}/comments",
            "/sdg"
        ]
    }

# ---------- AUTH ENDPOINTS ----------
@app.post("/register", response_model=UserOut, status_code=201)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.username == user.username))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Username taken")
    existing = await db.execute(select(User).where(User.email == user.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email registered")
    hashed = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, "Incorrect username or password")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# ---------- POST CRUD ----------
@app.post("/posts", response_model=PostOut, status_code=201)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_post = Post(**post.model_dump(), owner_id=current_user.id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    db_post.owner = current_user
    db_post.likes_count = 0
    db_post.comments_count = 0
    return db_post

@app.get("/posts", response_model=List[PostOut])
async def list_posts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).offset(skip).limit(limit))
    posts = result.scalars().all()
    for p in posts:
        owner_res = await db.execute(select(User).where(User.id == p.owner_id))
        p.owner = owner_res.scalar_one()
        p.likes_count = await get_post_likes_count(db, p.id)
        p.comments_count = await get_post_comments_count(db, p.id)
    return posts

@app.get("/posts/{post_id}", response_model=PostOut)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await get_post_or_404(post_id, db)
    owner_res = await db.execute(select(User).where(User.id == post.owner_id))
    post.owner = owner_res.scalar_one()
    post.likes_count = await get_post_likes_count(db, post.id)
    post.comments_count = await get_post_comments_count(db, post.id)
    return post

@app.put("/posts/{post_id}", response_model=PostOut)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    post = await get_post_or_404(post_id, db)
    check_post_owner(post, current_user)
    if post_update.title is not None:
        post.title = post_update.title
    if post_update.content is not None:
        post.content = post_update.content
    await db.commit()
    await db.refresh(post)
    owner_res = await db.execute(select(User).where(User.id == post.owner_id))
    post.owner = owner_res.scalar_one()
    post.likes_count = await get_post_likes_count(db, post.id)
    post.comments_count = await get_post_comments_count(db, post.id)
    return post

@app.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    post = await get_post_or_404(post_id, db)
    check_post_owner(post, current_user)
    await db.delete(post)
    await db.commit()
    return None

# ---------- COMMENTS ----------
@app.post("/posts/{post_id}/comments", response_model=CommentOut, status_code=201)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    await get_post_or_404(post_id, db)
    db_comment = Comment(content=comment.content, post_id=post_id, author_id=current_user.id)
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    owner_res = await db.execute(select(User).where(User.id == current_user.id))
    db_comment.author = owner_res.scalar_one()
    return db_comment

@app.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(404, "Comment not found")
    if comment.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(403, "Not enough permissions")
    await db.delete(comment)
    await db.commit()
    return None

# ---------- LIKES ----------
@app.post("/posts/{post_id}/like", response_model=LikeOut, status_code=201)
async def like_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    await get_post_or_404(post_id, db)
    existing = await db.execute(select(Like).where(Like.post_id == post_id, Like.user_id == current_user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Already liked")
    like = Like(post_id=post_id, user_id=current_user.id)
    db.add(like)
    await db.commit()
    await db.refresh(like)
    return like

@app.delete("/posts/{post_id}/like", status_code=204)
async def unlike_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(Like).where(Like.post_id == post_id, Like.user_id == current_user.id))
    like = result.scalar_one_or_none()
    if not like:
        raise HTTPException(404, "Like not found")
    await db.delete(like)
    await db.commit()
    return None

# ---------- ASYNC I/O DEMO (REQUIREMENT) ----------
@app.get("/posts/{post_id}/analyze")
async def analyze_post_sentiment(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    post = await get_post_or_404(post_id, db)
    result = await external_async_task(post.id, post.content)
    return result

# ---------- ADMIN ONLY ----------
@app.delete("/admin/posts/{post_id}", status_code=204)
async def admin_delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    post = await get_post_or_404(post_id, db)
    await db.delete(post)
    await db.commit()
    return None

# ---------- SDG INFO ----------
@app.get("/sdg")
async def sdg_info():
    return {
        "sdg": "SDG 8 - Decent Work and Economic Growth",
        "sierra_leone_relevance": "Enables youth employment by providing backend for social media platforms, job networking, and skill showcasing.",
        "impact": "Reduces youth unemployment through accessible digital infrastructure."
    }