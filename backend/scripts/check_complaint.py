import sys
sys.path.insert(0, '/projects/ironore-crm/backend')
from app.database import SessionLocal
from app.models import ComplaintMaster

db = SessionLocal()
c = db.query(ComplaintMaster).filter(ComplaintMaster.ComplaintID == 'CMP-20260825-0003').first()
if c:
    has_marketing = bool(c.MarketingReview and str(c.MarketingReview).strip())
    has_plant = bool(c.PlantHeadReview and str(c.PlantHeadReview).strip())
    has_rca = bool(c.RootCauseAnalysis and str(c.RootCauseAnalysis).strip())
    has_capa = bool(c.CorrectivePreventiveAction and str(c.CorrectivePreventiveAction).strip())
    has_solution = bool(c.Solution and str(c.Solution).strip())
    
    print('CMP-20260825-0003 Status:')
    print(f'Marketing: {has_marketing}')
    print(f'Plant: {has_plant}')
    print(f'RCA: {has_rca}')
    print(f'CAPA: {has_capa}')
    print(f'Solution: {has_solution}')
    print(f'Updated: {c.UpdatedDate}')
    print(f'Status: {c.Status}')
    print()
    print('All 4 fields filled:', has_marketing and has_plant and has_rca and has_capa)
    print('Ready for generation:', has_marketing and has_plant and has_rca and has_capa and not has_solution)
else:
    print('Complaint not found')
db.close()
