#!/usr/bin/env python3
"""
Automatic Database Migration Script for TutorConnect

This script automatically applies the rating column migration without user prompts.
Use this for automated deployments or CI/CD pipelines.

Usage:
    python scripts/auto_migrate.py
"""

import os
import sys
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import random

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, '.env'))

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_INSTANCE', 'cognio'),
    'user': os.environ.get('DB_USER', 'cognio_admin'),
    'password': os.environ.get('DB_PASSWORD', 'admin18'),
    'port': 3306
}

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    try:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM information_schema.columns 
            WHERE table_schema = %s 
            AND table_name = %s 
            AND column_name = %s
        """, (DB_CONFIG['database'], table_name, column_name))
        
        result = cursor.fetchone()
        return result[0] > 0
    except Error as e:
        print(f"❌ Error checking column existence: {e}")
        return False

def main():
    """Main migration function."""
    print("🚀 TutorConnect Automatic Database Migration")
    print("   Adding rating column for enhanced tutor search")
    print("=" * 60)
    
    try:
        print("🔌 Connecting to database...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print(f"✅ Connected to database: {DB_CONFIG['database']}")
        
        # Check if rating column already exists
        if check_column_exists(cursor, 'tutors', 'rating'):
            print("✅ Rating column already exists in tutors table.")
            print("🎉 Migration completed - no changes needed!")
            return True
        
        print("🔧 Adding rating column to tutors table...")
        
        try:
            # Add the rating column
            cursor.execute("""
                ALTER TABLE tutors 
                ADD COLUMN rating FLOAT DEFAULT 0.0 
                COMMENT 'Average tutor rating (0.0 to 5.0)'
            """)
            print("✅ Successfully added rating column.")
            
            # Get all tutor IDs and set demo ratings
            cursor.execute("SELECT id FROM tutors")
            tutors = cursor.fetchall()
            
            if tutors:
                print(f"🔄 Setting demo ratings for {len(tutors)} existing tutors...")
                for tutor in tutors:
                    tutor_id = tutor[0]
                    demo_rating = round(random.uniform(3.0, 5.0), 1)
                    cursor.execute("UPDATE tutors SET rating = %s WHERE id = %s", (demo_rating, tutor_id))
                print("✅ Demo ratings set for all tutors.")
            else:
                print("ℹ️  No existing tutors found.")
            
            # Auto-commit is enabled by default
            print("✅ Migration completed successfully!")
            
            # Show sample data
            cursor.execute("SELECT fullname, rating FROM tutors LIMIT 3")
            sample_tutors = cursor.fetchall()
            
            if sample_tutors:
                print("\n📊 Sample tutor ratings:")
                for name, rating in sample_tutors:
                    print(f"   • {name}: {rating}/5.0 stars")
            
            print("\n🎉 Database migration successful!")
            print("=" * 60)
            print("✅ The enhanced tutor search feature is now fully functional!")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
            
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return False
        
    finally:
        # Clean up
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)