"""
ORM models mapping 1:1 onto the six existing tables in Customer_DB.

IMPORTANT: These models describe the CURRENT schema only. Do not add
transactional tables (Orders, Inventory, Quotations, Dispatch,
Complaints) here until they actually exist in the database — the rest
of the application is written to explicitly say those features are
"not yet available" rather than assume they exist.

QUOTATION_MASTER: Now added to track customer quotation requests with pricing history.
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship

from .database import Base


class LoginMaster(Base):
    __tablename__ = "Login_Master"

    SLNO = Column(Integer, primary_key=True, autoincrement=True)
    User_Id = Column(String(10), unique=True, nullable=False)
    Password = Column(String(1000), nullable=False)  # stored as a bcrypt hash, never plaintext
    User_Name = Column(String(150))
    User_Email = Column(String(150))
    User_HOD = Column(String(50))
    User_Role = Column(String(20))
    User_Status = Column(Integer, default=1)  # bit field: 1=Active, 0=Inactive
    Created_By = Column(String(50))
    Created_Date = Column(Date)
    Updated_By = Column(String(50))
    Updated_Date = Column(Date)
    MobileNo = Column(String(50))
    Department = Column(Integer)
    ResponsibleSeller = Column(String(50))
    CID = Column(String(50))  # Link to Customer_Detail - may not exist in actual DB


class CustomerDetail(Base):
    __tablename__ = "Customer_Detail"

    CID = Column(String(50), primary_key=True)
    CustomerName = Column(String(250), nullable=False)
    Street1 = Column(String(50))
    Street2 = Column(String(50))
    Street3 = Column(String(50))
    Street4 = Column(String(50))
    Location = Column(String(50))
    City = Column(String(50))
    Country = Column(String(50))
    State = Column(String(50))
    PostalCode = Column(String(6))
    ContactPerson = Column(String(250))
    Fax = Column(String(250))
    Mobile = Column(String(50))
    Telephone = Column(String(50))
    Email = Column(String(250))
    CustomerCode = Column(String(50))
    CustomerGroup = Column(String(50))
    GSTNo = Column(String(50))
    PANNo = Column(String(50))
    Company_Code = Column(String(50))
    Currency = Column(String(50))
    Sales_office = Column(String(50))
    Sales_Group = Column(String(50))
    Status = Column(Integer, default=1)  # INTEGER in actual DB: 1=Active, 0=Inactive


class ProductCategoryMaster(Base):
    __tablename__ = "ProductCategory_Master"

    ProductCatID = Column(Integer, primary_key=True, autoincrement=True)
    ProductCategory = Column(String(50), nullable=False)
    PStatus = Column(Integer, default=1)  # BIT: 1=Active, 0=Inactive


class ProductMaster(Base):
    __tablename__ = "Product_Master"

    PID = Column(String(50), primary_key=True)
    ProductName = Column(String(50), nullable=False)
    ProductCategory = Column(String(50))  # Stores integer ID as string
    PStatus = Column(Integer, default=1)  # BIT: 1=Active, 0=Inactive
    EntryDate = Column(Date)
    EntryBy = Column(String(50))


class IronOreSpecificationMaster(Base):
    __tablename__ = "IronOreSpecification_Master"

    SID = Column(Integer, primary_key=True, autoincrement=True)
    PID = Column(Integer)  # INTEGER in actual DB
    Parameter = Column(String(50))
    Specification = Column(String(50))
    EntryBy = Column(String(50))
    EntryDate = Column(Date)
    LotNo = Column(String(50))
    Group = Column("Group", Integer)  # INTEGER in actual DB


class IronPelletSpecificationMaster(Base):
    __tablename__ = "IronPelletSpecification_Master"

    SID = Column(Integer, primary_key=True, autoincrement=True)
    PID = Column(Integer)  # INTEGER in actual DB
    Parameter = Column(String(50))
    TestingStandard = Column(String(50))
    Specification = Column(String(50))
    EntryBy = Column(String(50))
    EntryDate = Column(Date)
    PType = Column(String(50))
    Group = Column("Group", Integer)  # INTEGER in actual DB


class InventoryMaster(Base):
    __tablename__ = "Inventory_Master"

    InventoryID = Column(Integer, primary_key=True, autoincrement=True)
    PID = Column(String(50), ForeignKey("Product_Master.PID"))
    Category = Column(String(100))  # "Produced" or "Sold"
    QuantityMT = Column(Float)  # Quantity in Metric Tons (MT) - stored as DECIMAL(18,2) in DB
    ProducedDate = Column(Date)
    InitialPrice = Column(Float)  # Price per MT (in currency) - stored as DECIMAL(18,2) in DB
    SellingPrice = Column(Float)  # Price per MT (in currency) - stored as DECIMAL(18,2) in DB


class ComplaintMaster(Base):
    __tablename__ = "Complaints_Master"

    CID = Column(Integer, primary_key=True, autoincrement=True)
    ComplaintID = Column(String(50), unique=True, nullable=False)
    CategoryType = Column(String(100))
    ComplaintDescription = Column(String(1000))
    PONumber = Column(String(100))
    DispatchDate = Column(Date)
    RootCauseAnalysis = Column(String(2000))
    RootCauseAnalysisDate = Column(DateTime)
    CorrectivePreventiveAction = Column(String(2000))
    CorrectivePreventiveActionDate = Column(DateTime)
    MarketingReview = Column(String(1000))  # Stores "approved"/"rejected"/"under_review" or review comments
    MarketingReviewDate = Column(DateTime)
    PlantHeadReview = Column(String(1000))  # Stores "approved"/"rejected"/"under_review" or review comments
    PlantHeadReviewDate = Column(DateTime)
    HODReview = Column(String(100))
    HODReviewDate = Column(DateTime)
    Solution = Column(String(2000))  # AI-generated solution based on all reviews
    Status = Column(String(50), default='Under Review')  # Complaint status
    CreatedBy = Column(String(100))
    CreatedDate = Column(DateTime, nullable=False)
    UpdatedBy = Column(String(100))
    UpdatedDate = Column(DateTime)


class QuotationMaster(Base):
    __tablename__ = "Quotations_Master"

    QuotationID = Column(Integer, primary_key=True, autoincrement=True)
    QuotationNumber = Column(String(50), unique=True, nullable=False)  # e.g., QT-2026-08-001
    CID = Column(String(50), ForeignKey("Customer_Detail.CID"))
    PID = Column(String(50), ForeignKey("Product_Master.PID"))
    ProductName = Column(String(250))
    QuantityMT = Column(Float)  # Quantity requested in Metric Tons
    PricePerMT = Column(Float)  # Quoted price per MT
    TotalAmount = Column(Float)  # QuantityMT * PricePerMT
    ValidityDays = Column(Integer, default=7)  # Quote validity period
    Notes = Column(Text)  # Additional notes/terms
    Status = Column(String(50), default='Generated')  # Generated, Accepted, Rejected, Expired
    CreatedBy = Column(String(100))
    CreatedDate = Column(DateTime, nullable=False)
    ExpiryDate = Column(DateTime)
    AcceptedDate = Column(DateTime)
    PDFFilePath = Column(String(500))  # Path to generated PDF
    UpdatedBy = Column(String(100))
    UpdatedDate = Column(DateTime)
