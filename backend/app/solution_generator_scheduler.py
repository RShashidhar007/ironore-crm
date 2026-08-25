"""
Background scheduler to automatically generate solutions for complaints
that are marked as 'Ready_For_Solution_Generation' by the database trigger.

This runs periodically and calls the API to generate solutions.
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import ComplaintMaster
from .routers.complaint import regenerate_solution_if_conditions_met

logger = logging.getLogger(__name__)


class SolutionGeneratorScheduler:
    """
    Scheduler that automatically regenerates solutions for complaints
    when all conditions are met.
    """
    
    def __init__(self, check_interval_seconds: int = 30):
        """
        Initialize the scheduler.
        
        Args:
            check_interval_seconds: How often to check for complaints needing solutions
        """
        self.check_interval = check_interval_seconds
        self.running = False
    
    async def start(self):
        """Start the scheduler loop."""
        self.running = True
        logger.info(f"Solution Generator Scheduler started (check interval: {self.check_interval}s)")
        
        while self.running:
            try:
                await self.check_and_generate_solutions()
            except Exception as e:
                logger.error(f"Error in solution generator scheduler: {str(e)}")
            
            # Wait before next check
            await asyncio.sleep(self.check_interval)
    
    async def stop(self):
        """Stop the scheduler loop."""
        self.running = False
        logger.info("Solution Generator Scheduler stopped")
    
    async def check_and_generate_solutions(self):
        """
        Check for complaints that need solution generation and regenerate them.
        """
        db: Optional[Session] = None
        try:
            db = SessionLocal()
            
            # Find all complaints with:
            # 1. Non-empty MarketingReview
            # 2. Non-empty PlantHeadReview
            # 3. Non-empty RootCauseAnalysis
            # 4. Non-empty CorrectivePreventiveAction
            # 5. Empty or null Solution
            complaints = db.query(ComplaintMaster).filter(
                ComplaintMaster.MarketingReview != None,
                ComplaintMaster.MarketingReview != '',
                ComplaintMaster.PlantHeadReview != None,
                ComplaintMaster.PlantHeadReview != '',
                ComplaintMaster.RootCauseAnalysis != None,
                ComplaintMaster.RootCauseAnalysis != '',
                ComplaintMaster.CorrectivePreventiveAction != None,
                ComplaintMaster.CorrectivePreventiveAction != '',
                (ComplaintMaster.Solution == None) | (ComplaintMaster.Solution == '')
            ).all()
            
            if complaints:
                logger.info(f"Found {len(complaints)} complaints ready for solution generation")
                
                for complaint in complaints:
                    try:
                        # Try to regenerate solution
                        success = regenerate_solution_if_conditions_met(complaint)
                        
                        if success:
                            logger.info(f"Solution generated for {complaint.ComplaintID}")
                        else:
                            logger.debug(f"Conditions not met for {complaint.ComplaintID}")
                    
                    except Exception as e:
                        logger.error(f"Error generating solution for {complaint.ComplaintID}: {str(e)}")
                
                # Commit all changes
                db.commit()
        
        except Exception as e:
            logger.error(f"Error checking for solutions: {str(e)}")
            if db:
                db.rollback()
        
        finally:
            if db:
                db.close()


# Global scheduler instance
_scheduler: Optional[SolutionGeneratorScheduler] = None


async def start_solution_generator():
    """Start the solution generator scheduler in background."""
    global _scheduler
    
    if _scheduler is None:
        _scheduler = SolutionGeneratorScheduler(check_interval_seconds=30)
    
    # Create task to run in background without blocking
    asyncio.create_task(_scheduler.start())


async def stop_solution_generator():
    """Stop the solution generator scheduler."""
    global _scheduler
    
    if _scheduler:
        await _scheduler.stop()
        _scheduler = None


def get_scheduler() -> Optional[SolutionGeneratorScheduler]:
    """Get the current scheduler instance."""
    global _scheduler
    return _scheduler
