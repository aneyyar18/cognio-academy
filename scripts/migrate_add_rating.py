1#!/usr/bin/env python3
"""
Database Migration Script: Add rating column to tutors table

This script adds the 'rating' column to the tutors table to support
the enhanced tutor search functionality.

Usage:
    python scripts/migrate_add_rating.py

Requirements:
    - Run this script from the project root directory
    - Ensure the application database is accessible
    - Backup your database before running migrations
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from db import db
    from factory import create_app
    from models.tutor import Tutor
    import sqlalchemy as sa
    from sqlalchemy import text
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)


def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table."""
    try:
        # Query information_schema to check if column exists
        query = text("""
            SELECT COUNT(*) as count 
            FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND table_name = :table_name 
            AND column_name = :column_name
        """)
        
        result = engine.execute(query, table_name=table_name, column_name=column_name)
        count = result.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Error checking column existence: {e}")
        return False


def add_rating_column():
    """Add the rating column to the tutors table."""
    print("🔄 Starting database migration: Add rating column to tutors table")
    print("=" * 60)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Get database engine
            engine = db.engine
            
            # Check if the rating column already exists
            print("📋 Checking if rating column already exists...")
            if check_column_exists(engine, 'tutors', 'rating'):
                print("✅ Rating column already exists in tutors table.")
                print("🎉 Migration completed successfully - no changes needed!")
                return True
            
            # Create backup timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            print(f"⚠️  IMPORTANT: Please backup your database before proceeding!")
            print(f"📅 Migration timestamp: {timestamp}")
            
            # Confirm before proceeding
            response = input("🤔 Do you want to continue with the migration? (y/N): ").lower().strip()
            if response not in ['y', 'yes']:
                print("❌ Migration cancelled by user.")
                return False
            
            print("\n🔧 Adding rating column to tutors table...")
            
            # Add the rating column with default value
            alter_sql = text("""
                ALTER TABLE tutors 
                ADD COLUMN rating FLOAT DEFAULT 0.0 
                COMMENT 'Average tutor rating (0.0 to 5.0)'
            """)
            
            # Execute the migration
            with engine.begin() as connection:
                connection.execute(alter_sql)
                print("✅ Successfully added rating column to tutors table.")
            
            # Update existing tutors with a default rating
            print("🔄 Setting default rating values for existing tutors...")
            
            # Get all existing tutors and set random ratings for demo purposes
            tutors = Tutor.query.all()
            if tutors:
                import random
                for tutor in tutors:
                    # Set a random rating between 3.0 and 5.0 for existing tutors
                    # In a real scenario, you might calculate this from actual reviews
                    demo_rating = round(random.uniform(3.0, 5.0), 1)
                    tutor.rating = demo_rating
                
                db.session.commit()
                print(f"✅ Updated {len(tutors)} existing tutors with demo ratings.")
            else:
                print("ℹ️  No existing tutors found to update.")
            
            # Verify the migration
            print("\n🔍 Verifying migration...")
            if check_column_exists(engine, 'tutors', 'rating'):
                print("✅ Verification successful: rating column exists and is accessible.")
                
                # Show sample data
                sample_tutors = Tutor.query.limit(3).all()
                if sample_tutors:
                    print("\n📊 Sample tutor ratings:")
                    for tutor in sample_tutors:
                        print(f"   • {tutor.fullname}: {tutor.rating}/5.0 stars")
                
                print(f"\n🎉 Migration completed successfully!")
                print("=" * 60)
                print("✅ The tutors table now includes the rating column.")
                print("✅ All existing tutors have been assigned demo ratings.")
                print("✅ The enhanced tutor search feature is now fully functional!")
                return True
            else:
                print("❌ Verification failed: rating column was not created properly.")
                return False
                
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            print("🔄 Rolling back any changes...")
            try:
                db.session.rollback()
            except:
                pass
            return False


def main():
    """Main migration function."""
    print("🚀 TutorConnect Database Migration Tool")
    print("   Adding rating column for enhanced tutor search")
    print()
    
    try:
        success = add_rating_column()
        
        if success:
            print("\n📋 Next Steps:")
            print("   1. Test the /tutorsearch route to verify functionality")
            print("   2. Check that existing tutors display with ratings")
            print("   3. Verify that rating-based filtering works correctly")
            print("\n💡 Tip: You can now search tutors by minimum rating!")
            sys.exit(0)
        else:
            print("\n❌ Migration failed. Please check the error messages above.")
            print("💡 Tip: Make sure your database is accessible and you have proper permissions.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()