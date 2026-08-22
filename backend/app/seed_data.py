"""
Creates the six tables (if they don't exist) and loads initial data
for the CRM system.

Run with:  python -m app.seed_data
Safe to re-run: it skips rows that already exist.

NOTE: Against a real SQL Server (DB_MODE=mssql) the six tables are
expected to already exist with production data — you would not
normally run this seeder there, or you'd adapt it into a controlled
migration.
"""
from datetime import date

from .database import Base, engine, SessionLocal
from .models import (
    LoginMaster,
    CustomerDetail,
    ProductCategoryMaster,
    ProductMaster,
    IronOreSpecificationMaster,
    IronPelletSpecificationMaster,
)
from .auth import hash_password


def seed():
    # Note: Tables already exist in MSSQL - no need to create_all
    db = SessionLocal()
    try:
        # ---- Customer ----
        # Skip customer seeding - customers are managed through the UI
        print("  Customer records are managed through the application")

        # ---- Login ----
        # Login credentials are already in the database - do not modify
        # Users and their names are kept as they are in the DB
        print("  Login users are managed in the database")

        # ---- Categories ----
        # Update existing categories with correct status (True/False -> 1/0)
        categories = [
            (1, "Mines", 1),
            (2, "Pellet", 1),
            (3, "Iron Ore Fines", 0),
        ]
        for cat_id, name, status in categories:
            existing_cat = db.query(ProductCategoryMaster).filter_by(ProductCatID=cat_id).first()
            if existing_cat:
                # Update status if needed
                existing_cat.PStatus = status
            else:
                db.add(ProductCategoryMaster(ProductCatID=cat_id, ProductCategory=name, PStatus=status))

        # ---- Products ----
        # Real product data from the database (13000000 series)
        products = [
            ("13000000", "LOW CCS IRON ORE PELLET", "2", 1),
            ("13000001", "Unscreened Accretion", "2", 1),
            ("13000002", "IRON ORE PELLET FE 63", "2", 1),
            ("13000003", "IRON ORE PELLET FE 65", "2", 1),
            ("13000004", "Iron Ore Pellet chips 3-8 mm Fe 60-65%", "2", 1),
            ("13000005", "Iron Ore Fines FE 51-55%", "1", 1),
            ("13000006", "Iron Ore Fines FE 55-58%", "1", 1),
            ("13000007", "Iron Ore Fines FE 58-60%", "1", 1),
            ("13000008", "Iron Ore Fines FE 60-62%", "1", 1),
            ("13000009", "Iron Ore Fines FE 62-65%", "1", 1),
            ("13000010", "Iron Ore Fines FE 65-100%", "1", 1),
            ("13000011", "Iron Ore Lumps FE 51-55%", "1", 1),
            ("13000012", "Iron Ore Lumps FE 55-58%", "1", 1),
            ("13000026", "Iron Ore Lumps FE 58-60%", "1", 1),
            ("13000027", "Iron Ore Lumps FE 60-62%", "1", 1),
            ("13000028", "Iron Ore Lumps FE 62-65%", "1", 1),
            ("13000029", "Iron Ore Lumps FE 65-100%", "1", 1),
            ("13000037", "IRON ORE LOW PHOSS PELLET FE 63", "2", 1),
            ("13000040", "65% Fe High CCS", "2", 1),
            ("13000049", "Iron Ore Fines Below 57.99% Fe", "1", 1),
            ("13000052", "IRON ORE PELLET NORMAL PHOS FE 63 (IOG)", "2", 1),
            ("13000054", "IRON ORE PELLET NP FE 63 (IOGS & IOBP)", "2", 1),
            ("13000055", "Over size pellets (4mm to 24mm)", "2", 1),
            ("13000056", "Accretion (+24mm to +40mm)", "2", 1),
            ("13000058", "Iron Ore Lumps Below 57.99% Fe", "1", 1),
        ]
        for pid, name, cat, status in products:
            existing = db.get(ProductMaster, pid)
            if existing:
                # Update existing product   
                existing.ProductName = name
                existing.ProductCategory = cat
                existing.PStatus = status
            else:
                # Add new product
                db.add(ProductMaster(
                    PID=pid, ProductName=name, ProductCategory=cat,
                    PStatus=status, EntryDate=date(2025, 1, 15), EntryBy="admin",
                ))

        db.flush()

        # ---- Iron Ore specs ----
        # Remove old sample specs and add real specs
        db.query(IronOreSpecificationMaster).delete()
        
        iron_ore_specs = [
            # PID 13000006 - Iron Ore Fines FE 55-58%
            (13000006, "Iron (Fe)", "58±1", "N/FP/2593/2024-25/3F", 1),
            (13000006, "Alumina (Al2O3)", "2.8 MAX", "N/FP/2593/2024-25/3F", 1),
            (13000006, "Silica (SiO2)", "12 MAX", "N/FP/2593/2024-25/3F", 1),
            (13000006, "Sulphur (S)", "0.02 MAX", "N/FP/2593/2024-25/3F", 1),
            (13000006, "Phosphorous (P)", "0.045 MAX", "N/FP/2593/2024-25/3F", 1),
            (13000006, "Manganese (Mn)", "0.04 MAX", "N/FP/2593/2024-25/3F", 1),
            (13000006, "Size", "-10 mm", "N/FP/2593/2024-25/3F", 1),
            (13000006, "Above 10 mm", "3 % MAX", "N/FP/2593/2024-25/3F", 1),
            (13000006, "Below 10 mm", "97 % MIN", "N/FP/2593/2024-25/3F", 1),
            # PID 13000026 - Iron Ore Lumps FE 58-60%
            (13000026, "Iron (Fe)", "60±1", "N/FP/2593/2024-25/2L", 1),
            (13000026, "Alumina (Al2O3)", "3 % MAX", "N/FP/2593/2024-25/2L", 1),
            (13000026, "Silica (SiO2)", "6.5 % MAX", "N/FP/2593/2024-25/2L", 1),
            (13000026, "Sulphur (S)", "0.02 MAX", "N/FP/2593/2024-25/2L", 1),
        ]
        
        for pid, param, spec, lot, group in iron_ore_specs:
            db.add(IronOreSpecificationMaster(
                PID=pid, Parameter=param, Specification=spec,
                EntryBy="lab", EntryDate=date(2026, 1, 5), LotNo=lot, Group=group,
            ))

        # ---- Iron Pellet specs ----
        # Remove old sample specs and add real specs
        db.query(IronPelletSpecificationMaster).delete()
        
        iron_pellet_specs = [
            # PID 13000002 - IRON ORE PELLET FE 63
            (13000002, "CCS (Kg/Pellet)", "200 +/- 20", "Physical", 1),
            (13000002, "Size Analysis (%)", "None", "Physical", 1),
            (13000002, "> 16 mm/broken pellet/accretion", "5 Max.", "Physical", 1),
            (13000002, "6 to 16 mm", "> 90", "Physical", 1),
            (13000002, "< 6 mm/broken pellets", "3 Max", "Physical", 1),
            (13000002, "Mean Particle Size in mm", "11 +/- 1", "Physical", 1),
            (13000002, "Tumble Index (%)", "> 94", "Physical", 1),
            (13000002, "Abrasion Index (%)", "< 5", "Physical", 1),
            (13000002, "Porosity (%)", "> 25", "Physical", 1),
            (13000002, "Moisture (%)", "2.5 max. in dry season", "Physical", 1),
            (13000002, "None", "5 max in rainy season", "Physical", 1),
            (13000002, "Bulk Density (in T/m3)", "2.1", "Physical", 1),
            (13000002, "1) Fe", "63 +", "Chemical", 1),
            (13000002, "2) FeO", "0.20 Max", "Chemical", 1),
            (13000002, "3) SiO2 + Al2O3", "8 +/- 0.5", "Chemical", 1),
            (13000002, "4) Phosphorous", "0.065 Max", "Chemical", 1),
            (13000002, "6) Sulphur", "< 0.012", "Chemical", 1),
            (13000002, "7) Cao", "0.80 +/- 0.10", "Chemical", 1),
            (13000002, "8) MgO", "0.20 +/- 0.05", "Chemical", 1),
            (13000002, "9) Mn", "0.25 Max.", "Chemical", 1),
        ]
        
        for pid, param, spec, ptype, group in iron_pellet_specs:
            db.add(IronPelletSpecificationMaster(
                PID=pid, Parameter=param, TestingStandard="", Specification=spec,
                EntryBy="lab", EntryDate=date(2026, 1, 5), PType=ptype, Group=group,
            ))

        db.commit()
        print("✓ Seed complete. Real production data loaded.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
