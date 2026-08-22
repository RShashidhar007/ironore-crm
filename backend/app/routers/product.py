from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    ProductMaster,
    ProductCategoryMaster,
    IronOreSpecificationMaster,
    IronPelletSpecificationMaster,
    LoginMaster,
)
from ..schemas import ProductOut, ProductCategoryOut, IronOreSpecOut, IronPelletSpecOut
from ..auth import get_current_user

router = APIRouter(prefix="/api", tags=["products"])


def _get_product_category(db: Session, product: ProductMaster) -> Optional[str]:
    """Manually look up product category by ID (ProductCategory is stored as string int)."""
    if not product.ProductCategory:
        return None
    try:
        cat_id = int(product.ProductCategory)
        category = db.get(ProductCategoryMaster, cat_id)
        return category.ProductCategory if category else None
    except (ValueError, TypeError):
        return None


@router.get("/categories", response_model=List[ProductCategoryOut])
def list_categories(
    active_only: bool = Query(True),
    _: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(ProductCategoryMaster)
    if active_only:
        q = q.filter(ProductCategoryMaster.PStatus == 1)
    return q.all()


@router.get("/products", response_model=List[ProductOut])
def list_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    active_only: bool = Query(False),
    _: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(ProductMaster)
    if category:
        q = q.filter(ProductMaster.ProductCategory == category)
    if search:
        like = f"%{search}%"
        q = q.filter(
            (ProductMaster.ProductName.ilike(like)) | (ProductMaster.PID.ilike(like))
        )
    if active_only:
        q = q.filter(ProductMaster.PStatus == 1)

    results = []
    for p in q.all():
        cat_name = _get_product_category(db, p)
        results.append(ProductOut(
            PID=p.PID, ProductName=p.ProductName, ProductCategory=p.ProductCategory,
            CategoryName=cat_name, PStatus=p.PStatus, EntryDate=p.EntryDate, EntryBy=p.EntryBy,
        ))
    return results


@router.get("/products/{pid}", response_model=ProductOut)
def get_product(
    pid: str,
    _: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = db.get(ProductMaster, pid)
    if not p:
        return ProductOut(PID=pid, ProductName=None, PStatus=None)
    cat_name = _get_product_category(db, p)
    return ProductOut(
        PID=p.PID, ProductName=p.ProductName, ProductCategory=p.ProductCategory,
        CategoryName=cat_name, PStatus=p.PStatus, EntryDate=p.EntryDate, EntryBy=p.EntryBy,
    )


@router.get("/specs/iron-ore", response_model=List[IronOreSpecOut])
def get_iron_ore_specs(
    pid: Optional[str] = None,
    parameter: Optional[str] = None,
    lot_no: Optional[str] = None,
    _: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(IronOreSpecificationMaster)
    if pid:
        q = q.filter(IronOreSpecificationMaster.PID == pid)
    if parameter:
        q = q.filter(IronOreSpecificationMaster.Parameter.ilike(f"%{parameter}%"))
    if lot_no:
        q = q.filter(IronOreSpecificationMaster.LotNo == lot_no)
    return q.all()


@router.get("/specs/iron-pellet", response_model=List[IronPelletSpecOut])
def get_iron_pellet_specs(
    pid: Optional[str] = None,
    parameter: Optional[str] = None,
    _: LoginMaster = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(IronPelletSpecificationMaster)
    if pid:
        q = q.filter(IronPelletSpecificationMaster.PID == pid)
    if parameter:
        q = q.filter(IronPelletSpecificationMaster.Parameter.ilike(f"%{parameter}%"))
    return q.all()
