# Setup Instant Solution Generation Trigger

## How to Enable Instant Solution Generation When Editing in MSSQL

### Problem
When you edit complaint data directly in MSSQL (via SSMS "Edit Top 200 Rows"), the solution wasn't regenerating automatically.

### Solution
Use the database trigger to automatically mark complaints for regeneration the instant you save edits.

---

## Setup Instructions (One-Time Only)

### Step 1: Open MSSQL Server Management Studio (SSMS)

### Step 2: Open the trigger script
- File → Open → File
- Select: `backend/database/instant_solution_trigger.sql`

### Step 3: Run the script
- Click "Execute" or press F5
- You'll see messages confirming:
  - ✓ Stored procedure created
  - ✓ Trigger created
  - ✓ Logging table created
  - ✓ View created

---

## How It Works After Setup

### Workflow
```
You edit complaint in SSMS
    ↓
You click "Update" (Ctrl+Enter)
    ↓
Trigger fires INSTANTLY
    ↓
Checks: Are all 4 fields filled?
    ├─ MarketingReview: YES/NO
    ├─ PlantHeadReview: YES/NO
    ├─ RootCauseAnalysis: YES/NO
    └─ CorrectivePreventiveAction: YES/NO
    ↓
If ALL 4 are filled:
    ├─ Solution field is cleared (set to NULL)
    ├─ Status is marked as "Ready_For_Solution_Generation"
    └─ Event is logged in SolutionGenerationLog
    ↓
Backend scheduler (every 30 seconds):
    ├─ Detects the marked complaint
    ├─ Calls AI to generate solution
    └─ Updates Solution field
    ↓
Refresh SSMS (F5) to see the new solution within 30 seconds
```

---

## Example: Edit a Complaint

### Step 1: Right-click Complaints_Master table
```
Complaints_Master → Edit Top 200 Rows
```

### Step 2: Find a complaint and edit these columns:
- `MarketingReview`: Edit to "Approved" or any text
- `PlantHeadReview`: Edit to "Plant agrees" or any text
- `RootCauseAnalysis`: Already filled? Keep as is
- `CorrectivePreventiveAction`: Already filled? Keep as is

### Step 3: Click "Update" or press Ctrl+Enter
```
The trigger fires INSTANTLY
↓
Check the status: Look at the Solution column
```

### Step 4: Wait 30 seconds and refresh (F5)
```
Within 30 seconds, the backend scheduler will:
1. Detect the complaint
2. Call AI to generate solution
3. Update the Solution field

Refresh to see the new solution
```

---

## Verify the Trigger is Working

### Check if trigger fired:
```sql
SELECT TOP 10 * FROM SolutionGenerationLog 
ORDER BY CreatedAt DESC;
```

### Check complaints ready for generation:
```sql
SELECT * FROM vw_ComplaintsReadyForSolution 
WHERE ReadyStatus = 'READY_FOR_GENERATION';
```

### Check if solution was generated:
```sql
SELECT ComplaintID, Solution, UpdatedDate
FROM Complaints_Master
WHERE ComplaintID = 'YOUR_COMPLAINT_ID'
ORDER BY UpdatedDate DESC;
```

---

## Troubleshooting

### Q: I edited but no trigger message?
**A:** Check if you clicked "Update" (Ctrl+Enter). The trigger only fires on UPDATE.

### Q: Trigger fired but solution didn't update?
**A:** The backend scheduler needs to be running:
```bash
python -m uvicorn app.main:app --reload
```

### Q: Solution cleared but not regenerated after 30 seconds?
**A:** Check if all 4 fields are truly filled (not NULL, not empty string):
```sql
SELECT ComplaintID, 
       MarketingReview,
       PlantHeadReview,
       RootCauseAnalysis,
       CorrectivePreventiveAction,
       Solution,
       Status
FROM Complaints_Master
WHERE ComplaintID = 'YOUR_ID';
```

### Q: How to manually trigger regeneration?
**A:** Run the manual script:
```bash
python scripts/manual_trigger_solution.py
```

Or call the API:
```
POST /api/complaints/force-regenerate-solution/CMP-XXXX-XXXX
```

---

## Timeline Example

```
10:00:00 - You open SSMS "Edit Top 200 Rows"
10:00:05 - You find CMP-20260825-0001 and edit the columns
10:00:10 - You click "Update" (Ctrl+Enter)
           ↓ TRIGGER FIRES INSTANTLY
10:00:11 - Trigger checks conditions → All 4 fields filled ✓
10:00:12 - Solution cleared, marked as "Ready_For_Solution_Generation"
10:00:13 - Log entry created
10:00:30 - Backend scheduler cycle runs
10:00:31 - Scheduler detects the ready complaint
10:00:32 - AI generates solution
10:00:33 - Database updated with new solution
10:00:35 - You refresh (F5) in SSMS
10:00:36 - NEW SOLUTION IS VISIBLE ✓
```

---

## Advanced: Customize Trigger Conditions

If you want to change what triggers solution generation, edit the stored procedure:

```sql
-- Open this in SSMS
ALTER PROCEDURE sp_MarkComplaintReadyForSolution
    @ComplaintID NVARCHAR(50)
AS
BEGIN
    -- Modify the conditions here
    ...
END;
```

Then right-click the procedure → Modify → Save

---

## Database Objects Created

| Object | Type | Purpose |
|--------|------|---------|
| `sp_MarkComplaintReadyForSolution` | Stored Procedure | Checks conditions and marks for regeneration |
| `TR_Complaints_TriggerSolutionGeneration` | Trigger | Fires on UPDATE, calls the stored procedure |
| `SolutionGenerationLog` | Table | Logs all trigger events |
| `vw_ComplaintsReadyForSolution` | View | Shows complaints ready for solution generation |

---

## Need to Disable the Trigger?

```sql
-- Temporarily disable
ALTER TABLE Complaints_Master DISABLE TRIGGER TR_Complaints_TriggerSolutionGeneration;

-- Re-enable
ALTER TABLE Complaints_Master ENABLE TRIGGER TR_Complaints_TriggerSolutionGeneration;

-- Drop if needed
DROP TRIGGER TR_Complaints_TriggerSolutionGeneration;
```

---

## Questions?

The trigger ensures that whenever you edit a complaint's review fields in MSSQL, the system:
1. Detects the change INSTANTLY
2. Validates all required fields are filled
3. Marks it for regeneration
4. Backend scheduler regenerates the solution within 30 seconds

**Result: No manual steps needed - editing in MSSQL automatically triggers solution generation!**
