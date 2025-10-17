#!/usr/bin/env python3
"""
SQLAlchemy-based Migration Script for TutorConnect Booking System

This script uses SQLAlchemy to create the bookings table and related components.
It's an alternative to the raw SQL migration script.

Usage:
    python scripts/sqlalchemy_migrate_bookings.py
    python scripts/sqlalchemy_migrate_bookings.py --rollback  # To rollback changes
"""

import os
import sys
import argparse
from datetime import datetime, date, time, timedelta

# Add project root to path so we can import modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Load environment variables
load_dotenv(os.path.join(project_root, '.env'))

def get_database_url():
    """Get database URL from environment variables."""
    DB_USER = os.environ.get('DB_USER', 'cognio_admin')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'admin18')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_INSTANCE = os.environ.get('DB_INSTANCE', 'cdb')

    return f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_INSTANCE}'

def check_table_exists(engine, table_name):
    """Check if a table exists using SQLAlchemy inspector."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def create_tables_with_sqlalchemy(engine):
    """Create tables using SQLAlchemy models."""
    print("🔧 Creating tables using SQLAlchemy...")

    try:
        # Import all models so SQLAlchemy knows about them
        from db import db
        from models.booking import Booking, BookingStatus
        from models.student import Student
        from models.tutor import Tutor

        # Create a Flask app context for SQLAlchemy to work
        from flask import Flask
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(app)

        with app.app_context():
            # Create only the bookings table
            Booking.__table__.create(engine, checkfirst=True)
            print("✅ Bookings table created successfully using SQLAlchemy!")

        return True

    except Exception as e:
        print(f"❌ Error creating tables with SQLAlchemy: {e}")
        return False

def add_demo_data_sqlalchemy(engine):
    """Add demo booking data using SQLAlchemy."""
    print("🔄 Adding demo booking data using SQLAlchemy...")

    try:
        from flask import Flask
        from db import db
        from models.booking import Booking, BookingStatus
        from models.student import Student
        from models.tutor import Tutor

        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(app)

        with app.app_context():
            # Check if we have students and tutors
            student = Student.query.first()
            tutor = Tutor.query.first()

            if not student or not tutor:
                print("ℹ️  No students or tutors found. Skipping demo data creation.")
                return True

            # Check if we already have bookings
            existing_bookings = Booking.query.count()
            if existing_bookings > 0:
                print(f"ℹ️  Found {existing_bookings} existing bookings. Skipping demo data.")
                return True

            # Create demo bookings (future dates only)
            tomorrow = date.today() + timedelta(days=2)
            next_week = date.today() + timedelta(days=5)

            demo_bookings = [
                Booking(
                    student_id=student.id,
                    tutor_id=tutor.id,
                    booking_date=tomorrow,
                    start_time=time(14, 0),
                    end_time=time(15, 0),
                    status=BookingStatus.CONFIRMED,
                    subject='Mathematics',
                    notes='Review algebra concepts'
                ),
                Booking(
                    student_id=student.id,
                    tutor_id=tutor.id,
                    booking_date=next_week,
                    start_time=time(16, 0),
                    end_time=time(17, 30),
                    status=BookingStatus.PENDING,
                    subject='Physics',
                    notes='Newton laws discussion'
                )
            ]

            # Add bookings to session
            for booking in demo_bookings:
                db.session.add(booking)

            db.session.commit()
            print(f"✅ Added {len(demo_bookings)} demo bookings using SQLAlchemy.")

        return True

    except Exception as e:
        print(f"❌ Error adding demo data: {e}")
        return False

def rollback_migration_sqlalchemy(engine):
    """Rollback migration by dropping the bookings table."""
    print("🔄 Rolling back bookings table migration using SQLAlchemy...")

    try:
        if check_table_exists(engine, 'bookings'):
            # Use raw SQL to drop table since SQLAlchemy doesn't have a direct drop method
            with engine.connect() as connection:
                connection.execute("DROP TABLE bookings")
                connection.commit()
            print("✅ Bookings table removed successfully!")
        else:
            print("ℹ️  Bookings table does not exist - nothing to rollback.")

        return True

    except Exception as e:
        print(f"❌ Error during rollback: {e}")
        return False

def verify_migration_sqlalchemy(engine):
    """Verify migration using SQLAlchemy."""
    print("🔍 Verifying migration using SQLAlchemy...")

    try:
        if not check_table_exists(engine, 'bookings'):
            print("❌ Bookings table was not created!")
            return False

        # Use SQLAlchemy to check the table structure
        from flask import Flask
        from db import db
        from models.booking import Booking

        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(app)

        with app.app_context():
            # Check if we can query the table
            booking_count = Booking.query.count()

            print("✅ Migration verified successfully using SQLAlchemy!")
            print(f"   • Table: bookings ✓")
            print(f"   • Model: Booking class accessible ✓")
            print(f"   • Records: {booking_count} bookings ✓")

        return True

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description='SQLAlchemy-based migration for bookings table')
    parser.add_argument('--rollback', action='store_true',
                       help='Rollback the migration (removes bookings table)')
    parser.add_argument('--no-demo-data', action='store_true',
                       help='Skip adding demo data')

    args = parser.parse_args()

    if args.rollback:
        print("🔄 TutorConnect Bookings SQLAlchemy Migration Rollback")
    else:
        print("🚀 TutorConnect Bookings SQLAlchemy Migration")
        print("   Adding appointment booking system using SQLAlchemy")
    print("=" * 60)

    try:
        print("🔌 Connecting to database...")
        database_url = get_database_url()
        engine = create_engine(database_url)

        # Test connection
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            result.fetchone()

        print("✅ Connected to database successfully!")

        if args.rollback:
            # Rollback migration
            if rollback_migration_sqlalchemy(engine):
                print("🎉 SQLAlchemy rollback completed successfully!")
            else:
                return False
        else:
            # Check if table already exists
            if check_table_exists(engine, 'bookings'):
                print("✅ Bookings table already exists.")
                print("🎉 Migration completed - no changes needed!")
                return True

            # Apply migration
            if not create_tables_with_sqlalchemy(engine):
                return False

            if not args.no_demo_data:
                if not add_demo_data_sqlalchemy(engine):
                    return False

            # Verify migration
            if verify_migration_sqlalchemy(engine):
                print("\n🎉 SQLAlchemy bookings migration completed successfully!")
                print("=" * 60)
                print("✅ Students can now book appointments with tutors!")
                print("✅ The booking calendar feature is fully functional!")
            else:
                print("❌ Migration verification failed!")
                return False

        return True

    except SQLAlchemyError as e:
        print(f"❌ SQLAlchemy error: {e}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    finally:
        # Clean up
        if 'engine' in locals():
            engine.dispose()
            print("🔌 Database connection closed.")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)