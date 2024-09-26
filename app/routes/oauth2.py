from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
from ..database import get_db
from sqlalchemy.orm import Session
from ..config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

from app import models, schemas
# three pieces of information - secret key(private key), algorithm(HS256), expiration time
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# generate token
def create_token(data: dict):
    to_encode = data.copy()
    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expires_at})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

# verify token
def verify_token(token: str, payload_exception):
    try:
        # decode token sent by user
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # extract the user id from decoded token
        id: str = payload.get("user_id")
        if id is None:
            raise payload_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise payload_exception
    return token_data

# get current user -  we need OAuth2PasswordBearer
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unable to validate credentials", headers={"WWW-Authenticate:": "Bearer"})
    token = verify_token(token, credentials_exception)
    # query the database to get the user this id belongs to
    logged_in_user = db.query(models.User).filter(models.User.id == token.id).first()
    return logged_in_user