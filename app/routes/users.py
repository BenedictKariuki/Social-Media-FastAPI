from typing import List
from fastapi import Depends, HTTPException, status, Response, APIRouter
from .. import schemas, utils, models
from sqlalchemy.orm import Session
from ..database import get_db

# router for users - tags are for documentation
router = APIRouter(prefix='/users', tags=['users'])

# get all users
@router.get('/', response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

# get user by id
@router.get('/{id}', response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user with id {id} was not found')
    return user

# create user
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.User, db: Session = Depends(get_db)):
    try:
        # check if user exists
        user_ = db.query(models.User).filter(models.User.email == user.email).first()
        if user_:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This email is already in use!")
        # hash password
        user.password = utils.hash_password(user.password)
        new_user = models.User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except HTTPException as HTTPerror:
        db.rollback()
        raise HTTPerror
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Sorry! An internal server error occurred: {str(error)}")

# delete user
@router.delete('/{id}')
def delete_user(id: int, db: Session = Depends(get_db)):
    try:
        deleted_user_query = db.query(models.User).filter(models.User.id == id)
        if deleted_user_query.first() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user with id {id} was not found')
        deleted_user_query.delete()
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as error:
        db.rollback()
        return {'Error': str(error)}

# update user
@router.put('/{id}', response_model=schemas.UserResponse)
def update_user(id: int, user: schemas.User, db: Session = Depends(get_db)):
    try:
        updated_user_query = db.query(models.User).filter(models.User.id == id)
        updated_user = updated_user_query.first()
        if updated_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user with id {id} was not found')
        updated_user_query.update(user.model_dump())
        db.commit()
        return updated_user
    except Exception as error:
        db.rollback()
        return {'Error': str(error)}