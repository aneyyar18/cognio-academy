#!/usr/bin/env python3
"""
General Database Migration Helper for TutorConnect

This script helps apply database schema changes and migrations for the TutorConnect application.
It can run specific migrations or check the current database schema.

Usage:
    python scripts/migrate_db.py --check                    # Check current schema
    python scripts/migrate_db.py --add-rating               # Add rating column to tutors
    python scripts/migrate_db.py --create-tables            # Create all tables from models
    python scripts/migrate_db.py --backup                   # Create database backup

Requirements:
    - Run this script from the project root directory
    - Ensure the application database is accessible
    - Always backup your database before running migrations
"""

import sys
import os
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Load environment variables from .env file
load_dotenv(os.path.join(project_root, '.env'))

try:
    from db import db
    from factory import create_app
    from models.tutor import Tutor
    from models.student import Student
    from models.admin import Admin
    from models.message import Message
    from models.availability import TutorAvailability
    import sqlalchemy as sa
    from sqlalchemy import text, inspect
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)


class DatabaseMigrator:
    """Handles database migrations for TutorConnect."""
    
    def __init__(self):
        self.app = create_app()
        
    def check_schema(self):
        """Check the current database schema."""
        print("🔍 Checking current database schema...")
        print("=" * 60)
        
        with self.app.app_context():
            try:
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                print(f"📊 Found {len(tables)} tables in database:")
                
                for table in sorted(tables):
                    print(f"\n📋 Table: {table}")
                    columns = inspector.get_columns(table)
                    
                    for col in columns:
                        col_type = str(col['type'])
                        nullable = "NULL" if col['nullable'] else "NOT NULL"
                        default = f" DEFAULT {col['default']}" if col['default'] else ""
                        print(f"   • {col['name']:<20} {col_type:<15} {nullable}{default}")
                
                print(f"\n✅ Schema check completed successfully!")
                return True
                
            except Exception as e:
                print(f"❌ Error checking schema: {e}")
                return False
    
    def check_column_exists(self, table_name, column_name):
        """Check if a column exists in a table."""
        try:
            query = text("""
                SELECT COUNT(*) as count 
                FROM information_schema.columns 
                WHERE table_schema = DATABASE() 
                AND table_name = :table_name 
                AND column_name = :column_name
            """)
            
            result = db.engine.execute(query, table_name=table_name, column_name=column_name)
            count = result.fetchone()[0]
            return count > 0
        except Exception as e:
            print(f"❌ Error checking column existence: {e}")
            return False
    
    def add_rating_column(self):
        """Add rating column to tutors table."""
        print("🔄 Adding rating column to tutors table...")
        print("=" * 60)
        
        with self.app.app_context():
            try:
                # Check if column already exists
                if self.check_column_exists('tutors', 'rating'):
                    print("✅ Rating column already exists in tutors table.")
                    return True
                
                # Confirm before proceeding
                response = input("🤔 Add rating column to tutors table? (y/N): ").lower().strip()
                if response not in ['y', 'yes']:
                    print("❌ Operation cancelled.")
                    return False
                
                # Add the column
                alter_sql = text("""
                    ALTER TABLE tutors 
                    ADD COLUMN rating FLOAT DEFAULT 0.0 
                    COMMENT 'Average tutor rating (0.0 to 5.0)'
                """)
                
                with db.engine.begin() as connection:
                    connection.execute(alter_sql)
                
                # Set demo ratings for existing tutors
                tutors = Tutor.query.all()
                if tutors:
                    import random
                    for tutor in tutors:
                        tutor.rating = round(random.uniform(3.0, 5.0), 1)
                    db.session.commit()
                    print(f"✅ Updated {len(tutors)} tutors with demo ratings.")
                
                print("✅ Rating column added successfully!")
                return True
                
            except Exception as e:
                print(f"❌ Error adding rating column: {e}")
                return False
    
    def create_all_tables(self):
        """Create all tables from models."""
        print("🔄 Creating all database tables from models...")
        print("=" * 60)
        
        with self.app.app_context():
            try:
                # Confirm before proceeding
                response = input("🤔 Create/update all tables? This may modify existing data. (y/N): ").lower().strip()
                if response not in ['y', 'yes']:
                    print("❌ Operation cancelled.")
                    return False
                
                db.create_all()
                print("✅ All tables created/updated successfully!")
                return True
                
            except Exception as e:
                print(f"❌ Error creating tables: {e}")
                return False
    
    def create_backup_sql(self):
        """Generate SQL backup commands."""
        print("💾 Database backup information...")
        print("=" * 60)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"tutorconnect_backup_{timestamp}.sql"
        
        print("🔧 To create a database backup, run one of these commands:")
        print()
        print("📋 MySQL/MariaDB:")
        print(f"   mysqldump -u username -p database_name > {backup_filename}")
        print()
        print("📋 PostgreSQL:")
        print(f"   pg_dump -U username -h localhost database_name > {backup_filename}")
        print()
        print("📋 SQLite:")
        print(f"   sqlite3 database.db .dump > {backup_filename}")
        print()
        print("💡 Replace 'username' and 'database_name' with your actual values.")
        print(f"💾 Backup will be saved as: {backup_filename}")
        
        return True


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="TutorConnect Database Migration Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/migrate_db.py --check           Check current schema
  python scripts/migrate_db.py --add-rating      Add rating column
  python scripts/migrate_db.py --create-tables   Create all tables
  python scripts/migrate_db.py --backup          Show backup commands
        """
    )
    
    parser.add_argument('--check', action='store_true',
                       help='Check current database schema')
    parser.add_argument('--add-rating', action='store_true',
                       help='Add rating column to tutors table')
    parser.add_argument('--create-tables', action='store_true',
                       help='Create all tables from models')
    parser.add_argument('--backup', action='store_true',
                       help='Show database backup commands')
    
    args = parser.parse_args()
    
    # Show help if no arguments provided
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("🚀 TutorConnect Database Migration Helper")
    print()
    
    migrator = DatabaseMigrator()
    
    try:
        success = True
        
        if args.check:
            success &= migrator.check_schema()
        
        if args.add_rating:
            success &= migrator.add_rating_column()
        
        if args.create_tables:
            success &= migrator.create_all_tables()
        
        if args.backup:
            success &= migrator.create_backup_sql()
        
        if success:
            print("\n🎉 All operations completed successfully!")
        else:
            print("\n❌ Some operations failed. Check error messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()