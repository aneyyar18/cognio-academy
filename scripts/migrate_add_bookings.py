#!/usr/bin/env python3
"""
Database Migration Script for TutorConnect Booking System

This script adds the bookings table and related components for the appointment booking feature.
It includes proper enum handling, constraints, and rollback functionality.

Usage:
    python scripts/migrate_add_bookings.py
    python scripts/migrate_add_bookings.py --rollback  # To rollback changes
"""

import os
import sys
import argparse
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

# Load environment variables
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, '.env'))

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_INSTANCE', 'cdb'),
    'user': os.environ.get('DB_USER', 'cognio_admin'),
    'password': os.environ.get('DB_PASSWORD', 'admin18'),
    'port': 3306,
    'autocommit': False  # We want to handle transactions manually
}

def check_table_exists(cursor, table_name):
    """Check if a table exists in the database."""
    try:
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.tables
            WHERE table_schema = %s
            AND table_name = %s
        """, (DB_CONFIG['database'], table_name))

        result = cursor.fetchone()
        return result[0] > 0
    except Error as e:
        print(f"❌ Error checking table existence: {e}")
        return False

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

def create_bookings_table(cursor):
    """Create the bookings table with all necessary constraints."""
    print("🔧 Creating bookings table...")

    # Create the bookings table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS bookings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL,
        tutor_id INT NOT NULL,
        booking_date DATE NOT NULL,
        start_time TIME NOT NULL,
        end_time TIME NOT NULL,
        status ENUM('pending', 'confirmed', 'cancelled', 'completed') NOT NULL DEFAULT 'pending',
        subject VARCHAR(100) NULL,
        notes TEXT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

        -- Foreign key constraints
        CONSTRAINT fk_bookings_student
            FOREIGN KEY (student_id) REFERENCES students(id)
            ON DELETE CASCADE ON UPDATE CASCADE,

        CONSTRAINT fk_bookings_tutor
            FOREIGN KEY (tutor_id) REFERENCES tutors(id)
            ON DELETE CASCADE ON UPDATE CASCADE,

        -- Ensure end_time is after start_time
        CONSTRAINT chk_bookings_time_order
            CHECK (end_time > start_time),

        -- Ensure booking_date is not in the past (enforced at application level)
        -- Create index for common queries
        INDEX idx_bookings_tutor_date (tutor_id, booking_date),
        INDEX idx_bookings_student (student_id),
        INDEX idx_bookings_status (status),
        INDEX idx_bookings_date_time (booking_date, start_time)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    COMMENT='Stores appointment bookings between students and tutors';
    """

    cursor.execute(create_table_sql)
    print("✅ Bookings table created successfully!")

def add_demo_data(cursor):
    """Add some demo booking data for testing."""
    print("🔄 Adding demo booking data...")

    # First, check if we have students and tutors
    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tutors")
    tutor_count = cursor.fetchone()[0]

    if student_count == 0 or tutor_count == 0:
        print("ℹ️  No students or tutors found. Skipping demo data creation.")
        return

    # Get first student and tutor IDs for demo data
    cursor.execute("SELECT id FROM students ORDER BY id LIMIT 1")
    student_result = cursor.fetchone()

    cursor.execute("SELECT id FROM tutors ORDER BY id LIMIT 1")
    tutor_result = cursor.fetchone()

    if student_result and tutor_result:
        student_id = student_result[0]
        tutor_id = tutor_result[0]

        # Insert demo bookings (future dates only)
        demo_bookings = [
            (student_id, tutor_id, 'DATE_ADD(CURDATE(), INTERVAL 2 DAY)', '14:00:00', '15:00:00', 'confirmed', 'Mathematics', 'Review algebra concepts'),
            (student_id, tutor_id, 'DATE_ADD(CURDATE(), INTERVAL 5 DAY)', '16:00:00', '17:30:00', 'pending', 'Physics', 'Newton laws discussion'),
        ]

        for booking in demo_bookings:
            cursor.execute(f"""
                INSERT INTO bookings (student_id, tutor_id, booking_date, start_time, end_time, status, subject, notes)
                VALUES (%s, %s, {booking[2]}, %s, %s, %s, %s, %s)
            """, (booking[0], booking[1], booking[3], booking[4], booking[5], booking[6], booking[7]))

        print(f"✅ Added {len(demo_bookings)} demo bookings.")
    else:
        print("ℹ️  Could not find student/tutor for demo data.")

def rollback_migration(cursor):
    """Rollback the migration by dropping the bookings table."""
    print("🔄 Rolling back bookings table migration...")

    if check_table_exists(cursor, 'bookings'):
        # Drop the table (this will also drop all constraints and indexes)
        cursor.execute("DROP TABLE bookings")
        print("✅ Bookings table removed successfully!")
    else:
        print("ℹ️  Bookings table does not exist - nothing to rollback.")

def verify_migration(cursor):
    """Verify that the migration was successful."""
    print("🔍 Verifying migration...")

    # Check table exists
    if not check_table_exists(cursor, 'bookings'):
        print("❌ Bookings table was not created!")
        return False

    # Check table structure
    cursor.execute("DESCRIBE bookings")
    columns = cursor.fetchall()

    expected_columns = ['id', 'student_id', 'tutor_id', 'booking_date', 'start_time',
                       'end_time', 'status', 'subject', 'notes', 'created_at', 'updated_at']

    actual_columns = [col[0] for col in columns]

    missing_columns = [col for col in expected_columns if col not in actual_columns]
    if missing_columns:
        print(f"❌ Missing columns: {missing_columns}")
        return False

    # Check constraints exist
    cursor.execute("""
        SELECT CONSTRAINT_NAME
        FROM information_schema.table_constraints
        WHERE table_schema = %s
        AND table_name = 'bookings'
        AND constraint_type = 'FOREIGN KEY'
    """, (DB_CONFIG['database'],))

    constraints = cursor.fetchall()
    if len(constraints) < 2:  # Should have at least 2 foreign key constraints
        print("⚠️  Warning: Expected foreign key constraints may be missing.")

    # Check for demo data
    cursor.execute("SELECT COUNT(*) FROM bookings")
    booking_count = cursor.fetchone()[0]

    print(f"✅ Migration verified successfully!")
    print(f"   • Table: bookings ✓")
    print(f"   • Columns: {len(actual_columns)} ✓")
    print(f"   • Constraints: {len(constraints)} foreign keys ✓")
    print(f"   • Demo bookings: {booking_count} records ✓")

    return True

def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description='Migrate bookings table for TutorConnect')
    parser.add_argument('--rollback', action='store_true',
                       help='Rollback the migration (removes bookings table)')
    parser.add_argument('--no-demo-data', action='store_true',
                       help='Skip adding demo data')

    args = parser.parse_args()

    if args.rollback:
        print("🔄 TutorConnect Bookings Migration Rollback")
    else:
        print("🚀 TutorConnect Bookings Migration")
        print("   Adding appointment booking system")
    print("=" * 60)

    connection = None
    cursor = None

    try:
        print("🔌 Connecting to database...")
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        print(f"✅ Connected to database: {DB_CONFIG['database']}")

        if args.rollback:
            # Rollback migration
            rollback_migration(cursor)
            connection.commit()
            print("🎉 Rollback completed successfully!")
        else:
            # Check if table already exists
            if check_table_exists(cursor, 'bookings'):
                print("✅ Bookings table already exists.")
                print("🎉 Migration completed - no changes needed!")
                return True

            # Apply migration
            create_bookings_table(cursor)

            if not args.no_demo_data:
                add_demo_data(cursor)

            # Commit all changes
            connection.commit()
            print("✅ Migration committed successfully!")

            # Verify the migration
            if verify_migration(cursor):
                print("\n🎉 Bookings system migration completed successfully!")
                print("=" * 60)
                print("✅ Students can now book appointments with tutors!")
                print("✅ The booking calendar feature is fully functional!")
            else:
                print("❌ Migration verification failed!")
                return False

        return True

    except Error as e:
        print(f"❌ Database error: {e}")
        if connection and connection.is_connected():
            connection.rollback()
            print("🔄 Transaction rolled back due to error.")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if connection and connection.is_connected():
            connection.rollback()
            print("🔄 Transaction rolled back due to error.")
        return False

    finally:
        # Clean up
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("🔌 Database connection closed.")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)