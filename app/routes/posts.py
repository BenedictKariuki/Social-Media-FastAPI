from typing import List, Optional
from fastapi import Depends, HTTPException, status, Response, APIRouter
from .. import schemas, models
from sqlalchemy.orm import Session
from ..database import get_db
from . import oauth2
from sqlalchemy import func

# router for posts - tags are for documentation
router = APIRouter(prefix='/posts', tags=['Posts'])

# get all posts
@router.get('/', response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), limit: int = 10, offset: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(offset).all()
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(offset).all()
    return results

# get a spcific post
@router.get('/{id}', response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    result = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found")
    return result

# create new post route
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.CreatePost, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
        # new_post = cursor.fetchone()
        # conn.commit()
        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You do not have an account.")
        new_post = models.Post(user_id=current_user.id, **post.model_dump())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except Exception as error:
        db.rollback()
        return {'Error ': str(error)}

# delete a post
@router.delete('/{id}')
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
        # deleted_post = cursor.fetchone()
        deleted_post_query = db.query(models.Post).filter(models.Post.id == id)
        deleted_post = deleted_post_query.first()
        if deleted_post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found")
        # delete only posts you created
        if deleted_post.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't delete this post!")
        deleted_post_query.delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as error:
        db.rollback()
        return {'Error': str(error)}
   
# update a post
@router.put('/{id}', response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.UpdatePost, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    try:
        # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, id))
        # updated_post = cursor.fetchone()
        updated_post_query = db.query(models.Post).filter(models.Post.id == id)
        updated_post = updated_post_query.first()
        if updated_post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} was not found')
        # update only the posts you created
        if updated_post.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't update this post!")
        updated_post_query.update(post.model_dump(), synchronize_session=False)
        db.commit()
        return updated_post_query.first()
    except Exception as error:
        db.rollback()
        raise error
    