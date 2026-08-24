from typing import Optional, List, Any
from datetime import date
from pydantic import BaseModel


# ---------- Auth ----------
class LoginRequest(BaseModel):
    user_id: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_name: Optional[str] = None
    user_role: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_company: Optional[str] = None
    responsible_seller: Optional[str] = None


# ---------- Customer ----------
class CustomerOut(BaseModel):
    CID: str
    CustomerName: Optional[str] = None
    Street1: Optional[str] = None
    Street2: Optional[str] = None
    Street3: Optional[str] = None
    Street4: Optional[str] = None
    Location: Optional[str] = None
    City: Optional[str] = None
    Country: Optional[str] = None
    State: Optional[str] = None
    PostalCode: Optional[str] = None
    ContactPerson: Optional[str] = None
    Mobile: Optional[str] = None
    Telephone: Optional[str] = None
    Email: Optional[str] = None
    CustomerCode: Optional[str] = None
    CustomerGroup: Optional[str] = None
    GSTNo: Optional[str] = None
    PANNo: Optional[str] = None
    Company_Code: Optional[str] = None
    Currency: Optional[str] = None
    Sales_office: Optional[str] = None
    Sales_Group: Optional[str] = None
    Status: Optional[int] = None  # INTEGER in actual DB: 1=Active, 0=Inactive

    model_config = {"from_attributes": True}


# ---------- Product ----------
class ProductOut(BaseModel):
    PID: str
    ProductName: Optional[str] = None
    ProductCategory: Optional[str] = None
    CategoryName: Optional[str] = None
    PStatus: Optional[int] = None  # INTEGER (BIT): 1=Active, 0=Inactive
    EntryDate: Optional[date] = None
    EntryBy: Optional[str] = None

    model_config = {"from_attributes": True}


class ProductCategoryOut(BaseModel):
    ProductCatID: int  # INTEGER in actual DB
    ProductCategory: Optional[str] = None
    PStatus: Optional[int] = None  # INTEGER (BIT): 1=Active, 0=Inactive

    model_config = {"from_attributes": True}


# ---------- Specifications ----------
class IronOreSpecOut(BaseModel):
    SID: int
    PID: Optional[int] = None  # INTEGER in actual DB
    Parameter: Optional[str] = None
    Specification: Optional[str] = None
    LotNo: Optional[str] = None
    Group: Optional[int] = None  # INTEGER in actual DB
    EntryDate: Optional[date] = None

    model_config = {"from_attributes": True}


class IronPelletSpecOut(BaseModel):
    SID: int
    PID: Optional[int] = None  # INTEGER in actual DB
    Parameter: Optional[str] = None
    TestingStandard: Optional[str] = None
    Specification: Optional[str] = None
    PType: Optional[str] = None
    Group: Optional[int] = None  # INTEGER in actual DB
    EntryDate: Optional[date] = None

    model_config = {"from_attributes": True}


# ---------- Chat ----------
class ChatRequest(BaseModel):
    message: str
    action: Optional[str] = None  # optional explicit one-click action id


class ChatResponse(BaseModel):
    reply: str
    intent: str
    data: Optional[Any] = None
    suggested_actions: Optional[List[str]] = None


# ---------- Complaint ----------
class ComplaintIn(BaseModel):
    category_type: Optional[str] = None
    description: str
    po_number: Optional[str] = None
    dispatch_date: Optional[str] = None


class ComplaintOut(BaseModel):
    ComplaintID: str
    CategoryType: Optional[str] = None
    ComplaintDescription: Optional[str] = None
    PONumber: Optional[str] = None
    DispatchDate: Optional[date] = None
    RootCauseAnalysis: Optional[str] = None
    CorrectivePreventiveAction: Optional[str] = None
    MarketingReview: Optional[str] = None
    MarketingReviewDate: Optional[date] = None
    PlantHeadReview: Optional[str] = None
    PlantHeadReviewDate: Optional[date] = None
    HODReview: Optional[str] = None
    Solution: Optional[str] = None
    Status: Optional[str] = None
    CreatedBy: Optional[str] = None
    CreatedDate: Optional[date] = None
    UpdatedBy: Optional[str] = None
    UpdatedDate: Optional[date] = None

    model_config = {"from_attributes": True}


class ComplaintReviewIn(BaseModel):
    complaint_id: str
    review_type: str  # "marketing", "plant_head", or "hod"
    approval_status: str  # "approved", "rejected", or "under_review"
    review_comments: Optional[str] = None  # Comments from the reviewer


class ComplaintSolutionGenerateIn(BaseModel):
    complaint_id: str
    root_cause_analysis: str
    corrective_preventive_action: str


class NotificationOut(BaseModel):
    notification_id: str
    title: str
    message: str
    status: str

    model_config = {"from_attributes": True}
