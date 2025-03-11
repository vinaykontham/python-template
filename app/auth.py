from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

router = APIRouter()

@router.get("/secure-data", dependencies=[Depends(verify_token)])
def secure_endpoint():
    return {"message": "Secure Data Accessed"}
