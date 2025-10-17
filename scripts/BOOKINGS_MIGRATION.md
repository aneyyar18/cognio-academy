# TutorConnect Bookings System Migration

This document describes the database migration for the appointment booking system in TutorConnect.

## 📋 Overview

The bookings migration adds a complete appointment scheduling system that allows students to book sessions with tutors. This includes:

- **Bookings table** with proper constraints and indexes
- **Booking status management** (pending, confirmed, cancelled, completed)
- **Time conflict prevention** (no double booking)
- **Business rule enforcement** (24-hour advance booking, 14-day limit)
- **Demo data** for testing the system

## 🚀 Migration Scripts

### Option 1: Raw SQL Migration (Recommended)
```bash
# Apply migration
python scripts/migrate_add_bookings.py

# Rollback migration
python scripts/migrate_add_bookings.py --rollback

# Apply without demo data
python scripts/migrate_add_bookings.py --no-demo-data
```

### Option 2: SQLAlchemy Migration
```bash
# Apply migration using SQLAlchemy
python scripts/sqlalchemy_migrate_bookings.py

# Rollback migration
python scripts/sqlalchemy_migrate_bookings.py --rollback

# Apply without demo data
python scripts/sqlalchemy_migrate_bookings.py --no-demo-data
```

## 📊 Database Schema

### Bookings Table Structure

```sql
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    tutor_id INT NOT NULL,
    booking_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending',
    subject VARCHAR(100) NULL,
    notes TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Foreign Keys
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (tutor_id) REFERENCES tutors(id) ON DELETE CASCADE,

    -- Constraints
    CHECK (end_time > start_time),

    -- Indexes
    INDEX idx_bookings_tutor_date (tutor_id, booking_date),
    INDEX idx_bookings_student (student_id),
    INDEX idx_bookings_status (status),
    INDEX idx_bookings_date_time (booking_date, start_time)
);
```

### Booking Status Flow

```
pending → confirmed → completed
    ↓
cancelled (can happen at any stage before completed)
```

## 🔒 Business Rules Enforced

### Database Level
- ✅ **Foreign key constraints** - Ensures referential integrity
- ✅ **Time validation** - End time must be after start time
- ✅ **Cascade deletes** - Bookings are deleted if student/tutor is deleted

### Application Level
- ✅ **24-hour advance booking** - Cannot book within 24 hours
- ✅ **14-day booking window** - Cannot book more than 2 weeks ahead
- ✅ **Double booking prevention** - Checks for time conflicts
- ✅ **Timezone handling** - All times stored in GMT, displayed in tutor's timezone

## 🎯 Features Enabled

### For Students
- **View tutor availability** in calendar format (7-day view)
- **Book appointments** with time slot selection
- **Add session notes** and select subjects
- **View booking status** and history

### For Tutors
- **Receive booking notifications**
- **Confirm or manage appointments**
- **View scheduled sessions**

### For System
- **Prevent scheduling conflicts**
- **Maintain booking history**
- **Support timezone conversions**
- **Enable future rating/review system**

## 🔧 Prerequisites

### Database Requirements
- MySQL 5.7+ or MariaDB 10.2+
- Existing `students` and `tutors` tables
- Proper database permissions for DDL operations

### Environment Setup
```env
DB_HOST=localhost
DB_INSTANCE=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

### Python Dependencies
```bash
pip install mysql-connector-python python-dotenv sqlalchemy flask-sqlalchemy
```

## ✅ Migration Verification

After running the migration, verify success:

### 1. Check Table Exists
```sql
SHOW TABLES LIKE 'bookings';
```

### 2. Verify Structure
```sql
DESCRIBE bookings;
```

### 3. Check Constraints
```sql
SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE
FROM information_schema.table_constraints
WHERE table_name = 'bookings'
AND table_schema = 'your_database_name';
```

### 4. Test Demo Data
```sql
SELECT * FROM bookings;
```

### 5. Application Test
- Navigate to a tutor profile page
- Click "Book Session" button
- Verify calendar displays correctly
- Test booking flow

## 🔄 Rollback Process

If you need to rollback the migration:

```bash
# Using raw SQL script
python scripts/migrate_add_bookings.py --rollback

# Using SQLAlchemy script
python scripts/sqlalchemy_migrate_bookings.py --rollback
```

**Warning:** Rollback will permanently delete all booking data!

## 🐛 Troubleshooting

### Common Issues

**1. Foreign Key Constraint Error**
```
ERROR 1452: Cannot add or update a child row
```
**Solution:** Ensure `students` and `tutors` tables exist and have data.

**2. Column Already Exists**
```
ERROR 1060: Duplicate column name
```
**Solution:** Table already migrated. Check with `DESCRIBE bookings;`

**3. Permission Denied**
```
ERROR 1142: CREATE command denied
```
**Solution:** Ensure database user has CREATE, ALTER, and INDEX privileges.

**4. Connection Error**
```
ERROR 2003: Can't connect to MySQL server
```
**Solution:** Check database server status and `.env` configuration.

### Verification Commands

```bash
# Check migration status
python -c "
from scripts.migrate_add_bookings import check_table_exists
import mysql.connector
# ... connection code ...
print('Bookings table exists:', check_table_exists(cursor, 'bookings'))
"

# Test booking creation
python -c "
from models.booking import Booking
from datetime import date, time, timedelta
# Test creating a booking
"
```

## 📈 Performance Considerations

### Indexes Created
- `idx_bookings_tutor_date` - Optimizes tutor schedule queries
- `idx_bookings_student` - Speeds up student booking history
- `idx_bookings_status` - Efficient status-based filtering
- `idx_bookings_date_time` - Calendar view optimization

### Query Patterns Optimized
- Find available time slots for a tutor
- Get student's booking history
- Check for scheduling conflicts
- Filter bookings by status

## 🔮 Future Enhancements

The booking system is designed to support:
- **Payment integration** - Add payment_status, amount columns
- **Recurring bookings** - Add recurrence pattern fields
- **Video call integration** - Add meeting_url, platform columns
- **Rating system** - Link to future rating/review tables
- **Notification system** - Support email/SMS reminders

## 📝 Migration History

| Date | Version | Description | Status |
|------|---------|-------------|---------|
| 2024-10-05 | 1.0 | Initial bookings system | ✅ Ready |

## 🤝 Support

For questions or issues with the migration:

1. **Check the logs** - Migration scripts provide detailed output
2. **Verify prerequisites** - Ensure all requirements are met
3. **Test rollback** - If needed, use rollback functionality
4. **Review application logs** - Check Flask/SQLAlchemy logs

---

**Next Steps After Migration:**
1. Test the booking flow end-to-end
2. Configure email notifications (optional)
3. Set up monitoring for booking conflicts
4. Plan integration with payment systems (future)
5. Implement tutor booking management interface