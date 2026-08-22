from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CustomerDetail, LoginMaster
from ..schemas import CustomerOut
from ..auth import get_current_user

router = APIRouter(prefix="/api/customer", tags=["customer"])


@router.get("/me", response_model=CustomerOut)
def get_my_customer_details(
    current_user: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns ONLY the customer record linked to the authenticated login.
    There is no path in this API to request another customer's CID.
    """
    if not current_user.CID:
        raise HTTPException(
            status_code=404,
            detail="No customer account is linked to this login. Please contact support.",
        )

    customer = db.get(CustomerDetail, current_user.CID)
    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Your customer record could not be found in the current CRM database.",
        )
    return customer
