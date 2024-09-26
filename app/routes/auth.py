from fastapi import APIRouter, Depends, HTTPException, status
from .. import schemas, models, utils
from sqlalchemy.orm import Session
from ..database import get_db
from . import oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(tags=['Authentication'])

# login user
@router.post('/login', response_model=schemas.Token)
def login_user(payload: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        # OAuth2PasswordRequestForm returns a dict with two properties - username, password
        # it expects the payload to be in the form data, not in the body
        user = db.query(models.User).filter(models.User.email == payload.username).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
        # check password
        if not utils.verify_password(payload.password, user.password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
        # generate token
        token = oauth2.create_token(data={'user_id': user.id})
        return {'token': token, 'token_type': 'bearer'}
    except Exception as error:
        return {'Error': error}
