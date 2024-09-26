from . import models
from .database import engine
from .routes import posts, users, auth, votes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# create database tables based on the models you have created
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(votes.router)

# base route   
@app.get('/')
def root():
    return {'message': 'Welcome to our platform'}




    
