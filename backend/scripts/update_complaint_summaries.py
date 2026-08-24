"""
Script to generate AI summaries and solutions for existing complaints
that have NULL in their Solution or Summary fields.
"""
import sys
from datetime import datetime
from sqlalchemy.orm import Session

# Add the parent directory to path so we can import from app
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import ComplaintMaster
from app.ollama_client import generate_reply


def generate_complaint_summary_and_solution(category: str, description: str, po_number: str = None, dispatch_date: str = None):
    """Generate AI summary and solution for a complaint using Ollama."""
    
    # Build the verified data context - this is what Ollama will analyze
    verified_data = f"""Complaint Information Retrieved from Database:
- Category: {category or 'General'}
- Customer Description: {description}
- PO Number: {po_number or 'Not provided'}
- Dispatch Date: {dispatch_date or 'Not provided'}

Based on this information, please provide a brief summary of the issue and a recommended solution."""
    
    # Build the customer message/prompt - this is the instruction
    customer_message = """Analyze this complaint and provide:
1. SUMMARY: A brief 2-3 sentence summary of what the customer's issue is
2. SOLUTION: A recommended solution or next steps in 2-3 sentences

Format your response EXACTLY as shown:
SUMMARY: [write summary here]
SOLUTION: [write solution here]"""
    
    # Call Ollama with the proper parameters
    response = generate_reply(customer_message, verified_data)
    
    # Default fallback values
    summary = f"Customer complaint regarding {category or 'product quality'}: {description[:150]}{'...' if len(description) > 150 else ''}"
    solution = "Our technical team is reviewing this issue and will provide an update within 24-48 hours."
    
    # Parse the response if we got one
    if response:
        try:
            if "SUMMARY:" in response and "SOLUTION:" in response:
                parts = response.split("SOLUTION:")
                summary = parts[0].replace("SUMMARY:", "").strip()
                solution = parts[1].strip()
            else:
                # If format doesn't match, just use the whole response as summary
                summary = response[:500] if len(response) > 500 else response
        except Exception as e:
            print(f"Warning: Failed to parse Ollama response: {e}")
            # Keep fallback values
    else:
        print("Warning: Ollama did not return a response, using fallback values")
    
    return summary, solution


def update_existing_complaints():
    """Update all existing complaints that have NULL Summary or Solution."""
    db: Session = SessionLocal()
    
    try:
        # Find all complaints with NULL Summary or NULL Solution
        complaints = db.query(ComplaintMaster).filter(
            (ComplaintMaster.Summary == None) | (ComplaintMaster.Solution == None)
        ).all()
        
        if not complaints:
            print("No complaints found with NULL Summary or Solution.")
            return
        
        print(f"Found {len(complaints)} complaints to update...")
        
        updated_count = 0
        failed_count = 0
        
        for complaint in complaints:
            try:
                print(f"\nProcessing Complaint ID: {complaint.ComplaintID}")
                
                # Generate summary and solution
                summary, solution = generate_complaint_summary_and_solution(
                    category=complaint.CategoryType,
                    description=complaint.ComplaintDescription or "No description provided",
                    po_number=complaint.PONumber,
                    dispatch_date=complaint.DispatchDate.strftime('%Y-%m-%d') if complaint.DispatchDate else None
                )
                
                # Update the complaint
                if not complaint.Summary:
                    complaint.Summary = summary
                    print(f"  ✓ Added Summary")
                
                if not complaint.Solution:
                    complaint.Solution = solution
                    print(f"  ✓ Added Solution")
                
                if not complaint.Progress:
                    complaint.Progress = "Complaint registered and under initial review"
                    print(f"  ✓ Added Progress")
                
                if not complaint.Status:
                    complaint.Status = "Under Review"
                    print(f"  ✓ Set Status")
                
                complaint.UpdatedDate = datetime.now()
                complaint.UpdatedBy = "AI_System"
                
                db.commit()
                updated_count += 1
                print(f"  ✓ Successfully updated Complaint {complaint.ComplaintID}")
                
            except Exception as e:
                print(f"  ✗ Error processing complaint {complaint.ComplaintID}: {e}")
                db.rollback()
                failed_count += 1
                continue
        
        print(f"\n{'='*60}")
        print(f"Update Summary:")
        print(f"  Total complaints processed: {len(complaints)}")
        print(f"  Successfully updated: {updated_count}")
        print(f"  Failed: {failed_count}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"Fatal error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("Updating Existing Complaints with AI Summaries and Solutions")
    print("="*60)
    update_existing_complaints()
