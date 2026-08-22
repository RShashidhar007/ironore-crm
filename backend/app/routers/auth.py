from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import LoginMaster, CustomerDetail
from ..schemas import LoginRequest, LoginResponse
from ..auth import verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(LoginMaster).filter(LoginMaster.User_Id == payload.user_id).first()

    # Deliberately generic error for both "no such user" and "wrong password"
    # so the API never reveals which part was incorrect.
    generic_error = "Invalid user ID or password. Please check your credentials and try again."

    if not user or not verify_password(payload.password, user.Password):
        raise HTTPException(status_code=401, detail=generic_error)

    if not user.User_Status or user.User_Status == 0:
        raise HTTPException(
            status_code=403,
            detail="This account is inactive. Please contact support for assistance.",
        )

    # Get customer details if CID is linked
    customer_name = None
    customer_company = None
    if user.CID:
        customer = db.query(CustomerDetail).filter(CustomerDetail.CID == user.CID).first()
        if customer:
            customer_name = customer.CustomerName
            customer_company = customer.CustomerName

    token = create_access_token({"sub": user.User_Id})
    return LoginResponse(
        access_token=token,
        user_name=user.User_Name or user.User_Id,
        user_role=user.User_Role,
        customer_id=user.CID,
        customer_name=customer_name,
        customer_company=customer_company,
        responsible_seller=user.ResponsibleSeller,
    )
