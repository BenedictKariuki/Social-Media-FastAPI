from passlib.context import CryptContext

# create password hashing context
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# return a hashed password
def hash_password(password: str):
    return pwd_context.hash(password)

# verufy password
def verify_password(raw_password, hashed_password):
    return pwd_context.verify(raw_password, hashed_password)