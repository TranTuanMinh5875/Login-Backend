import os
import shutil
import datetime
import sys

def backup_database():
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(current_dir, "auth.db")
    backup_dir = os.path.join(current_dir, "backups")
    
    os.makedirs(backup_dir, exist_ok=True)
    
    if not os.path.exists(db_path):
        print("Database file not found:", db_path)
        return False
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"auth_backup_{timestamp}.db")
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"Backup created: {backup_path}")
        
        backups = sorted([f for f in os.listdir(backup_dir) if f.startswith("auth_backup_")])
        if len(backups) > 7:
            for old_backup in backups[:-7]:
                os.remove(os.path.join(backup_dir, old_backup))
                print(f"Removed old backup: {old_backup}")
        
        return True
        
    except Exception as e:
        print(f"Backup failed: {e}")
        return False

if __name__ == "__main__":
    success = backup_database()
    sys.exit(0 if success else 1)