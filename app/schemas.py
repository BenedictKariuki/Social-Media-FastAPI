from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

# creating a pydantic model for Posts
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None

# creating a pydantic model for creating a new post
class CreatePost(Post):
    pass

# create a pydantic model for updating
class UpdatePost(BaseModel):
    title: str
    content: str
    published: bool

# how to send user data to server
class User(BaseModel):
    email: EmailStr
    password: str

# how a user is returned
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    
    class Config:
        from_attributes = True

# create a pydantic model for response
# Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict, but an ORM model (or any other arbitrary object with attributes).
class PostResponse(Post):
    user_id: int
    user: UserResponse

    class Config:
        from_attributes = True

class PostOut(BaseModel):
    Post: PostResponse
    votes: int
  


# how the token is returned
class Token(BaseModel):
    token: str
    token_type: str

# what the token contains
class TokenData(BaseModel):
    id: Optional[int] = None

# how to send a vote/like
class Vote(BaseModel):
    post_id: int
    vote_dir: int