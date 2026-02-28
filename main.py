# ===== IMPORTS =====
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# ===== CREATE APP FIRST =====
app = FastAPI()

# ===== CONFIG =====
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

# ===== JWT SETUP =====
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

# ===== ROUTES =====

@app.post("/analyze")
def analyze_contract(
    current_user: str = Depends(get_current_user)
):
    return {
        "analysis": f"Protected route working for user: {current_user}"
    }