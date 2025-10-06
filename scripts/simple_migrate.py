#!/usr/bin/env python3
"""
Simple Database Migration Script for TutorConnect

This script applies database changes needed for the enhanced tutor search feature.
It directly connects to the database without going through Flask.

Usage:
    python scripts/simple_migrate.py

Requirements:
    - MySQL/MariaDB database running
    - Environment variables set in .env file
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

def add_rating_column(cursor):
    """Add the rating column to the tutors table."""
    try:
        # Add the rating column
        cursor.execute("""
            ALTER TABLE tutors 
            ADD COLUMN rating FLOAT DEFAULT 0.0 
            COMMENT 'Average tutor rating (0.0 to 5.0)'
        """)
        print("✅ Successfully added rating column to tutors table.")
        return True
    except Error as e:
        print(f"❌ Error adding rating column: {e}")
        return False

def update_tutor_ratings(cursor):
    """Set demo ratings for existing tutors."""
    try:
        # Get all tutor IDs
        cursor.execute("SELECT id FROM tutors")
        tutors = cursor.fetchall()
        
        if not tutors:
            print("ℹ️  No existing tutors found to update.")
            return True
        
        # Update each tutor with a random rating
        for tutor in tutors:
            tutor_id = tutor[0]
            demo_rating = round(random.uniform(3.0, 5.0), 1)
            cursor.execute("UPDATE tutors SET rating = %s WHERE id = %s", (demo_rating, tutor_id))
        
        print(f"✅ Updated {len(tutors)} tutors with demo ratings.")
        return True
    except Error as e:
        print(f"❌ Error updating tutor ratings: {e}")
        return False

def show_schema_info(cursor):
    """Show current schema information for tutors table."""
    try:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default, column_comment
            FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = 'tutors'
            ORDER BY ordinal_position
        """, (DB_CONFIG['database'],))
        
        columns = cursor.fetchall()
        
        print("\n📋 Tutors table schema:")
        print("=" * 80)
        print(f"{'Column Name':<25} {'Type':<15} {'Nullable':<10} {'Default':<15} {'Comment'}")
        print("-" * 80)
        
        for col in columns:
            column_name, data_type, is_nullable, default, comment = col
            nullable = "YES" if is_nullable == "YES" else "NO"
            default_val = str(default) if default else "NULL"
            comment_val = comment if comment else ""
            print(f"{column_name:<25} {data_type:<15} {nullable:<10} {default_val:<15} {comment_val}")
        
        return True
    except Error as e:
        print(f"❌ Error showing schema: {e}")
        return False

def main():
    """Main migration function."""
    print("🚀 TutorConnect Simple Database Migration")
    print("   Adding rating column for enhanced tutor search")
    print("=" * 60)
    
    # Test database connection
    try:
        print("🔌 Connecting to database...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print(f"✅ Connected to database: {DB_CONFIG['database']}")
        
        # Check if rating column already exists
        print("\n📋 Checking current schema...")
        if check_column_exists(cursor, 'tutors', 'rating'):
            print("✅ Rating column already exists in tutors table.")
            show_schema_info(cursor)
            print("\n🎉 Migration completed - no changes needed!")
            return
        
        print("⚠️  Rating column does not exist. Need to add it.")
        
        # Confirm before proceeding
        response = input("\n🤔 Add rating column to tutors table? (y/N): ").lower().strip()
        if response not in ['y', 'yes']:
            print("❌ Migration cancelled by user.")
            return
        
        print("\n🔧 Applying migration...")
        
        # Start transaction
        connection.start_transaction()
        
        try:
            # Add the rating column
            if not add_rating_column(cursor):
                raise Exception("Failed to add rating column")
            
            # Update existing tutors with demo ratings
            if not update_tutor_ratings(cursor):
                raise Exception("Failed to update tutor ratings")
            
            # Commit the transaction
            connection.commit()
            print("✅ Migration completed successfully!")
            
            # Show updated schema
            print("\n📋 Updated schema:")
            show_schema_info(cursor)
            
            # Show some sample data
            cursor.execute("SELECT fullname, rating FROM tutors LIMIT 3")
            sample_tutors = cursor.fetchall()
            
            if sample_tutors:
                print("\n📊 Sample tutor ratings:")
                for name, rating in sample_tutors:
                    print(f"   • {name}: {rating}/5.0 stars")
            
            print("\n🎉 Migration completed successfully!")
            print("=" * 60)
            print("✅ The tutors table now includes the rating column.")
            print("✅ All existing tutors have been assigned demo ratings.")
            print("✅ The enhanced tutor search feature is now fully functional!")
            
        except Exception as e:
            # Rollback on error
            connection.rollback()
            print(f"❌ Migration failed: {e}")
            print("🔄 Changes have been rolled back.")
            
    except Error as e:
        print(f"❌ Database connection error: {e}")
        print("\n💡 Please check:")
        print("   - Database server is running")
        print("   - Connection credentials in .env are correct")
        print("   - Database name exists")
        
    finally:
        # Clean up
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("\n🔌 Database connection closed.")

if __name__ == "__main__":
    main()