"""
Database migration script to add new columns to Complaints_Master table.
Uses the same connection settings from .env file.
"""
import pyodbc
from app.config import settings


def get_connection():
    """Create a connection to SQL Server using the same settings as the app."""
    conn_str = (
        f"DRIVER={{{settings.MSSQL_DRIVER}}};"
        f"SERVER={settings.MSSQL_SERVER};"
        f"DATABASE={settings.MSSQL_DATABASE};"
        f"UID={settings.MSSQL_USER};"
        f"PWD={settings.MSSQL_PASSWORD};"
        f"Encrypt={settings.MSSQL_ENCRYPT};"
        f"TrustServerCertificate={settings.MSSQL_TRUST_SERVER_CERT};"
    )
    return pyodbc.connect(conn_str)


def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute("""
        SELECT COUNT(*) 
        FROM sys.columns 
        WHERE object_id = OBJECT_ID(?) AND name = ?
    """, f'[dbo].[{table_name}]', column_name)
    return cursor.fetchone()[0] > 0


def add_complaint_columns():
    """Add new columns to Complaints_Master table if they don't exist."""
    print("="*60)
    print("Database Migration: Adding Columns to Complaints_Master")
    print("="*60)
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print(f"\n✓ Connected to database: {settings.MSSQL_DATABASE}")
        print(f"  Server: {settings.MSSQL_SERVER}\n")
        
        # Define columns to add
        columns_to_add = [
            ("PONumber", "NVARCHAR(100) NULL", "Store purchase order number"),
            ("DispatchDate", "DATE NULL", "Store dispatch date"),
            ("Summary", "NVARCHAR(2000) NULL", "AI-generated summary of complaint"),
            ("Solution", "NVARCHAR(2000) NULL", "AI-generated solution"),
            ("Progress", "NVARCHAR(2000) NULL", "Current progress description"),
            ("Status", "NVARCHAR(50) NULL DEFAULT 'Under Review'", "Complaint status"),
            ("UpdatedBy", "NVARCHAR(100) NULL", "Who last updated"),
            ("UpdatedDate", "DATETIME NULL", "When last updated"),
        ]
        
        added_count = 0
        skipped_count = 0
        
        for column_name, column_type, description in columns_to_add:
            if column_exists(cursor, "Complaints_Master", column_name):
                print(f"⊘ {column_name:15} - Already exists (skipped)")
                skipped_count += 1
            else:
                try:
                    sql = f"ALTER TABLE [dbo].[Complaints_Master] ADD [{column_name}] {column_type}"
                    cursor.execute(sql)
                    conn.commit()
                    print(f"✓ {column_name:15} - Added successfully ({description})")
                    added_count += 1
                except Exception as e:
                    print(f"✗ {column_name:15} - Error: {e}")
                    conn.rollback()
        
        # Verify all columns
        print(f"\n{'='*60}")
        print("Verification: Current Complaints_Master Schema")
        print(f"{'='*60}")
        
        cursor.execute("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'Complaints_Master'
            ORDER BY ORDINAL_POSITION
        """)
        
        print(f"\n{'Column Name':<30} {'Type':<20} {'Nullable':<10}")
        print("-"*60)
        for row in cursor.fetchall():
            col_name = row[0]
            data_type = row[1]
            max_length = f"({row[2]})" if row[2] else ""
            nullable = row[3]
            print(f"{col_name:<30} {data_type}{max_length:<20} {nullable:<10}")
        
        print(f"\n{'='*60}")
        print(f"Migration Summary:")
        print(f"  Columns added: {added_count}")
        print(f"  Already existed: {skipped_count}")
        print(f"  Total processed: {added_count + skipped_count}")
        print(f"{'='*60}")
        
        if added_count > 0:
            print("\n✓ Migration completed successfully!")
            print("\nNext step: Run 'python update_complaint_summaries.py' to generate")
            print("AI summaries for existing complaints.")
        else:
            print("\n✓ All columns already exist. No changes needed.")
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
    
    return True


if __name__ == "__main__":
    success = add_complaint_columns()
    exit(0 if success else 1)
