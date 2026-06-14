from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import Like, Comment, Post, User
from typing import Tuple

async def get_post_likes_count(db: AsyncSession, post_id: int) -> int:
    result = await db.execute(select(func.count(Like.id)).where(Like.post_id == post_id))
    return result.scalar()

async def get_post_comments_count(db: AsyncSession, post_id: int) -> int:
    result = await db.execute(select(func.count(Comment.id)).where(Comment.post_id == post_id))
    return result.scalar()

async def get_post_with_owner(db: AsyncSession, post_id: int) -> Tuple[Post, User]:
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        return None, None
    owner_result = await db.execute(select(User).where(User.id == post.owner_id))
    owner = owner_result.scalar_one()
    return post, owner