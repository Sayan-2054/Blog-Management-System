# src/main.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
import hashlib
from passlib.context import CryptContext
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Blog Management System",
    description="A blog management system with CRUD operations, likes, and comments",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory storage (replace with database in production)
users_db = {}
posts_db = {}
likes_db = {}
comments_db = {}
post_counter = 0
comment_counter = 0

# Pydantic Models
class User(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

class BlogPost(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    author: Optional[str] = None

class BlogPostResponse(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    comments_count: int = 0

class BlogPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)

class Comment(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class CommentResponse(BaseModel):
    id: int
    content: str
    author: str
    post_id: int
    created_at: datetime

class LikeResponse(BaseModel):
    message: str
    likes_count: int

# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    username = decode_access_token(token)
    
    if username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return username

# Authentication endpoints
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: User):
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = hash_password(user.password)
    users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password
    }
    
    return UserResponse(username=user.username, email=user.email)

@app.post("/api/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    if user_login.username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    user_data = users_db[user_login.username]
    if not verify_password(user_login.password, user_data["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_login.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Blog Post CRUD endpoints
@app.post("/api/posts", response_model=BlogPostResponse)
async def create_post(post: BlogPost, current_user: str = Depends(get_current_user)):
    global post_counter
    post_counter += 1
    
    now = datetime.utcnow()
    post_data = {
        "id": post_counter,
        "title": post.title,
        "content": post.content,
        "author": current_user,
        "created_at": now,
        "updated_at": now
    }
    
    posts_db[post_counter] = post_data
    likes_db[post_counter] = set()
    comments_db[post_counter] = []
    
    return BlogPostResponse(
        **post_data,
        likes_count=0,
        comments_count=0
    )

@app.get("/api/posts", response_model=List[BlogPostResponse])
async def get_all_posts():
    result = []
    for post_id, post_data in posts_db.items():
        likes_count = len(likes_db.get(post_id, set()))
        comments_count = len(comments_db.get(post_id, []))
        
        result.append(BlogPostResponse(
            **post_data,
            likes_count=likes_count,
            comments_count=comments_count
        ))
    
    return sorted(result, key=lambda x: x.created_at, reverse=True)

@app.get("/api/posts/{post_id}", response_model=BlogPostResponse)
async def get_post(post_id: int):
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    post_data = posts_db[post_id]
    likes_count = len(likes_db.get(post_id, set()))
    comments_count = len(comments_db.get(post_id, []))
    
    return BlogPostResponse(
        **post_data,
        likes_count=likes_count,
        comments_count=comments_count
    )

@app.put("/api/posts/{post_id}", response_model=BlogPostResponse)
async def update_post(
    post_id: int, 
    post_update: BlogPostUpdate, 
    current_user: str = Depends(get_current_user)
):
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    post_data = posts_db[post_id]
    if post_data["author"] != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    # Update only provided fields
    if post_update.title is not None:
        post_data["title"] = post_update.title
    if post_update.content is not None:
        post_data["content"] = post_update.content
    
    post_data["updated_at"] = datetime.utcnow()
    
    likes_count = len(likes_db.get(post_id, set()))
    comments_count = len(comments_db.get(post_id, []))
    
    return BlogPostResponse(
        **post_data,
        likes_count=likes_count,
        comments_count=comments_count
    )

@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: int, current_user: str = Depends(get_current_user)):
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    post_data = posts_db[post_id]
    if post_data["author"] != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    # Clean up related data
    del posts_db[post_id]
    if post_id in likes_db:
        del likes_db[post_id]
    if post_id in comments_db:
        del comments_db[post_id]
    
    return {"message": "Post deleted successfully"}

# Like functionality
@app.post("/api/posts/{post_id}/like", response_model=LikeResponse)
async def like_post(post_id: int, current_user: str = Depends(get_current_user)):
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post_id not in likes_db:
        likes_db[post_id] = set()
    
    if current_user in likes_db[post_id]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already liked this post"
        )
    
    likes_db[post_id].add(current_user)
    likes_count = len(likes_db[post_id])
    
    return LikeResponse(
        message="Post liked successfully",
        likes_count=likes_count
    )

@app.delete("/api/posts/{post_id}/like")
async def unlike_post(post_id: int, current_user: str = Depends(get_current_user)):
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post_id not in likes_db or current_user not in likes_db[post_id]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You haven't liked this post"
        )
    
    likes_db[post_id].remove(current_user)
    likes_count = len(likes_db[post_id])
    
    return LikeResponse(
        message="Post unliked successfully",
        likes_count=likes_count
    )

# Comment functionality
@app.post("/api/posts/{post_id}/comment", response_model=CommentResponse)
async def add_comment(
    post_id: int, 
    comment: Comment, 
    current_user: str = Depends(get_current_user)
):
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    global comment_counter
    comment_counter += 1
    
    comment_data = {
        "id": comment_counter,
        "content": comment.content,
        "author": current_user,
        "post_id": post_id,
        "created_at": datetime.utcnow()
    }
    
    if post_id not in comments_db:
        comments_db[post_id] = []
    
    comments_db[post_id].append(comment_data)
    
    return CommentResponse(**comment_data)

@app.get("/api/posts/{post_id}/comments", response_model=List[CommentResponse])
async def get_comments(post_id: int):
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    comments = comments_db.get(post_id, [])
    return [CommentResponse(**comment) for comment in comments]

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
