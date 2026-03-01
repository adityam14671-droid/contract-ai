# ===== IMPORTS =====
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta

# ===== APP =====
app = FastAPI()

# ===== CONFIG =====
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ===== PASSWORD HASHING =====
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    # bcrypt supports max 72 bytes
    password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)

# ===== FAKE DATABASE =====
users_db = {}

# ===== MODELS =====
class UserCreate(BaseModel):
    email: str
    password: str

# ===== TOKEN FUNCTION =====
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ===== SIGNUP =====
@app.post("/signup")
def signup(user: UserCreate):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    users_db[user.email] = {
        "email": user.email,
        "password": hash_password(user.password),
    }

    return {"message": "User created successfully"}

# ===== LOGIN (FOR SWAGGER OAUTH2) =====
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = users_db.get(form_data.username)

    if not db_user or not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": form_data.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ===== JWT PROTECTION =====
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return email

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ===== PROTECTED ROUTE =====
@app.post("/analyze")
def analyze_contract(current_user: str = Depends(get_current_user)):
    return {
        "analysis": f"Protected route working for user: {current_user}"
    }