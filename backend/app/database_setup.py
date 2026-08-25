"""
Automatic database setup on startup
Creates triggers, stored procedures, and tables automatically
No manual SQL scripts needed
"""
import logging
from sqlalchemy import text, exc
from .database import SessionLocal

logger = logging.getLogger(__name__)


def execute_sql_safe(db, sql_statement, description):
    """Safely execute SQL statement"""
    try:
        # Split by GO and execute each part separately
        statements = sql_statement.split('\nGO\n')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and not stmt.upper().startswith('--'):
                db.execute(text(stmt))
        db.commit()
        logger.info(f"✓ {description}")
        return True
    except exc.SQLAlchemyError as e:
        logger.warning(f"⚠ {description}: {str(e)[:80]}")
        db.rollback()
        return False
    except Exception as e:
        logger.warning(f"⚠ {description}: {str(e)[:80]}")
        db.rollback()
        return False


def setup_database_components():
    """
    Automatically set up all database components on startup
    - Creates trigger
    - Creates stored procedure
    - Creates logging table
    - Creates view
    """
    db = SessionLocal()
    try:
        logger.info("Starting automatic database setup...")
        
        # Create log table first (needed by trigger)
        create_log_table_sql = """
        IF NOT EXISTS (SELECT * FROM sys.objects WHERE type = 'U' AND name = 'SolutionGenerationLog')
        BEGIN
            CREATE TABLE SolutionGenerationLog (
                LogID INT PRIMARY KEY IDENTITY(1,1),
                ComplaintID NVARCHAR(50),
                TriggerTime DATETIME,
                Action NVARCHAR(500),
                CreatedAt DATETIME DEFAULT GETDATE()
            );
        END
        """
        execute_sql_safe(db, create_log_table_sql, "SolutionGenerationLog table")
        
        # Drop old trigger if exists
        try:
            db.execute(text("IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_Complaints_TriggerSolutionGeneration') DROP TRIGGER TR_Complaints_TriggerSolutionGeneration"))
            db.commit()
        except:
            db.rollback()
        
        # Drop old procedure if exists
        try:
            db.execute(text("IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_MarkComplaintReadyForSolution') DROP PROCEDURE sp_MarkComplaintReadyForSolution"))
            db.commit()
        except:
            db.rollback()
        
        # Create stored procedure
        create_proc_sql = """
        CREATE PROCEDURE sp_MarkComplaintReadyForSolution
            @ComplaintID NVARCHAR(50)
        AS
        BEGIN
            SET NOCOUNT ON;
            
            UPDATE Complaints_Master
            SET 
                Solution = NULL,
                Status = 'Ready_For_Solution_Generation',
                UpdatedDate = GETDATE()
            WHERE 
                ComplaintID = @ComplaintID
                AND MarketingReview IS NOT NULL
                AND MarketingReview != ''
                AND PlantHeadReview IS NOT NULL
                AND PlantHeadReview != ''
                AND RootCauseAnalysis IS NOT NULL
                AND RootCauseAnalysis != ''
                AND CorrectivePreventiveAction IS NOT NULL
                AND CorrectivePreventiveAction != '';
                
            IF @@ROWCOUNT > 0
            BEGIN
                INSERT INTO SolutionGenerationLog (ComplaintID, TriggerTime, Action)
                VALUES (@ComplaintID, GETDATE(), 'Trigger fired: marked for regeneration');
            END
        END
        """
        execute_sql_safe(db, create_proc_sql, "sp_MarkComplaintReadyForSolution procedure")
        
        # Create trigger
        create_trigger_sql = """
        CREATE TRIGGER TR_Complaints_TriggerSolutionGeneration
        ON Complaints_Master
        AFTER UPDATE
        AS
        BEGIN
            SET NOCOUNT ON;
            
            DECLARE @ComplaintID NVARCHAR(50);
            SELECT TOP 1 @ComplaintID = ComplaintID FROM inserted;
            
            IF @ComplaintID IS NOT NULL
            BEGIN
                EXEC sp_MarkComplaintReadyForSolution @ComplaintID;
            END
        END
        """
        execute_sql_safe(db, create_trigger_sql, "TR_Complaints_TriggerSolutionGeneration trigger")
        
        # Create view
        create_view_sql = """
        IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_ComplaintsReadyForSolution')
            DROP VIEW vw_ComplaintsReadyForSolution
        
        CREATE VIEW vw_ComplaintsReadyForSolution AS
        SELECT TOP 10000
            ComplaintID,
            CategoryType,
            ComplaintDescription,
            MarketingReview,
            PlantHeadReview,
            RootCauseAnalysis,
            CorrectivePreventiveAction,
            Solution,
            Status,
            CASE 
                WHEN MarketingReview IS NOT NULL AND LTRIM(RTRIM(MarketingReview)) != '' THEN 'YES'
                ELSE 'NO'
            END AS HasMarketingReview,
            CASE 
                WHEN PlantHeadReview IS NOT NULL AND LTRIM(RTRIM(PlantHeadReview)) != '' THEN 'YES'
                ELSE 'NO'
            END AS HasPlantReview,
            CASE 
                WHEN RootCauseAnalysis IS NOT NULL AND LTRIM(RTRIM(RootCauseAnalysis)) != '' THEN 'YES'
                ELSE 'NO'
            END AS HasRCA,
            CASE 
                WHEN CorrectivePreventiveAction IS NOT NULL AND LTRIM(RTRIM(CorrectivePreventiveAction)) != '' THEN 'YES'
                ELSE 'NO'
            END AS HasCPA,
            CASE 
                WHEN Solution IS NOT NULL AND LTRIM(RTRIM(Solution)) != '' THEN 'YES'
                ELSE 'NO'
            END AS HasSolution,
            CASE 
                WHEN MarketingReview IS NOT NULL AND LTRIM(RTRIM(MarketingReview)) != ''
                     AND PlantHeadReview IS NOT NULL AND LTRIM(RTRIM(PlantHeadReview)) != ''
                     AND RootCauseAnalysis IS NOT NULL AND LTRIM(RTRIM(RootCauseAnalysis)) != ''
                     AND CorrectivePreventiveAction IS NOT NULL AND LTRIM(RTRIM(CorrectivePreventiveAction)) != ''
                     AND (Solution IS NULL OR LTRIM(RTRIM(Solution)) = '')
                THEN 'READY_FOR_GENERATION'
                ELSE 'WAITING'
            END AS ReadyStatus,
            UpdatedDate
        FROM Complaints_Master
        ORDER BY UpdatedDate DESC
        """
        execute_sql_safe(db, create_view_sql, "vw_ComplaintsReadyForSolution view")
        
        logger.info("✓✓✓ Database setup complete - automatic solution generation ready!")
        
    except Exception as e:
        logger.error(f"Database setup error: {str(e)}")
    finally:
        db.close()


def setup_database_on_startup():
    """
    Called on application startup to set up database components
    """
    try:
        setup_database_components()
    except Exception as e:
        logger.error(f"Failed to setup database: {str(e)}")
