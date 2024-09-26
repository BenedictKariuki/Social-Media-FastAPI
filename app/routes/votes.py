from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, models
from . import oauth2

router = APIRouter(prefix='/vote', tags=['Votes'])


@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # check whether post exists
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} was not found")
    
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    # if the user upvotes, check to see whether they've already upvoted
    found_vote = vote_query.first()
    if vote.vote_dir == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='You have already liked this post!')
        new_vote = models.Vote(user_id=current_user.id, post_id=vote.post_id)
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)
        return {"msg":"sucessfully upvoted"}
    # if the user downvotes, check to see whether they've actually upvoted
    elif vote.vote_dir == 0:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You have not like this post")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"msg": "succesfully downvoted"}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vote direction can either be 0 or 1")
    
    