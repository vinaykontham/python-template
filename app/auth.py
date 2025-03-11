from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme)):
    if not token or not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

def is_valid_token(token: str) -> bool:
    # Implement token validation logic here
    return True  # Placeholder for actual validation logic


@router.get("/secure-data", dependencies=[Depends(verify_token)])
def secure_endpoint():
    return {"message": "Secure Data Accessed"}
