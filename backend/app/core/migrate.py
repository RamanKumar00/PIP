import sqlite3
import os

def run_migration():
    db_path = "placementor.db"
    if not os.path.exists(db_path):
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "placementor.db")
    
    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    columns = ["recruiter_report", "semantic_analysis", "interview_preparation", "analytics_data"]
    for col in columns:
        try:
            print(f"Adding column '{col}' to table 'resume_analyses'...")
            cursor.execute(f"ALTER TABLE resume_analyses ADD COLUMN {col} TEXT DEFAULT '{{}}';")
            conn.commit()
            print(f"Column '{col}' added successfully.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print(f"Column '{col}' already exists, skipping.")
            else:
                print(f"Error adding column '{col}': {e}")
                
    conn.close()
    print("Database migration completed.")

if __name__ == "__main__":
    run_migration()
